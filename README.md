Backend on fastapi
----


### Start project

    export $(cat .env)
    python main.py


### Create user in Postgress

    CREATE USER ml_user WITH PASSWORD 'secret_password';
    GRANT ALL PRIVILEGES ON DATABASE ml_web to ml_user;
    GRANT ALL ON SCHEMA public TO ml_user;
