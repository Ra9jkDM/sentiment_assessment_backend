import pytest
from fastapi.testclient import TestClient
from main import app
from tests.test_environment import recreate, url, user
import requests

recreate()

# @pytest.mark.skip()

def test_get_version():
    res = requests.get(url+'version')

    assert res.status_code == 200
    assert 'version' in res.json()

def test_register_user():
    res = requests.post(url+'registration', json=user)

    print(res.json())

    assert res.status_code == 200
    assert res.json()['status'] == 'success'

def test_is_user_in_system():
    res = requests.post(url+'login', json={
        "username": user['username'],
        "password": user['password'],
        "is_active": True
    })

    print(res.json())

    assert res.status_code == 200
    assert res.json()['status'] == 'success'
    assert 'cookie' in res.json()

def test_logout():
    res = requests.post(url+'login', json={
        "username": user['username'],
        "password": user['password'],
        "is_active": True
    })

    print(res.json())
    cookie = res.json()['cookie']
    res = requests.get(url+'logout', cookies={'auth': cookie})

    assert res.status_code == 200
    assert res.json()['status'] == 'success'