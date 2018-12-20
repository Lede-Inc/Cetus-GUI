#!/bin/python3
# -*- coding: utf-8 -*-

import sys
import getopt
import pymysql
import subprocess


def help_and_exit():
    print('''Usage:
    -h 显示帮助信息
    -P 端口
    -u 用户
    -p 密码
    -d 数据库
    ''')
    sys.exit()


def get_cpu_mem(pid):
    try:
        p = subprocess.Popen("ps aux|grep %s|grep -v 'grep'|awk '{print $3}'" % pid,
                             shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        cpu = p.stdout.read().strip()
        p = subprocess.Popen("ps aux|grep %s|grep -v 'grep'|awk '{print $6}'" % pid,
                             shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        mem = p.stdout.read().strip()

        return bytes.decode(cpu), bytes.decode(mem)
    except Exception as e:
        print(e)
        return 0, 0


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'hP:u:p:',
                                   ['help', 'port=', 'user=', 'passwd='])

    except getopt.GetoptError as err:
        print(err)
        help_and_exit()

    for opt, arg in opts:
        if opt in ('-h', '--help',):
            help_and_exit()
        elif opt in ('-P', '--port'):
            port = arg
        elif opt in ('-u', '--user'):
            user = arg
        elif opt in ('-p', '--passwd'):
            passwd = arg

    try:
        db = pymysql.connect(host='127.0.0.1', user=user, passwd=passwd, port=int(port), autocommit=None)
        cursor = db.cursor()
    except Exception as e:
        print(e)
        raise Exception('数据库连接失败')

    try:
        res_list, pid = list(), str()

        cursor.execute('cetus')
        for item in cursor.fetchall():
            if item[1] == 'Startup time':
                pid = item[0]
                res_list.append(('startup_time', item[2]))
            if item[1] == 'Loaded modules':
                res_list.append(('modules', item[2]))
            if item[1] == 'Idle backend connections':
                res_list.append(('idle_conns', item[2]))
            if item[1] == 'Used backend connections':
                res_list.append(('used_conns', item[2]))
            if item[1] == 'Client connections':
                res_list.append(('client_conns', item[2]))
            if item[1] == 'Query count':
                res_list.append(('query_count', item[2]))
            if item[1] == 'QPS (1min, 5min, 15min)':
                _u = item[2].split(',')
                res_list.append(('qps1', _u[0].strip()))
                res_list.append(('qps5', _u[1].strip()))
                res_list.append(('qps15', _u[2].strip()))
            if item[1] == 'TPS (1min, 5min, 15min)':
                _u = item[2].split(',')
                res_list.append(('tps1', _u[0].strip()))
                res_list.append(('tps5', _u[1].strip()))
                res_list.append(('tps15', _u[2].strip()))

        backends_list = list()
        cursor.execute('select * from backends')
        for item in cursor.fetchall():
            backends_list.append(item[2:])
        res_list.append(('backends', str(backends_list)))

        cpu, mem = get_cpu_mem(pid)
        res_list.extend([('cpu', cpu), ('mem', mem)])

        cursor.execute('show status')
        for item in cursor.fetchall():
            res_list.append((item[1], item[2]))

        return 0, res_list

    except Exception as e:
        print(e)
        raise Exception('数据查询失败')
    finally:
        db.close()


if __name__ == '__main__':
    ret, msg = main()
    print(msg)
    sys.exit(ret)
