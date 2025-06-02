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

### Default admin user

    sent@admin.com:admin123

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
    set key value

##### Remove all keys

    flushall


### Systemd

    /lib/systemd/system/sent_analis.service (pgadmin.service)
    /lib/systemd/system/sent_model.service 
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

#### Kill process on local port

    fuser 8000/tcp # view
    fuser -k 8000/tcp # kill (tcp or udp)

#### Настройка Nginx

Внести изменения в файл ```/etc/nginx/sites-enabled/default```

    server {
            root /var/www/html/sent_analis;
            index index.html index.htm;
            server_name domain.com;

            location / {
                try_files $uri $uri/ /index.html?$args;
            }

            location /api/ {
                proxy_pass http://127.0.0.1:8000;
            }


        listen [::]:443 ssl; 
        listen 443 ssl; 

        # SSL настройки и сертификаты Certbot
        ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem; 
        ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;
        include /etc/letsencrypt/options-ssl-nginx.conf; 
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; 
    }


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

#### 3 Возникала ошибка при отправке больших файлов больше 3KB

Ошибка в логике при взаимодействии с MinIO соединение закрывалось, а после этого была попытка скачивания содержимого файла. Была добавлена команда предзагрузки файла

- Bug исправлен

#### 4 При изменении личной информации пользователь мог повысить свои привилегии
От имени пользователя можно было отправить запрос на '/api/user/update' и сменить роль на 'admin'

- Bug исправлен

#### Удаление файлов более 100MB из репозитория

[BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)


    wget https://repo1.maven.org/maven2/com/madgag/bfg/1.15.0/bfg-1.15.0.jar
    
    java -jar bfg-1.15.0.jar -D e3_lstm.pt .
    java -jar bfg-1.15.0.jar -D e5_lstm_web.pt .
    git reflog expire --expire=now --all && git gc --prune=now --aggressive
