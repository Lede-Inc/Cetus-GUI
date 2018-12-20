#!/bin/bash

sudo yum install -y gcc gcc-c++ python34 python34-devel python34-pip erlang rabbitmq-server nodejs
sudo service rabbitmq-server start
sudo rabbitmqctl start_app
sudo pip3 install virtualenv
sudo pip2 install supervisor
virtualenv -p python3 cetus_env
source cetus_env/bin/activate
mkdir logs

cd backend/
pip install -r requirement.txt
python manage.py makemigrations
python manage.py makemigrations cetus
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model();
User.objects.create_superuser('admin', '', 'admin') if not User.objects.filter(username='admin') else 0;" | python manage.py shell

cd ../frontend/
npm install

cd ..
supervisord -c supervisor.cnf
supervisorctl restart backend beat celerycam cetus frontend monitor
