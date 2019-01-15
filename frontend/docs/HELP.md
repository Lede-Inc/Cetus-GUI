## Cetus-GUI 帮助文档

---

此文档主要是帮助您解决Cetus-GUI安装和使用过程中可能会出现的问题。

目前项目处于测试阶段，希望您在使用时能积极向我们反馈bug和需求，我们将会很快的解决。

---

### 基础环境配置

---

**所有与项目相关节点**确保有Python3环境。

**所有节点**确保执行下列命令：

* sudo yum install gcc gcc-c++ python3-devel python3-pip git
* sudo pip3 install pymysql

---

### docker部署

---

此处是docker方式部署的配置方法，适用于简单配置Cetus-GUI环境的方式，源码安装请见源码部署一节。

#### docker安装

```
  # sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-selinux docker-engine-selinux docker-engine
  # sudo yum install -y yum-utils device-mapper-persistent-data lvm2
  # sudo yum-config-manager --add-repo https://mirrors.ustc.edu.cn/docker-ce/linux/centos/docker-ce.repo
  # sudo yum makecache fast
  # sudo yum install docker-ce
  # sudo pip install -U docker-compose
```

#### 镜像部署

部署服务器的3306/4505/4506/8300/9527端口请务必不要占用！

```
  # git clone https://github.com/Lede-Inc/Cetus-GUI
  # cd Cetus-GUI/backend/install
  # docker-compose up -d
```

#### SaltStack安装

docker节点已经默认安装了salt-master，此处只需安装Minion节点即可，docker节点所在服务器也可以配置为Minion。

* 安装
    
``` 
    # sudo yum install https://repo.saltstack.com/py3/redhat/salt-py3-repo-latest-2.el7.noarch.rpm
    # sudo yum clean expire-cache
    # sudo yum install salt-minion
```
    
* 配置

```
    # sudo vi /etc/salt/minion
  
    master: Master节点ip，此处填写docker节点所在宿主机的ip即可
    id: Minion唯一标识
```

* 启动

```
    # sudo service salt-minion start
```

* 测试

  在镜像内部执行，测试Minion是否配置成功。

```
    # salt-key -A -y
    # salt-key -L
    # salt '*' test.ping 
```

#### 网络配置

由于网络配置原因，需要修改部分配置信息。

为简化说明，我们假设镜像所在节点ip为10.0.0.1，Minion id为Minion1。待安装Cetus节点ip为10.0.0.2，Minion id为Minion2。

* 镜像内部执行

```
    # echo '10.0.0.1 Minion1' >> vi /etc/hosts
    # echo '10.0.0.2 Minion2' >> vi /etc/hosts
```

* 所有Minion节点执行

```
    # echo '10.0.0.1 cetus_gui_db' >> vi /etc/hosts
```

#### 登陆

http://localhost:9527

---

### 源码部署

---

源码部署适合于对项目进行大规模修改的情况，docker方式部署请跳过这一段。

#### SaltStack安装

项目的应用依赖于配置好的SaltStack环境，请确保环境足够新以支持Python3 API。

以下是出现问题时可能的解决方案：

* 安装

    Master节点：
    * 项目当前**必须**与Master节点位于同一个服务器
    * 安装流程
        * sudo yum install https://repo.saltstack.com/py3/redhat/salt-py3-repo-latest-2.el7.noarch.rpm
        * sudo yum clean expire-cache
        * sudo yum install salt-master
        * sudo yum install salt-minion
        
    Minion节点：
    * Master节点所在服务器也可以配置为Minion
    * 安装流程
        * sudo yum install https://repo.saltstack.com/py3/redhat/salt-py3-repo-latest-2.el7.noarch.rpm
        * sudo yum clean expire-cache
        * sudo yum install salt-minion

* 配置

    Master节点：
    * 配置
    
    ```
      # sudo vi /etc/salt/master
      
      file_roots:
        base:
         - $PATH/backend/shells    # $PATH指项目所在路径
    ```
    
    * 启动
        * sudo service salt-master start

    Minion节点：
    * 配置
    
    ```
      # sudo vi /etc/salt/minion
      
      master: Master节点
      id: Minion唯一标识
    ```
    
    * 启动
        * sudo service salt-master start
        
* 非root用户启动

    在启动salt时可以修改启动用户，与整个项目的部署用户保持一致。**这一步是我们用非root用户部署项目时，必须要做的。**
    
    ```
      # sudo vi /etc/salt/master
          
      user: user
      
      # 修改权限
      # sudo chown -R user:user /etc/salt /var/cache/salt /var/log/salt /var/run/salt
      
      # sudo service salt-minion restart
    ```
    
    Minion节点不需要修改，这样可以使发送到Minion的命令仍为root执行。
        
* 其他问题

    如果有salt命令执行时报编码错误，极有可能是调用了Python2下的salt命令，请删除Python2配置环境下的SaltStack并安装Python3版本。
    
    pip3 install salt

#### 部署环境

部署环境上至少需要Python2和Python3双版本，需要**至少一个MySQL实例来放置项目数据库和Cetus配置数据库**。

```
    git clone https://github.com/Lede-Inc/Cetus-GUI
    cd Cetus-GUI
    
    修改如下配置：
    
    # Salt默认配置文件
    vi /etc/salt/master
    file_roots:
      base:
        - $PROJECT_PATH/Cetus-GUI/backend/shells
    
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

以下是出现问题时可能的解决方案：

* 更新项目代码

    ```
    # git pull origin master
    # sh deploy.sh
    ```
    
* RabbitMQ问题

    * 可参考https://github.com/judasn/Linux-Tutorial/blob/master/markdown-file/RabbitMQ-Install-And-Settings.md
    
* 端口占用
    
    请确保以下端口未被占用
    * Django项目占用8000端口
    * Supervisor占用9001端口
    * SaltStack占用4505/4056端口
    * Vue项目占用9528端口
    
* 部署情况查询
    
    ```
    # supervisorctl
    backend                          RUNNING
    beat                             RUNNING
    celerycam                        RUNNING
    cetus                            RUNNING
    frontend                         RUNNING
    monitor                          RUNNING
    ```
    
    若有进程的状态非RUNNING，请查看deploy.sh的执行日志情况。
    
---

### 日志管理

---

在部署应用和安装配置Cetus过程中可能会存在各种报错，有些情况可能无法直接从网页端获取结果或解决方案，需要从后台日志中查询。

以下是应用程序和Cetus日志对应的位置。

* 应用日志

```
    cd $PATH/logs               # $PATH指项目所在路径(docker的路径为/app)
    supervisor_backend.log      # Django日志  
    supervisor_beat.log          
    supervisor_celerycam.log    
    supervisor_cetus.log        # 后台任务日志
    supervisord.log             
    supervisor_frontend.log     
    supervisor_monitor.log      # Cetus监控日志  
```

* Cetus日志

```
    cd $CETUS_PATH/logs         # $CETUS_PATH指Cetus项目所在路径，默认为/home/cetus_服务端口号
    cetus.log                   # 运行日志
    xa.log                      # XA事务日志
    slowquery.log               # 慢日志
```
