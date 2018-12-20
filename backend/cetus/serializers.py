from rest_framework import serializers

from .models import TbCetusGroupInfo, TbCetusNodeInfo
from djcelery.models import TaskState


class CetusNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TbCetusNodeInfo
        fields = "__all__"


class CetusGroupSerializer(serializers.ModelSerializer):
    nodes = CetusNodeSerializer(read_only=True, many=True)

    class Meta:
        model = TbCetusGroupInfo
        fields = "__all__"


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskState
        fields = "__all__"
