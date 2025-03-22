import pytest
from tests.test_environment import recreate, url, user
import requests

NEW_PASSWORD = 'new_pass_123'

def login(username=None, password=None):
    res = requests.post(url+'login', json={
        "username": username if username else user['username'],
        "password": password if password else user['password'],
        "is_active": True
    })
    response = res.json()
    print(response)
    return {'auth': response['cookie'] if 'cookie' in response else response}

def test_get_user_info():
    cookie = login()

    res = requests.get(url+'user', cookies=cookie)
    obj = res.json()
    print(obj)

    assert obj['username'] == user['username']
    assert obj['firstname'] == user['firstname']
    assert obj['lastname'] == user['lastname']
    assert obj['role'] == user['role']

def test_login_in_deactivate_user():
    cookie = login(username='user@example.com', password='stringst')
    assert cookie['auth']['status'] == 'failure'

def test_update_user():
    cookie = login()
    res = requests.post(url+'user/update', cookies=cookie, json={
        "username": user['username'],
        "firstname": "Bob_first_name",
        "lastname": "Last_name",
        "role": "admin"
    })

    assert res.json()['status'] == 'success'

    res = requests.get(url+'user', cookies=cookie)
    obj = res.json()

    assert obj['firstname'] == 'Bob_first_name'
    assert obj['lastname'] == 'Last_name'
    assert obj['role'] == 'user'

def test_get_null_photo():
    cookie = login()
    res = requests.get(url+'user/avatar', cookies=cookie)
    obj = res.json()

    print(obj)
    assert obj['status'] == 'failure'

def test_upload_photo():
    cookie = login()
    file = {'photo': b'test_img'}
    res = requests.post(url+'user/avatar/update', cookies=cookie, files=file)
    obj = res.json()

    print(obj)
    assert obj['status'] == 'success'

    res = requests.get(url+'user/avatar', cookies=cookie)
    obj = res.content
    print(obj)

    assert obj == b'test_img'

def test_delete_photo():
    cookie = login()
    res = requests.post(url+'user/avatar/delete', cookies=cookie)
    obj = res.json()
    print(obj)
    assert obj['status'] == 'success'

    res = requests.get(url+'user/avatar', cookies=cookie)
    assert res.json()['status'] == 'failure'

# @pytest.mark.skip()
def test_change_password():
    cookie = login()
    res = requests.post(url+'user/change_password', cookies=cookie, json={
        "password": NEW_PASSWORD
    })
    obj = res.json()
    print(obj)
    assert obj['status'] == 'success'

    cookie = login(password=NEW_PASSWORD)
    res = requests.get(url+'user', cookies=cookie)
    obj = res.json()
    print(obj)

    assert obj['username'] == user['username']

# @pytest.mark.skip()
def test_delete_account():
    cookie = login(password=NEW_PASSWORD)
    res = requests.post(url+'user/delete_account', cookies=cookie)

    print(res.json())
    assert res.json()['status'] == 'success'

    cookie = login(password=NEW_PASSWORD)
    print(cookie)
    assert cookie['auth']['status'] == 'failure'