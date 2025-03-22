import pytest
from tests.test_environment import recreate, url, user
from tests.z_user_test import login
import requests


def admin_login():
    return login(username='sent@admin.com', password='admin123')


def test_list_users_with_wrong_role():
    cookie = login()
    res = requests.get(url+'admin/users', cookies=cookie, params={
        'page': 0
    })
    obj = res.json()
    print(obj)

    assert obj['detail'] == 'Wrong role'


def test_list_users():
    cookie = admin_login()
    res = requests.get(url+'admin/users', cookies=cookie, params={
        'page': 0
    })
    obj = res.json()
    print(obj)

    assert len(obj) == 2

    for i in obj:
        assert i['password'] == '********'

def test_get_user_length():
    cookie = admin_login()
    res = requests.get(url+'admin/users/length', cookies=cookie)
    obj = res.json()
    print(obj)

    assert obj == 2

def test_create_admin_user():
    cookie = admin_login()
    res = requests.post(url+'admin/users/create', cookies=cookie, json={
        "username": "user@example.com",
        "firstname": "string",
        "lastname": "string",
        "role": "admin",
        "password": "stringst",
        "is_active": False
    })
    obj = res.json()
    print(obj)

    assert obj['status'] == 'success'

    res = requests.get(url+'admin/users/length', cookies=cookie)
    assert res.json() == 3


def test_update_user():
    cookie = admin_login()
    res = requests.post(url+'admin/users/update', cookies=cookie, json={
        "username": "user@example.com",
        "firstname": "934tuhn",
        "lastname": "mf[wk]",
        "role": "user",
        "password": "dfhol809",
        "is_active": False
    })  
    assert res.json()['status'] == 'success'

def test_update_user():
    cookie = admin_login()

    res = requests.post(url+'admin/users/create', cookies=cookie, json={
        "username": "new_user@example.com",
        "firstname": "string",
        "lastname": "string",
        "role": "admin",
        "password": "stringst",
        "is_active": False
    })

    res = requests.post(url+'admin/users/delete', cookies=cookie, json={
        'user': 'new_user@example.com'
    })

    res = requests.get(url+'admin/users/length', cookies=cookie)
    assert res.json() == 3


def test_activate_user():
    cookie = admin_login()

    res = requests.post(url+'admin/users/create', cookies=cookie, json={
        "username": "new_user_1@example.com",
        "firstname": "string",
        "lastname": "string",
        "role": "admin",
        "password": "stringst",
        "is_active": False
    })

    res = requests.post(url+'admin/users/activate', cookies=cookie, json={
        "user": "new_user_1@example.com",
        "is_active": True
    })

    assert res.json()['status'] == 'success'

    res = requests.get(url+'admin/users', cookies=cookie, params={
        'page': 0,
        'name': 'new_user_1@example.com'
    })
    obj = res.json()

    assert obj[0]['is_active'] == True