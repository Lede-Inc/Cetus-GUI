#!/bin/python3

import sys
import subprocess
import os
import getopt
import shutil


def help_and_exit():
    print('''Usage:
    -h 显示帮助信息
    -u 下载地址
    -t 类型
    -r 路径
    -v 版本号
    ''')
    sys.exit()


def download_cetus(**kwargs):
    try:
        shutil.rmtree(kwargs.get('cetus_route'), ignore_errors=True)
        p = subprocess.Popen('git clone {cetus_url} {cetus_route}'.format(**kwargs),
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()
        if os.path.isdir(kwargs.get('cetus_route')):
            os.chdir(kwargs.get('cetus_route'))
            cmd = 'git log --pretty=format:%ad.%h --date=short -n1;'
            if kwargs.get('cetus_version') != 'null':
                cmd = 'git checkout {cetus_version};'.format(**kwargs) + cmd
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            o = bytes.decode(p.communicate()[0]).replace('-', '')
        else:
            raise Exception('下载失败')
        return 0, o
    except Exception as e:
        print(e)
        return 1, e


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'ht:v:u:r:',
                                   ['help', 'type=', 'version=', 'url=', 'route='])

    except getopt.GetoptError as err:
        print(err)
        help_and_exit()

    cetus_url = 'https://github.com/Lede-Inc/cetus'
    cetus_route = '/tmp/cetus_mirror'
    cetus_version = 'null'
    cetus_type = 'rw'
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help_and_exit()
        elif opt in ('-t', '--type'):
            cetus_type = arg
        elif opt in ('-v', '--version'):
            cetus_version = arg
        elif opt in ('-u', '--url'):
            cetus_url = arg
        elif opt in ('-r', '--route'):
            cetus_route = arg

    code, cetus_version = download_cetus(**locals())
    return code, 'cetus.{cetus_type}.{cetus_version}'.format(**locals())


if __name__ == '__main__':
    ret, msg = main()
    print(msg)
    sys.exit(ret)
