#!/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import getopt
import socket
import shutil


def help_and_exit():
    print('''Usage:
    -h 显示帮助信息
    -t Cetus类型
    -p 服务端口
    -a 管理端口
    -b 分支
    -d Cetus目录
    ''')
    sys.exit()


def check_socket(port_list):
    for index in port_list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', int(index)))
        sock.close()
        if not result:
            raise Exception('端口已被占用')


def create_environment(user, cetus_path):
    try:
        os.system('useradd %s' % user)
        p = subprocess.Popen('sudo yum install cmake gcc glib2-devel flex mysql-devel gperftools-libs git -y',
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()
        path = cetus_path[:cetus_path.rfind('/')] + '/logs'
        if not os.path.exists(path):
            os.makedirs(path)
        os.system('chown -R %s:%s %s' % (user, user, path))
    except Exception as e:
        print(e)
        raise Exception('环境初始化失败')


def install_cetus(cetus_type, cetus_route, cetus_path, user):
    try:
        os.chdir(cetus_route)
        cetus_type = 'ON' if cetus_type == 'rw' else 'OFF'

        p = subprocess.Popen('mkdir build && cd build && cmake ../ -DCMAKE_BUILD_TYPE=Debug '
                             '-DCMAKE_INSTALL_PREFIX=%s -DSIMPLE_PARSER=%s && make install' % (cetus_path, cetus_type),
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()
        os.system('chown -R %s:%s %s' % (user, user, cetus_path[:cetus_path.rfind('/')]))
    except Exception as e:
        print(e)
        raise Exception('安装失败')
    finally:
        shutil.rmtree(cetus_route, ignore_errors=True)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'ht:s:a:r:p:',
                                   ['help', 'type=', 'service=', 'admin=', 'route=', 'path='])
    except getopt.GetoptError as err:
        print(err)
        help_and_exit()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help_and_exit()
        elif opt in ('-t', '--type'):
            cetus_type = arg
        elif opt in ('-s', '--service'):
            service_port = arg
        elif opt in ('-a', '--admin'):
            admin_port = arg
        elif opt in ('-r', '--route'):
            cetus_route = arg
        elif opt in ('-p', '--path'):
            cetus_path = arg

    try:
        check_socket([service_port, admin_port])
        user = 'cetus_%s' % service_port
        create_environment(user, cetus_path)
        install_cetus(cetus_type, cetus_route, cetus_path, user)
        return 0, '安装成功'

    except Exception as e:
        print(e)
        return 1, e


if __name__ == '__main__':
    ret, msg = main()
    sys.exit(ret)
