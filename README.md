## Cetus GUI

---

Cetus GUI是基于web端的Cetus集群可视化管理系统，能有效的提升部署与管理Cetus集群的效率。

**本项目当前仅适用于RedHat/CentOS系统在SaltStack环境下使用远程配置库安装配置多Cetus节点的需求。**

---

### 环境需求

---

系统要求：CentOS 6+

环境要求：SaltStack Latest

---

### 安装

**请务必先阅读 [help](./frontend/docs/HELP.md) 文档来配置基础环境。**

```

git clone https://github.com/Lede-Inc/Cetus-GUI
cd Cetus-GUI

修改如下配置：

# Salt默认配置文件
vi /etc/salt/master
file_roots:
  base:
    - $PROJECT_PATH/cetus_gui/backend/shells

# 修改Django配置文件
vi backend/backend/settings.py
DATABASES = {
    # 默认数据库，存放项目和Cetus信息
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xxx',
        'USER': 'xxx',
        'PASSWORD': 'xxx',
        'HOST': 'xxx',
        'PORT': xxx,
    },
    # 存放Cetus远程配置库信息，可与默认数据库一致
    'catalog': {
        'user': 'xxx',
        'password': 'xxx',
        'host': 'xxx',
        'port': xxx,
    }
}
# Cetus源代码路径
CETUS_URL = 'https://github.com/Lede-Inc/cetus'
# RabbitMQ配置端口
BROKER_URL = 'amqp://guest@localhost:5672//'

修改后执行：
sh deploy.sh

```

### 登陆

---

```
http://localhost:9528
```

### TODO

---

```
本地Cetus监控
Docker部署
```

