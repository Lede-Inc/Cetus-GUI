from django.db import models
from datetime import datetime


class TbCetusGroupInfo(models.Model):
    CETUS_TYPE = (
        ("rw", "读写分离版"),
        ("shard", "分片版"),
    )
    cetus_name = models.CharField(max_length=20, verbose_name="Cetus名称")
    cetus_type = models.CharField(max_length=10, choices=CETUS_TYPE, verbose_name="Cetus类型")
    config_db = models.CharField(max_length=20, null=True, verbose_name="配置库库名")
    create_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateTimeField(null=True, verbose_name="更新时间")


    class Meta:
        verbose_name = "Cetus服务"
        verbose_name_plural = verbose_name
        db_table = "tb_cetus_group_info"


class TbCetusNodeInfo(models.Model):
    group = models.ForeignKey(TbCetusGroupInfo, on_delete=models.CASCADE, verbose_name="节点所属组", related_name='nodes')
    salt_id = models.CharField(max_length=50, verbose_name="SALT ID")
    service_port = models.IntegerField(verbose_name="服务端口")
    admin_port = models.IntegerField(verbose_name="管理端口")
    version = models.CharField(max_length=100, null=True, verbose_name="版本")
    dir = models.CharField(max_length=200, null=True, verbose_name="路径")
    status = models.IntegerField(default=1, verbose_name="节点状态")
    create_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateTimeField(null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Cetus节点"
        verbose_name_plural = verbose_name
        db_table = "tb_cetus_node_info"


