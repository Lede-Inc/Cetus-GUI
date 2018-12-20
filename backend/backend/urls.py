from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from cetus import views, tasks

router = routers.DefaultRouter()
router.register(r'cetus', views.CetusViewSet)
router.register(r'node', views.CetusNodeViewSet)
router.register(r'task', tasks.TaskStatusSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^login/', obtain_jwt_token),
]
