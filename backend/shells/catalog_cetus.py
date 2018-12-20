#!/bin/python3
# -*- coding: utf-8 -*-

import sys
import getopt
import pymysql
import json


def help_and_exit():
    print('''Usage:
    --help 显示帮助信息
    -h 数据库IP
    -P 端口
    -u 用户
    -p 密码
    -d 数据库 
    -t Cetus类型
    -s 服务端口
    -a 管理端口
    -r 路径
    ''')
    sys.exit()


def create_tables():
    settings_sql = '''
CREATE TABLE IF NOT EXISTS settings (
   option_key varchar(64) NOT NULL,
   option_value varchar(1024),
   option_default varchar(1024),
   option_type varchar(10) NOT NULL DEFAULT 'Dynamic',
   description varchar(255),
   PRIMARY KEY (option_key)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
'''
    services_sql = '''
CREATE TABLE IF NOT EXISTS services (
   id varchar(64) NOT NULL,
   data varchar(64) NOT NULL,
   start_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (id)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
'''
    objects_sql = '''
CREATE TABLE IF NOT EXISTS objects (
   object_name varchar(64) NOT NULL,
   object_value json NOT NULL,
   mtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (object_name)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
'''

    monitor_sql = '''
CREATE TABLE `monitor` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `node_id` int(11) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT NULL,
  `startup_time` datetime DEFAULT NULL,
  `modules` varchar(20) DEFAULT NULL,
  `idle_conns` int(11) DEFAULT NULL,
  `used_conns` int(11) DEFAULT NULL,
  `client_conns` int(11) DEFAULT NULL,
  `query_count` int(11) DEFAULT NULL,
  `qps1` float(10,2) DEFAULT NULL,
  `qps5` float(10,2) DEFAULT NULL,
  `qps15` float(10,2) DEFAULT NULL,
  `tps1` float(10,2) DEFAULT NULL,
  `tps5` float(10,2) DEFAULT NULL,
  `tps15` float(10,2) DEFAULT NULL,
  `backends` varchar(10000) DEFAULT NULL,
  `cpu` float(10,2) DEFAULT NULL,
  `mem` int(11) DEFAULT NULL,
  `Com_select` int(11) DEFAULT NULL,
  `Com_insert` int(11) DEFAULT NULL,
  `Com_update` int(11) DEFAULT NULL,
  `Com_delete` int(11) DEFAULT NULL,
  `Com_select_shard` int(11) DEFAULT NULL,
  `Com_insert_shard` int(11) DEFAULT NULL,
  `Com_update_shard` int(11) DEFAULT NULL,
  `Com_delete_shard` int(11) DEFAULT NULL,
  `Com_select_global` int(11) DEFAULT NULL,
  `Com_select_bad_key` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_time_id` (`create_time`, `node_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
'''

    return locals()


def init_objects(cetus_type):
    variables_json = {"variables": [{"name": "profiling", "type": "string", "silent_values": ["*"], "allowed_values": ["*"]},
                                    {"name": "PROFILING", "type": "string", "silent_values": ["*"], "allowed_values": ["*"]},
                                    {"name": "net_write_timeout", "type": "int", "silent_values": ["*"], "allowed_values": ["*"]},
                                    {"name": "character_set_results", "type": "int", "silent_values": ["*"], "allowed_values": ["*"]},
                                    {"name": "SQL_SELECT_LIMIT", "type": "int", "silent_values": ["*"], "allowed_values": ["*"]}]}
    users_json = {"users": []}
    object_list = [('variables', json.dumps(variables_json)),
                   ('users', json.dumps(users_json))]
    if cetus_type == 'shard':
        shard_json = {"vdb": [], "table": [], "single_tables": []}
        object_list.append(('sharding', json.dumps(shard_json)))
    return object_list


