from rest_framework.pagination import PageNumberPagination
from djcelery.models import CrontabSchedule, PeriodicTask

import salt.client
import subprocess
import pymysql
import logging
import json
import ast
import datetime

from backend.settings import DATABASES, MONITOR_CRON
from .models import TbCetusGroupInfo, TbCetusNodeInfo

logger = logging.getLogger('django')


class StandardResultsSetPagination(PageNumberPagination):
    """
    项目分页策略
    """
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


def create_task(name, task_name, args):
    """
    创建任务
    """
    cron_info = CrontabSchedule.objects.filter(**MONITOR_CRON).first()
    if not cron_info:
        cron_info = CrontabSchedule.objects.create(**MONITOR_CRON)

    task, created = PeriodicTask.objects.get_or_create(name=name,
                                                       task=task_name,
                                                       queue='cetus_monitor')
    task.crontab = cron_info
    task.enabled = True
    task.args = args
    task.save()


def convert_command_results(header, msg, flag):
    """
    转换管理命令结果集
    """
    if flag:
        return '%s:\n' \
               'Errno: %s\n' \
               '%s\n\n' % (header, msg[0], msg[1])
    else:
        res = '%s:\n' % header
        affect_rows, headers, columns = msg[0], msg[1], msg[2]

        _c, _r = list(), list()
        for _u in columns:
            for _x in _u:
                if _x:
                    _r.append(str(_x))
                else:
                    _r.append('NULL')
            _c.append(_r)
            _r = list()
        columns = _c

        if msg[1]:
            max_length, line = list(), '+'
            for item in headers:
                max_length.append(len(item))
            for column in columns:
                for index, item in enumerate(column):
                    if len(item) > max_length[index]:
                        max_length[index] = len(item)
            for item in max_length:
                line += '+'.rjust(item + 3, '-')
            res += '%s\n' % line
            for index, item in enumerate(headers):
                res += '| ' + item.ljust(max_length[index] + 1, ' ')
            res += '|\n%s\n' % line
            for column in columns:
                for index, item in enumerate(column):
                    res += '| ' + item.ljust(max_length[index] + 1, ' ')
                res += '|\n'
            res += '%s\n' % line
            res += '%s rows in set\n\n' % affect_rows
        else:
            res += 'Query OK, %s row affected\n\n' % affect_rows
        return res


