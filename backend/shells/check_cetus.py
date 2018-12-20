#!/bin/python3
# -*- coding: utf-8 -*-

import getopt
import sys
import pymysql


def help_and_exit():
    print('''Usage:
    -h 显示帮助信息
    -u 用户
    -p 密码
    -P 端口
    ''')
    sys.exit()


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'hu:p:P:',
                                   ['help', 'user=', 'passwd=', 'port='])

    except getopt.GetoptError as err:
        print(err)
        help_and_exit()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help_and_exit()
        elif opt in ('-u', '--user'):
            user = arg
        elif opt in ('-p', '--passwd'):
            password = arg
        elif opt in ('-P', '--port'):
            port = arg

    try:
        conn = pymysql.connect(host='127.0.0.1', user=user, passwd=password, port=int(port), autocommit=None)
        cursor = conn.cursor()
        res = cursor.execute('select version')
        if res == 1:
            return 0, 'success'
    except Exception as e:
        return 1, e


if __name__ == '__main__':
    ret, msg = main()
    print(ret)
    print(msg)
    sys.exit(ret)
