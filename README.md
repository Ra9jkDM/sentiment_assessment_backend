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
    set key value

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

### Memcached

Не сохраняет кеш после перезагрузки (https://docs.memcached.org/features/restart/)

docker exec -it 54949211863b /bin/bash
ls -ahl /tmp
id # 1001
sudo chown -R 1001:1001 data/ # dir data is empty

    services:
    memcached:
        image: bitnami/memcached:latest
        restart: always
        ports:
        - "11211:11211"
        volumes:
        - ./data:/data
        command: /opt/bitnami/scripts/memcached/run.sh -vvv -e /data/memory_file

#### View cache data

    telnet localhost 11211
    stats items
    stats cachedump 4 10
    stats slabs

    EXIT: ctrl+]

#### Kill process on local port

    fuser 8000/tcp # view
    fuser -k 8000/tcp # kill (tcp or udp)

### Bugs

#### 1 При входе не давало входить и выбрасывало на экран авторизации

При формировании файла куки в нем попался символ '/', который экранировался как '%2'. Из-за этого при сравнении файлов на стороне сервера авторизационные куки не совпадали и фронтенд корректно отрабатывал выбрасывая пользователя из аккауна.
Для исправления этого поведения была использована функция 'from urllib.parse import unquote'

- Bug исправлен

#### 2 При перезагрузке memcache пользователь не мог выйти из аккаунта

При перезагрузке сервиса, где храняться cookie для авторизации вошедший в приложение пользователь
не мог выйти. Для выхода требовалось зайти в панель разработчика -> Хранилище -> Cookies и вручную удалить
запись с ключем "auth"
Для  исправления добавлена проверка на существование ключа в базе данных memcache, если ключ есть, то он удаляется, 
иначе сервер отдает запрос с положительным ответом и пользователя выкидывает(разлогинивает) из приложения
Memcache имеет функцию Warm Restart, которая должна позволять перезагружжать сервис без потери ключей (сохраняя их в файл),
но данная функция не работает

- Bug исправлен