class CetusConn(object):
    """
    创建连接
    """

    def __init__(self, host='127.0.0.1', port='3306', user='root', password='', db='test', cursor='', **kwargs):
        self.conn = pymysql.connect(host=host, user=user, db=db, passwd=password, port=port, autocommit=None)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor) if cursor == 'dict' else self.conn.cursor()

    def execute(self, sql, *args, **kwargs):
        """
        执行查询SQL
        """
        if isinstance(self.cursor, pymysql.cursors.DictCursor):
            self.cursor.execute(sql, kwargs or args)
            return self.cursor.fetchall()
        else:
            effect_rows = self.cursor.execute(sql, kwargs or args)
            if self.cursor.description:
                column_names = [d[0] for d in self.cursor.description]
            else:
                column_names = []
            return effect_rows, column_names, self.cursor.fetchall()

    def get_remote_db_args(self, args):
        """
        获取参数列表
        """
        r = self.execute('select option_key, option_value from settings where option_key in %s', args)
        return {x['option_key']: x['option_value'] for x in r}

    def get_cetus_fund_params(self, info):
        """
        获取节点信息
        """
        if info == 'base':
            return self.execute('SELECT option_key as `name`, option_value as `value`,'
                                'option_type as `type`, description as `descrip` FROM settings')
        elif info in ['users', 'variables', 'sharding']:
            res = self.execute('SELECT object_name as `name`, object_value as `value` '
                               'FROM objects where object_name=%s', info)
            return json.loads(res[0].get('value'))

    def change_cetus_fund_params(self, info, params):
        """
        修改参数
        """
        if info == 'base':
            for item in params:
                self.execute('UPDATE settings SET option_value=%s WHERE option_key=%s', item['value'], item['name'])
        elif info == 'users':
            _tmp = list()
            for item in params.get('users'):
                _tmp.append({'user': item['user'], 'client_pwd': item['client_pwd'], 'server_pwd': item['server_pwd']})
            params = json.dumps({'users': _tmp})
            self.execute('UPDATE objects SET object_value=%s WHERE object_name=%s', params, info)
        elif info == 'variables':
            _tmp = list()
            for item in params.get('variables'):
                silent_values = json.loads(item['silent_values'])
                allowed_values = json.loads(item['allowed_values'])
                _tmp.append({'name': item['name'], 'type': item['type'], 'silent_values': silent_values, 'allowed_values': allowed_values})
            params = json.dumps({'variables': _tmp})
            self.execute('UPDATE objects SET object_value=%s WHERE object_name=%s', params, info)
        elif info == 'sharding':
            if params.get('vdb'):
                _b = []
                for ele in params.get('vdb'):
                    partitions = json.loads(ele['partitions'])
                    _b.append({'id': ele['id'], 'num': ele['num'], 'type': ele['type'], 'method': ele['method'], 'partitions': partitions})
                params['vdb'] = _b
            if params.get('table'):
                _b = []
                for ele in params.get('table'):
                    _b.append({'db': ele['db'], 'vdb': ele['vdb'], 'pkey': ele['pkey'], 'table': ele['table']})
                params['table'] = _b
            if params.get('single_tables'):
                _b = []
                for ele in params.get('single_tables'):
                    _b.append({'db': ele['db'], 'group': ele['group'], 'table': ele['table']})
                params['single_tables'] = _b
            params = json.dumps(params)
            self.execute('UPDATE objects SET object_value=%s WHERE object_name=%s', params, info)

    def get_monitor_data(self, node_id, range_hours, cetus_type):
        """
        获取监控信息
        """
        now = datetime.datetime.now()
        past = now - datetime.timedelta(hours=range_hours)

        sql_res = self.execute('select * from monitor where node_id=%s and create_time '
                               'BETWEEN %s and %s order by create_time desc limit 20', node_id, past, now)
        if not sql_res:
            return {}
        sql_res.reverse()

        _c = dict()
        if sql_res:
            for _i in sql_res[0].keys():
                _c.update({_i: []})
            for _i in sql_res:
                for _k, _v in _i.items():
                    _c[_k].append(_v)

        backends = ast.literal_eval(_c['backends'][-1])
        backends = [{'address': item[0], 'state': item[1], 'type': item[2], 'slave_delay': item[3],
                     'idle_conns': item[4], 'used_conns': item[5], 'total_conns': item[6]} for item in backends]

        res = {'tps': {'legend': ['TPS (1min)', 'TPS (5min)', 'TPS (15min)'],
                       'title': 'TPS',
                       'series': [{'name': 'TPS (1min)', 'type': 'line', 'data': _c['tps1']},
                                  {'name': 'TPS (5min)', 'type': 'line', 'data': _c['tps5']},
                                  {'name': 'TPS (15min)', 'type': 'line', 'data': _c['tps15']}]},
               'qps': {'legend': ['QPS (1min)', 'QPS (5min)', 'QPS (15min)'],
                       'title': 'QPS',
                       'series': [{'name': 'QPS (1min)', 'type': 'line', 'data': _c['qps1']},
                                  {'name': 'QPS (5min)', 'type': 'line', 'data': _c['qps5']},
                                  {'name': 'QPS (15min)', 'type': 'line', 'data': _c['qps15']}]},
               'backends': backends,
               'conns': {'legend': ['Idle connections', 'Used connections', 'Client connections'],
                         'title': 'Connections',
                         'series': [{'name': 'Idle connections', 'type': 'line', 'data': _c['idle_conns']},
                                    {'name': 'Used connections', 'type': 'line', 'data': _c['used_conns']},
                                    {'name': 'Client connections', 'type': 'line', 'data': _c['client_conns']}]},
               'load': {'legend': ['CPU load'],
                        'title': 'Load',
                        'series': [{'name': 'CPU load', 'type': 'line', 'data': _c['cpu']}]},
               'mem': {'legend': ['Used Memory (KB)'],
                       'title': 'Used Memory',
                       'series': [{'name': 'Memory Used (KB)', 'type': 'line', 'data': _c['mem']}]},
               'sentence': {'legend': ['Select QPS', 'Insert QPS', 'Update QPS', 'Delete QPS', 'Select global QPS', 'Select bad QPS'],
                            'title': 'Sentence QPS',
                            'series': [{'name': 'Select QPS', 'type': 'line', 'data': _c['Com_select']},
                                       {'name': 'Insert QPS', 'type': 'line', 'data': _c['Com_insert']},
                                       {'name': 'Update QPS', 'type': 'line', 'data': _c['Com_update']},
                                       {'name': 'Delete QPS', 'type': 'line', 'data': _c['Com_delete']},
                                       {'name': 'Select global QPS', 'type': 'line', 'data': _c['Com_select_global']},
                                       {'name': 'Select bad QPS', 'type': 'line', 'data': _c['Com_select_bad_key']}]},
               'xAxis': _c['create_time'],
               }
        if cetus_type == 'shard':
            res['sentence']['legend'].extend(['Select shard QPS', 'Insert shard QPS', 'Update shard QPS', 'Delete shard QPS'])
            res['sentence']['series'].extend([{'name': 'Select shard QPS', 'type': 'line', 'data': _c['Com_select_shard']},
                                              {'name': 'Insert shard QPS', 'type': 'line', 'data': _c['Com_insert_shard']},
                                              {'name': 'Update shard QPS', 'type': 'line', 'data': _c['Com_update_shard']},
                                              {'name': 'Delete shard QPS', 'type': 'line', 'data': _c['Com_delete_shard']}])

        return res

    def __del__(self):
        if 'self.conn' in locals():
            self.conn.close()


