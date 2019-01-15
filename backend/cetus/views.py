from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

import ast
from celery import signature
import logging

from .serializers import CetusGroupSerializer, CetusNodeSerializer
from .models import TbCetusGroupInfo, TbCetusNodeInfo
from .tasks import remove_node, remove_cetus
from .func import CetusConn, convert_command_results
from backend.settings import DATABASES

logger = logging.getLogger('django')


class CetusViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    Cetus服务信息视图
    """
    queryset = TbCetusGroupInfo.objects.all().order_by('-create_time')
    serializer_class = CetusGroupSerializer
    filter_fields = ('cetus_name', 'cetus_type')

    def create(self, request, *args, **kwargs):
        """
        新增服务与节点
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_cetus = serializer.save()

        for node in request.data.get('nodes'):
            node_data = {'group_id': new_cetus.id,
                         'salt_id': node.get('salt_id'),
                         'service_port': request.data.get('service_port'),
                         'admin_port': request.data.get('admin_port'),
                         'version': ''
                         }
            TbCetusNodeInfo.objects.create(**node_data)

        return Response(new_cetus, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def install(self, request):
        """
        安装服务
        """
        data = request.data
        data['version'] = data.get('version') or 'null'
        data['path'] = data.get('path') or '/home'
        cetus_info = self.create(request)
        data['id'] = cetus_info.data.id
        signature('install_cetus', kwargs=data).delay()
        return Response('安装请求发送成功', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def command(self, request, pk=None):
        """
        执行管理命令
        """
        data = request.data
        msg = list()
        for node_id in data.get('nodes'):
            node_info = TbCetusNodeInfo.objects.get(pk=node_id)
            cetus_info = TbCetusGroupInfo.objects.get(pk=node_info.group_id)
            try:
                admin_info = CetusConn(db=cetus_info.config_db,
                                       cursor='dict',
                                       **DATABASES['catalog']) \
                    .get_remote_db_args(['admin-username', 'admin-password'])
                conn = CetusConn(host=node_info.salt_id,
                                 port=node_info.admin_port,
                                 user=admin_info['admin-username'],
                                 password=admin_info['admin-password'])
                r = conn.execute(data.get('commands'))
                r = convert_command_results("%s:%s" %
                                            (node_info.salt_id, node_info.admin_port), r, 0)
            except Exception as e:
                r = convert_command_results("%s:%s" %
                                            (node_info.salt_id, node_info.admin_port),
                                            ast.literal_eval(str(e)), 1)
            msg.append(r)

        return Response(msg, status=status.HTTP_200_OK)

    @action(methods=['get', 'post'], detail=True)
    def param(self, request, pk=None):
        """
        修改参数
        """
        data = request.data
        config_db = TbCetusGroupInfo.objects.get(pk=pk).config_db
        if request.method == 'GET':
            res = CetusConn(db=config_db,
                            cursor='dict',
                            **DATABASES['catalog']) \
                .get_cetus_fund_params(request.GET.get('type'))
        elif request.method == 'POST':
            res = CetusConn(db=config_db,
                            cursor='dict',
                            **DATABASES['catalog']) \
                .change_cetus_fund_params(data.get('type'), data.get('data'))

            admin_info = CetusConn(db=config_db,
                                   cursor='dict',
                                   **DATABASES['catalog']) \
                .get_remote_db_args(['admin-username', 'admin-password'])
            try:
                for item in TbCetusNodeInfo.objects.filter(group_id=pk):
                    conn = CetusConn(host=item.salt_id,
                                     port=item.admin_port,
                                     user=admin_info['admin-username'],
                                     password=admin_info['admin-password'])
                    conn.execute('config reload')
            except Exception as e:
                logger.error('Cetus Not Start')

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def remove(self, request, pk=None):
        """
        删除服务
        """
        res = remove_cetus(pk)
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def upgrade(self, request, pk=None):
        """
        更新服务
        """
        data = request.data
        data['version'] = data.get('version') or 'null'
        for item in TbCetusNodeInfo.objects.filter(group_id=pk):
            data.update(id=item.id)
            TbCetusNodeInfo.objects.filter(pk=item.id).update(status=2)
            signature('upgrade_node', kwargs=data).delay()
        return Response('更新请求发送成功', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def operate(self, request, pk=None):
        """
        操作服务
        """
        data = request.data
        for item in TbCetusNodeInfo.objects.filter(group_id=pk):
            data.update(id=item.id)
            res = signature('operate_node', kwargs=data)()
        return Response(res, status=status.HTTP_200_OK)


class CetusNodeViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Cetus节点信息视图
    """
    queryset = TbCetusNodeInfo.objects.all()
    serializer_class = CetusNodeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_node = serializer.save()
        return Response(new_node, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def install(self, request):
        """
        安装节点
        """
        data = request.data
        data['version'] = data.get('version') or 'null'
        data['path'] = data.get('path') or '/home'
        cetus_info = self.create(request)
        data['id'] = cetus_info.data.id
        signature('install_node', kwargs=data).delay()
        return Response('安装请求发送成功', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def upgrade(self, request, pk=None):
        """
        更新节点
        """
        data = request.data
        data['version'] = data.get('version') or 'null'
        TbCetusNodeInfo.objects.filter(pk=data['id']).update(status=2)
        signature('upgrade_node', kwargs=data).delay()
        return Response('更新请求发送成功', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def remove(self, request, pk=None):
        """
        删除节点
        """
        res = remove_node(id=pk)
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def operate(self, request, pk=None):
        """
        操作节点
        """
        data = request.data
        data.update(id=pk)
        res = signature('operate_node', kwargs=data)()
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def monitor(self, request, pk=None):
        """
        监控节点
        """
        data = request.data
        data.update(id=pk)
        node_info = TbCetusNodeInfo.objects.get(pk=pk)
        cetus_info = TbCetusGroupInfo.objects.get(pk=node_info.group_id)

        res = CetusConn(db=cetus_info.config_db,
                        cursor='dict',
                        **DATABASES['catalog']) \
            .get_monitor_data(pk, 168, cetus_info.cetus_type)
        return Response(res, status=status.HTTP_200_OK)
