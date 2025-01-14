Backend on fastapi
----


### Requirements

    pip freeze > requirements.txt
    pip install -r requirements.txt

### Setup environ

    . dev.sh

### Start project

    export $(cat .env)
    python main.py

### Create user in Postgress

    CREATE DATABASE ml_web;
    CREATE USER ml_user WITH PASSWORD 'secret_password';
    GRANT ALL PRIVILEGES ON DATABASE ml_web to ml_user;
    GRANT ALL ON SCHEMA public TO ml_user;

    GRANT ALL ON DATABASE ml_web TO ml_user;
    ALTER DATABASE ml_web OWNER TO ml_user;

#### Redis

##### Connect

    redis-cli
    auth secret_key

##### Get all keys

    keys *
    get key

##### Remove all keys

    flushall


### Systemd

/lib/systemd/system/sent_analis.service (pgadmin.service)
sudo chmod 644 file.service

[Unit]
Description=Sentiment Analis Backend Service
After=network.target

[Service]
Type=idle
Restart=on-failure
User=den
ExecStart=/home/den/ml_sen_project/back/start.sh

[Install]
WantedBy=multi-user.target

#!/bin/bash

cd /home/den/ml_sen_project/back
export $(cat .env)
source venv/bin/activate
python main.py

sudo systemctl daemon-reload

### Bugs

#### 1 При входе не давало входить и выбрасывало на экран авторизации

При формировании файла куки в нем попался символ '/', который экранировался как '%2'. Из-за этого при сравнении файлов на стороне сервера авторизационные куки не совпадали и фронтенд корректно отрабатывал выбрасывая пользователя из аккауна.
Для исправления этого поведения была использована функция 'from urllib.parse import unquote'

- Bug исправлен