def init_settings(cetus_type, cetus_dir, service_port, admin_port):
    variables = [('verbose-shutdown', 'false', 'false', 'Static', '程序退出时，记录下退出代码'),
                 ('daemon', 'false', 'false', 'Static', '通过守护进程启动'),
                 ('user', None, None, 'Static', '启动进程的用户，只有以root身份运行时才能使用'),
                 ('basedir', None, None, 'Static', '基础路径，其它配置可以以此为基准配置相对路径 (必须是绝对路径)'),
                 ('conf-dir', None, None, 'Static', 'JSON配置文件路径，JSON文件包括包括：账号配置文件、变量处理配置文件、分库版本的分片规则配置文件'),
                 ('pid-file', '%s/cetus_%s.pid' % (cetus_dir, service_port), '%s/cetus_%s.pid' % (cetus_dir, service_port), 'Static', 'PID文件路径'),
                 ('plugin-dir', 'lib/cetus/plugins', 'lib/cetus/plugins', 'Static', '库文件路径'),
                 ('log-level', 'critical', 'critical', 'Static', '可选值: debug | info | message | warning | error | critical(default)'),
                 ('log-file', '%s/logs/cetus.log' % cetus_dir, '%s/logs/cetus.log' % cetus_dir, 'Static', '日志文件路径'),
                 ('log-xa-file', '%s/logs/xa.log' % cetus_dir, '%s/logs/xa.log' % cetus_dir, 'Static', 'xa日志路径（分库中有效）'),
                 ('log-backtrace-on-crash', 'true', 'true', 'Static', '程序崩溃时启动gdb调试器'),
                 ('max-open-files', '0', '0', 'Static', '最大打开的文件数目(ulimit -n)'),
                 ('default-charset', 'utf8', 'utf8', 'Dynamic', '默认数据库字符标码方式'),
                 ('default-username', 'cetus_test', 'cetus_test', 'Dynamic', '默认用户名，在Proxy启动时自动创建连接使用的用户名'),
                 ('default-db', 'test', 'test', 'Dynamic', '默认数据库，当连接未指定db时，使用的默认数据库名称'),
                 ('ifname', 'eth0', 'eth0', 'Dynamic', ''),
                 ('default-pool-size', '10', '10', 'Dynamic', '每个worker进程启动时允许创建的连接数 当前连接数不足此值时，会自动创建连接 最小只能设置为10，如果设置小于10，则实际该值为10'),
                 ('max-pool-size', '20', '20', 'Dynamic', '每个worker进程允许创建的最大连接数，包括连接池里的空闲连接和正在使用的连接'),
                 ('worker-processes', '1', '1', 'Dynamic', '启动worker进程的数量，启动的数量最好小于等于cpu数目'),
                 ('max-resp-size', '10485760', '10485760', 'Dynamic', '每个后端返回结果集的最大数量'),
                 ('max-alive-time', '600', '600', 'Dynamic', '后端连接最大存活时间'),
                 ('merged-output-size', '8192', '8192', 'Dynamic', 'tcp流式结果集合并输出阈值，超过此大小，则输出'),
                 ('max-header-size', '65536', '65536', 'Dynamic', '设置响应中header最大大小，供tcp stream使用，如果响应头部特别大，需要设置更大的大小'),
                 # ('worker-id', '', '', 'Dynamic'),
                 ('disable-threads', 'false', 'false', 'Static', '禁用辅助线程，包括: 后端存活检测、只读库延迟检测、MGR节点状态和角色检测等'),
                 ('ssl', 'false', 'false', 'Static', '前端支持SSL连接'),
                 ('enable-back-compress', 'false', 'false', 'Static', '启用后端传给Cetus的结果集压缩，一般不启用'),
                 ('enable-client-compress', 'false', 'false', 'Static', ''),
                 ('check-slave-delay', 'true', 'true', 'Static', '是否检查从库延迟'),
                 ('slave-delay-down', '10', '10', 'Dynamic', '从库延迟超过该秒，状态将被设置为DOWN'),
                 ('slave-delay-recover', '1', '1', 'Dynamic', '从库延迟少于该秒数，状态将恢复为UP'),
                 ('default-query-cache-timeout', '100', '100', 'Dynamic', '设置query cache的默认超时时间，单位为ms'),
                 ('default-client-idle-timeout', '28800', '28800', 'Dynamic', ''),
                 ('long-query-time', '1000', '1000', 'Dynamic', '慢查询记录阈值(毫秒)'),
                 ('enable-client-found-rows', 'false', 'false', 'Static', '允许客户端使用FOUND_ROWS标志'),
                 ('reduce-connections', 'false', 'false', 'Static', '自动减少空闲连接'),
                 ('enable-query-cache', 'false', 'false', 'Static', '开启Proxy请求缓存'),
                 ('enable-tcp-stream', 'false', 'false', 'Static', '采用tcp stream来输出响应，规避内存炸裂等问题'),
                 ('log-xa-in-detail', 'false', 'false', 'Static', '记录xa日志详情（分库中有效）'),
                 ('disable-dns-cache', 'false', 'false', 'Static', '禁用解析连接到后端的域名'),
                 ('master-preferred', 'false', 'false', 'Static', 'Proxy在读写分离时可以指定访问的库'),
                 ('max-allowed-packet', '33554432', '33554432', 'Dynamic', '最大允许报文大小'),
                 ('remote-conf-url', None, None, 'Static', '远端配置中心信息'),
                 ('group-replication-mode', '0', '0', 'Dynamic', '当后端MySQL集群是单主模式的MGR时，该参数设置为 1'),
                 ('sql-log-buffersize', '1048576', '1048576', 'Static', '全量日志的缓存大小'),
                 ('sql-log-switch', 'OFF', 'OFF', 'Dynamic', '全量日志功能是否可用'),
                 ('sql-log-prefix', 'cetus', 'cetus', 'Static', '全量日志的文件名前缀'),
                 ('sql-log-path', '%s/logs/cetus-pid.clg' % cetus_dir, '%s/logs/cetus-pid.clg' % cetus_dir, 'Static', '全量日志输出的路径'),
                 ('sql-log-maxsize', '1024', '1024', 'Static', '每个全量日志的最大容量'),
                 ('sql-log-mode', 'backend', 'backend', 'Dynamic', '输出的全量日志的类型,可配置的值包括：connect、client、front、backend、all'),
                 ('sql-log-idletime', '10000', '10000', 'Dynamic', '全量日志的线程在没有日志可以写入文件的情况下，等待下写入的时间'),
                 ('sql-log-maxnum', '3', '3', 'Dynamic', '保留的历史文件的个数，默认为3，0表示不限制文件个数'),
                 ('check-dns', 'false', 'false', 'Dynamic', ''),
                 ('temporary-file', None, None, 'Static', ''),

                 ('admin-address', '0.0.0.0:%s' % admin_port, '0.0.0.0:%s' % admin_port, 'Static', '管理模块的IP和端口'),
                 ('admin-username', 'admin', 'admin', 'Static', '管理模块的用户名'),
                 ('admin-password', 'admin', 'admin', 'Static', '管理模块的密码明文'),
                 ('admin-allow-ip', None, None, 'Dynamic', '参数未设置时，不作限制；仅能限制IP不区分用户'),
                 ('admin-deny-ip', None, None, 'Dynamic', ''),

                 ('proxy-address', '0.0.0.0:%s' % service_port, '0.0.0.0:%s' % service_port, 'Static', 'Proxy监听的IP和端口'),
                 ('proxy-read-only-backend-addresses', '0.0.0.0:3307', '0.0.0.0:3307', 'Static', '只读后端(从库)的IP和端口，若是分库模式，需要同时指定group'),
                 ('proxy-backend-addresses', '0.0.0.0:3306', '0.0.0.0:3306', 'Static', '读写后端(主库)的IP和端口，若是分库模式，需要同时指定group'),
                 ('proxy-connect-timeout', '2', '2', 'Dynamic', '连接Proxy的超时时间'),
                 ('proxy-read-timeout', '600', '600', 'Dynamic', '读Proxy的超时时间'),
                 ('proxy-write-timeout', '-600', '-600', 'Dynamic', '写Proxy的超时时间'),
                 ('proxy-allow-ip', None, None, 'Dynamic', 'Proxy允许访问的"用户@IP"'),
                 ('proxy-deny-ip', None, None, 'Dynamic', ''),
                 ]

    if cetus_type == 'rw':
        variables.extend([('plugins', 'admin,proxy', 'admin,proxy', 'Static', '加载模块名称')])
    if cetus_type == 'shard':
        variables.extend([('plugins', 'admin,shard', 'admin,shard', 'Static', '加载模块名称'),
                          ('allow-nested-subquery', 'false', 'false', 'Static', ''),
                          ('proxy-xa-commit-or-rollback-read-timeout', '-1', '-1', 'Dynamic', '')])

    return variables


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'h:P:u:p:d:t:s:a:r:',
                                   ['help', 'host=', 'port=', 'user=', 'passwd=', 'database=', 'type=', 'service=', 'admin=', 'route='])

    except getopt.GetoptError as err:
        print(err)
        help_and_exit()

    for opt, arg in opts:
        if opt in ('--help',):
            help_and_exit()
        elif opt in ('-h', '--host'):
            host = arg
        elif opt in ('-P', '--port'):
            port = arg
        elif opt in ('-u', '--user'):
            user = arg
        elif opt in ('-p', '--passwd'):
            passwd = arg
        elif opt in ('-d', '--database'):
            database = arg
        elif opt in ('-t', '--type'):
            cetus_type = arg
        elif opt in ('-s', '--service'):
            service_port = arg
        elif opt in ('-a', '--admin'):
            admin_port = arg
        elif opt in ('-r', '--route'):
            cetus_dir = arg

    try:
        db = pymysql.connect(host=host, user=user, passwd=passwd, port=int(port))
        cursor = db.cursor()
    except Exception as e:
        print(e)
        raise Exception('数据库连接失败')

    try:
        cursor.execute('CREATE DATABASE IF NOT EXISTS %s' % database)
        cursor.execute('USE %s' % database)

        for item in create_tables().values():
            cursor.execute(item)

        objects = init_objects(cetus_type)
        cursor.executemany('REPLACE INTO objects (object_name,object_value) VALUES (%s, %s)', objects)

        settings = init_settings(cetus_type, cetus_dir, service_port, admin_port)
        cursor.executemany('REPLACE INTO settings (option_key,option_value,option_default,option_type,description) VALUES (%s,%s,%s,%s,%s)', settings)

        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
        raise Exception('初始化数据失败')
    finally:
        db.close()

    return 0, 'success'


if __name__ == '__main__':
    ret, msg = main()
    sys.exit(ret)
