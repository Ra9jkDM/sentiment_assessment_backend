import pytest
from tests.test_environment import recreate, url, user
from tests.z_user_test import login
import requests

@pytest.mark.parametrize('text', [(' '), ('some прошло'), ('?'), ('./.321'), 
                        ('Hey'), ('Привет'), ('Когда же мой рабочий день кончится?')])
def test_lstm_test(text):
    cookie = login()
    res = requests.post(url+'ml/lstm', cookies=cookie, 
                        json={'text': text})
    obj = res.json()
    print(obj)

    assert obj['status'] == 'success'
    assert 'text' in obj
    assert 'positive' in obj

def test_lstm_table():
    cookie = login()
    res = requests.post(url+'ml/lstm/table', cookies=cookie, 
                        files={'file': open('tests/test_data/test_ml_3.xlsx', 'rb')})
    obj = res.json()