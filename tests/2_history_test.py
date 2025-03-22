import pytest
from tests.test_environment import recreate, url, user
from tests.z_user_test import login
import requests

def test_history_type_text():
    cookie = login()
    res = requests.get(url+'history', cookies=cookie, params={
        'page': 0,
        'history_type': 'text'
    })
    obj = res.json()
    print(obj)

    assert len(obj) >= 7
    assert 'date' in obj[0]

def test_history_type_table():
    cookie = login()
    res = requests.get(url+'history', cookies=cookie, params={
        'page': 0,
        'history_type': 'table'
    })
    obj = res.json()
    print(obj)

    assert len(obj) == 1
    assert 'date' in obj[0]

def test_history_length_text():
    cookie = login()
    res = requests.get(url+'history/length', cookies=cookie, params={
        'history_type': 'text'
    })
    obj = res.json()
    print(obj)

    assert obj == 7

def test_history_length_table():
    cookie = login()
    res = requests.get(url+'history/length', cookies=cookie, params={
        'history_type': 'table'
    })
    obj = res.json()
    print(obj)

    assert obj == 1

def test_get_file():
    cookie = login()
    res = requests.get(url+'history/file', cookies=cookie, params={
        'id': 1
    })

    assert len(res.content) > 6000


def test_history_delete_text():
    cookie = login()
    res = requests.post(url+'history/delete', cookies=cookie, json={
        'id': 1,
        "history_type": "text"
    })
    obj = res.json()
    print(obj)

    assert obj['status'] == 'success'

    res = requests.get(url+'history/length', cookies=cookie, params={
        'history_type': 'text'
    })
    obj = res.json()
    print(obj)

    assert obj == 6

def test_history_delete_table():
    cookie = login()
    res = requests.post(url+'history/delete', cookies=cookie, json={
        'id': 1,
        "history_type": "table"
    })
    obj = res.json()
    print(obj)

    assert obj['status'] == 'success'

    res = requests.get(url+'history/length', cookies=cookie, params={
        'history_type': 'table'
    })
    obj = res.json()
    print(obj)

    assert obj == 0
