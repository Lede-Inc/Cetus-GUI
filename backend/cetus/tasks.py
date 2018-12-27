from rest_framework import viewsets, mixins
from celery.decorators import task
from djcelery.models import TaskState, PeriodicTask

import random
import string
import time
import logging

from .func import SaltClient, config_remote_configuration_db
from .models import TbCetusGroupInfo, TbCetusNodeInfo
from .serializers import TaskStatusSerializer
from backend.settings import DATABASES, CETUS_URL

logger = logging.getLogger('django')


class TaskStatusSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    任务信息视图
    """
    queryset = TaskState.objects.all()
    serializer_class = TaskStatusSerializer


@task(name='install_cetus')
def install_cetus(**kwargs):
    """
    安装Cetus任务
    """

    logger.info(kwargs)
    kwargs.update(cetus_url=CETUS_URL,
                  # 生成随机路径下载Cetus
                  cetus_route='/tmp/cetus_mirror_%s' %
                              ''.join(random.choice(string.ascii_uppercase +
                                                    string.digits) for _ in range(10)))

    try:
        for node in kwargs.get('nodes'):
            node_id = TbCetusNodeInfo.objects.get(salt_id=node.get('salt_id'),
                                                  service_port=kwargs.get('service_port')).id
            kwargs.update(node_id=node_id,
                          salt_id=node.get('salt_id'))
            kwargs.update(record_version=SaltClient.download_cetus_node(**kwargs))

            kwargs.update(dir='{path}/cetus_{service_port}/{record_version}'.format(**kwargs))
            TbCetusNodeInfo.objects.filter(pk=node_id) \
                .update(version=kwargs.get('record_version'), dir=kwargs.get('dir'))

            SaltClient.install_cetus_node(**kwargs)
    except Exception as e:
        logger.error(e)
        TbCetusGroupInfo.objects.filter(id=kwargs.get('id')).delete()
        raise Exception('安装失败')

    try:
        if kwargs.get('control') == 'remote':
            config_db = 'cetus_remote_%s' % kwargs.get('id')
            kwargs.update(cetus_dir='{path}/cetus_{service_port}'.format(**kwargs),
                          database=config_db,
                          **DATABASES['catalog'])
            config_remote_configuration_db(**kwargs)
            TbCetusGroupInfo.objects.filter(id=kwargs.get('id')).update(config_db=config_db)
    except Exception as e:
        logger.error(e)
        TbCetusGroupInfo.objects.filter(id=kwargs.get('id')).delete()
        raise Exception('远程库配置失败')

    # TODO: 增加本地支持
    # elif kwargs.get('control') == 'local':
    #     TbCetusGroupInfo.objects.filter(id=kwargs.get('id')).update(config_db='locally')

    for node in TbCetusNodeInfo.objects.filter(group_id=kwargs.get('id')):
        SaltClient.operate_cetus_node(node.id, 'start')


@task(name='install_node')
def install_node(**kwargs):
    """
    安装节点任务
    """

    logger.info(kwargs)
    cetus_info = TbCetusGroupInfo.objects.get(pk=kwargs['group'])
    kwargs.update(id=kwargs['id'],
                  node_id=kwargs['id'],
                  cetus_type=cetus_info.cetus_type,
                  config_db=cetus_info.config_db,
                  cetus_url=CETUS_URL,
                  cetus_route='/tmp/cetus_mirror_%s' %
                              ''.join(random.choice(string.ascii_uppercase +
                                                    string.digits) for _ in range(10)))

    try:
        kwargs.update(version=SaltClient.download_cetus_node(**kwargs))

        kwargs.update(dir='{path}/cetus_{service_port}/{version}'.format(**kwargs))
        TbCetusNodeInfo.objects.filter(pk=kwargs.get('id')) \
            .update(version=kwargs.get('version'), dir=kwargs.get('dir'))

        SaltClient.install_cetus_node(**kwargs)
    except Exception as e:
        logger.error(e)
        TbCetusNodeInfo.objects.filter(id=kwargs.get('id')).delete()
        raise Exception('安装失败')
    else:
        SaltClient.operate_cetus_node(kwargs.get('id'), 'start')


@task(name='upgrade_node')
def upgrade_node(**kwargs):
    """
    更新节点任务
    """

    logger.info(kwargs)
    node_info = TbCetusNodeInfo.objects.get(pk=kwargs['id'])
    cetus_info = TbCetusGroupInfo.objects.get(pk=node_info.group_id)
    kwargs.update(salt_id=node_info.salt_id,
                  cetus_type=cetus_info.cetus_type,
                  cetus_url=CETUS_URL,
                  cetus_route='/tmp/cetus_mirror_%s' %
                              ''.join(random.choice(string.ascii_uppercase +
                                                    string.digits) for _ in range(10)),
                  service_port=node_info.service_port,
                  admin_port=node_info.admin_port)

    try:
        SaltClient.operate_cetus_node(kwargs.get('id'), 'abort')
        TbCetusNodeInfo.objects.filter(pk=kwargs.get('id')).update(status=2)

        kwargs.update(version=SaltClient.download_cetus_node(**kwargs))
        kwargs.update(dir=node_info.dir[:node_info.dir.rfind('/') + 1] + kwargs['version'])

        SaltClient.install_cetus_node(node_id=kwargs.get('id'), **kwargs)

        TbCetusNodeInfo.objects.filter(pk=kwargs.get('id')) \
            .update(version=kwargs.get('version'), dir=kwargs.get('dir'))

    except Exception as e:
        logger.error(e)
        TbCetusNodeInfo.objects.filter(pk=kwargs['id']).update(status=-1)
        raise Exception('更新失败')
    else:
        SaltClient.operate_cetus_node(kwargs.get('id'), 'start')


@task(name='remove_cetus')
def remove_cetus(pk):
    """
    删除Cetus任务
    """

    try:
        for item in TbCetusNodeInfo.objects.filter(group_id=pk):
            SaltClient.operate_cetus_node(item.id, 'abort')
            PeriodicTask.objects.filter(name='node_%s_monitor' % item.id).delete()
        TbCetusGroupInfo.objects.filter(pk=pk).delete()
        return '删除成功'
    except Exception as e:
        return '删除失败'


@task(name='remove_node')
def remove_node(**kwargs):
    """
    删除节点任务
    """

    code, res = SaltClient.operate_cetus_node(kwargs.get('id'), 'abort')
    if not code:
        TbCetusNodeInfo.objects.filter(pk=kwargs.get('id')).delete()
        PeriodicTask.objects.filter(name='node_%s_monitor' % kwargs.get('id')).delete()
        return '删除成功'
    else:
        return '删除失败'


@task(name='operate_node')
def operate_node(**kwargs):
    """
    操作节点任务
    """

    code, msg = SaltClient.operate_cetus_node(kwargs.get('id'), kwargs.get('type'))
    return msg


@task(name='cetus_monitor')
def cetus_monitor(*args):
    """
    收集监控信息任务
    """

    return SaltClient.record_monitor_data(args[0],
                                          time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