class SaltClient(object):
    """
    启动Salt Client
    """

    @staticmethod
    def _exec_script(salt_id, url, args):
        """
        传输并执行脚本
        """
        logger.info((salt_id, url, args))

        res = salt.client.LocalClient().cmd(salt_id,
                                            "cmd.script",
                                            [url, args, "shell='/bin/bash'"],
                                            show_timeout=True)
        if res.get(salt_id):
            if not res.get(salt_id).get('retcode'):
                return 0, res.get(salt_id).get('stdout')
            else:
                return 1, res.get(salt_id).get('stdout') + \
                       res.get(salt_id).get('stderr')
        else:
            return 1, 'salt connect error'

    @classmethod
    def download_cetus_node(cls, **kwargs):
        """
        下载Cetus源码
        """
        code, res = cls._exec_script(kwargs.get('salt_id'),
                                     'salt://download_cetus.py',
                                     '-t {cetus_type} '
                                     '-v {version} '
                                     '-u {cetus_url} '
                                     '-r {cetus_route}'.format(**kwargs))
        logger.info((code, res))

        if code == 0:
            return res
        else:
            raise Exception('下载失败')

    @classmethod
    def install_cetus_node(cls, **kwargs):
        """
        安装Cetus节点
        """
        code, res = cls._exec_script(kwargs.get('salt_id'),
                                     'salt://install_cetus.py',
                                     '-t {cetus_type} '
                                     '-s {service_port} '
                                     '-a {admin_port} '
                                     '-r {cetus_route} '
                                     '-p {dir}'.format(**kwargs))

        create_task('node_%s_monitor' % kwargs.get('id'), 'cetus_monitor', [kwargs.get('id')])

        if code == 0:
            logger.info(res)
            return res
        else:
            logger.error(res)
            raise Exception('安装失败')

    @classmethod
    def check_cetus_node(cls, node_id):
        """
        检查Cetus节点
        """
        node_info = TbCetusNodeInfo.objects.get(pk=node_id)
        cetus_info = TbCetusGroupInfo.objects.get(pk=node_info.group_id)
        admin_info = CetusConn(db=cetus_info.config_db,
                               cursor='dict',
                               **DATABASES['catalog']) \
            .get_remote_db_args(['admin-username', 'admin-password'])

        kwargs = {
            'admin_user': admin_info['admin-username'],
            'admin_passwd': admin_info['admin-password'],
            'admin_port': node_info.admin_port,
        }

        code, res = cls._exec_script(node_info.salt_id,
                                     'salt://check_cetus.py',
                                     '-u {admin_user} '
                                     '-p {admin_passwd} '
                                     '-P {admin_port}'.format(**kwargs))
        logger.info((code, res))

        if code == 0:
            TbCetusNodeInfo.objects.filter(pk=node_id).update(status=0)
        elif code == 1:
            TbCetusNodeInfo.objects.filter(pk=node_id).update(status=-1)
        elif code == 2:
            TbCetusNodeInfo.objects.filter(pk=node_id).update(status=-1)
            raise Exception('连接失败')

        return code, res

    @classmethod
    def operate_cetus_node(cls, node_id, operate_type):
        """
        操控Cetus节点
        """
        node_info = TbCetusNodeInfo.objects.get(pk=node_id)
        cetus_info = TbCetusGroupInfo.objects.get(pk=node_info.group_id)
        kwargs = {
            'operate_type': operate_type,
            'config_db': cetus_info.config_db,
            'cetus_route': node_info.dir,
            'cetus_owner': 'cetus_%s' % node_info.service_port
        }

        kwargs.update(**DATABASES['catalog'])
        if operate_type == 'start':
            TbCetusNodeInfo.objects.filter(pk=node_id).update(status=3)
            msg, errmsg = '启动成功', '启动失败'
        elif operate_type == 'shutdown':
            TbCetusNodeInfo.objects.filter(pk=node_id).update(status=-2)
            msg, errmsg = '关闭成功', '关闭失败'
        elif operate_type == 'restart':
            TbCetusNodeInfo.objects.filter(pk=node_id).update(status=-2)
            msg, errmsg = '重启成功', '重启失败'
        elif operate_type == 'abort':
            TbCetusNodeInfo.objects.filter(pk=node_id).update(status=-2)
            msg, errmsg = '强制关闭成功', '强制关闭失败'

        code, res = cls._exec_script(node_info.salt_id,
                                     'salt://operate_cetus.py',
                                     '-t {operate_type} '
                                     '-h {host} '
                                     '-P {port} '
                                     '-u {user} '
                                     '-p {password} '
                                     '-d {config_db} '
                                     '-r {cetus_route} '
                                     '-o {cetus_owner}'.format(**kwargs))

        logger.info((code, res))

        if code == 0:
            if operate_type in ['start', 'restart']:
                code, res = cls.check_cetus_node(node_id)
                if code == 0:
                    return 0, msg
                else:
                    return 1, errmsg
            elif operate_type in ['shutdown', 'abort']:
                TbCetusNodeInfo.objects.filter(pk=node_id).update(status=-1)
                return 0, msg
        else:
            cls.check_cetus_node(node_id)
            return 1, errmsg

    @classmethod
    def record_monitor_data(cls, node_id, exec_time):
        """
        收集监控信息
        """
        node_info = TbCetusNodeInfo.objects.get(pk=node_id)
        cetus_info = TbCetusGroupInfo.objects.get(pk=node_info.group_id)
        admin_info = CetusConn(db=cetus_info.config_db,
                               cursor='dict',
                               **DATABASES['catalog']) \
            .get_remote_db_args(['admin-username', 'admin-password'])

        code, res = cls._exec_script(node_info.salt_id,
                                     'salt://cetus_monitor.py',
                                     '-u %s -p %s -P %s' % (admin_info['admin-username'],
                                                            admin_info['admin-password'],
                                                            node_info.admin_port))
        logger.info((code, res))

        if code == 0:
            res = ast.literal_eval(res)
            res.append(('create_time', exec_time))
            res.append(('node_id', str(node_id)))
            conn = CetusConn(db=cetus_info.config_db, cursor='dict', **DATABASES['catalog'])
            conn.execute('insert into monitor (%s) values (%s)' %
                         (",".join(['`%s`' % x[0] for x in res]), ",".join(['"%s"' % x[1] for x in res])))
        else:
            logger.error(res)
            logger.error(node_id)
            raise Exception('数据收集失败')


def config_remote_configuration_db(**kwargs):
    """
    配置远程配置库
    """
    logger.info(kwargs)

    p = subprocess.Popen('python3 ./shells/catalog_cetus.py %s' %
                         '-h {host} '
                         '-P {port} '
                         '-u {user} '
                         '-p {password} '
                         '-d {database} '
                         '-t {cetus_type} '
                         '-s {service_port} '
                         '-a {admin_port} '
                         '-r {cetus_dir}'.format(**kwargs),
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    o = p.communicate()

    logger.info((p.returncode, o))
    if p.returncode == 0:
        return o[0]
    else:
        logger.error(o[0] + o[1])
        raise Exception('配置失败')
