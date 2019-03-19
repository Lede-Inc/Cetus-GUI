#!/bin/python3
# -*- coding: utf-8 -*-

import sys
import getopt
import os
import subprocess
import pwd
import signal
from threading import Timer


def help_and_exit():
    print('''Usage:
    -h 显示帮助信息
    -u 下载地址
    -t 类型
    -r 路径
    -v 版本号
    ''')
    sys.exit()


def change_user(username):
    user_info = pwd.getpwnam(username)
    os.setgid(user_info.pw_gid)
    os.setuid(user_info.pw_uid)


def start_cetus(**kwargs):
    try:
        os.chdir(kwargs.get('cetus_route'))
        change_user(kwargs.get('cetus_owner'))
        print('{cetus_route}/bin/cetus --remote-conf-url='
              'mysql://{user}:{passwd}@{host}:{port}/{database} 1>/dev/null 2>&1'.format(**kwargs))

        kill = lambda process: process.kill()
        p = subprocess.Popen('{cetus_route}/bin/cetus --remote-conf-url='
                             'mysql://{user}:{passwd}@{host}:{port}/{database} &> /dev/null'.format(**kwargs),
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        job = Timer(5, kill, [p])
        try:
            job.start()
        finally:
            job.cancel()

        return 0, 'success'

        # if p.returncode == 0:
        #     return 0, 'success'
        # else:
        #     raise Exception('failure')
    except Exception as e:
        return 1, e


def shutdown_cetus(**kwargs):
    return shutdown_abort_cetus(**kwargs)


def shutdown_abort_cetus(**kwargs):
    try:
        pid_path = '%s/%s.pid' % (kwargs.get('cetus_route')[:kwargs.get('cetus_route').rfind('/')],
                                  kwargs.get('cetus_owner'))
        if os.path.exists(pid_path):
            with open(pid_path, 'r') as f:
                pid_list = [int(f.read())]
        else:
            cmd = 'remote-conf-url.*' + kwargs.get('database')
            child = subprocess.Popen(['pgrep', '-f', cmd],
                                     shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = child.communicate()[0]
            pid_list = [int(pid) for pid in out.split()]
        for item in pid_list:
            os.kill(item, signal.SIGKILL)
        tmp_path = '/tmp/0.0.0.0:' + kwargs.get('admin_port')
        os.remove(tmp_path) if os.path.exists(tmp_path) else None
        return 0, 'success'
    except Exception as e:
        return 1, e


def restart_cetus(**kwargs):
    shutdown_abort_cetus(**kwargs)
    return start_cetus(**kwargs)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   't:h:P:u:p:d:r:o:a:',
                                   ['help', 'type=', 'host=', 'port=', 'user=', 'passwd=', 'database=', 'route=', 'owner=', 'admin='])

    except getopt.GetoptError as err:
        print(err)
        help_and_exit()

    for opt, arg in opts:
        if opt in ('--help',):
            help_and_exit()
        elif opt in ('-t', '--type'):
            operate_type = arg
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
        elif opt in ('-r', '--route'):
            cetus_route = arg
        elif opt in ('-o', '--owner'):
            cetus_owner = arg
        elif opt in ('-a', '--admin'):
            admin_port = arg

    if operate_type == 'start':
        res = start_cetus(**locals())
    elif operate_type == 'shutdown':
        res = shutdown_cetus(**locals())
    elif operate_type == 'restart':
        res = restart_cetus(**locals())
    elif operate_type == 'abort':
        res = shutdown_abort_cetus(**locals())

    return res


if __name__ == '__main__':
    ret, msg = main()
    print(msg)
    sys.exit(ret)
