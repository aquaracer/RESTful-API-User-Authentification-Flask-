from const import HTTP_OK
import requests
import json
import pytest
from app.models import User, Session
from contextlib import contextmanager


@contextmanager
def connect():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.mark.parametrize("page_number, page_size, expected",
    [('1', '10', True),
     ('3', '1', True),
     ('5', '5', False) ])
def test_users_list(page_number, page_size, expected):
    url = 'http://localhost:5000/user'
    data = {"login": "user_1", "password": "111",
            "admin" : False, "expiration_date" : "2019/12/29"  }
    response = requests.post(url, json=data)
    data = {"login": "user_2", "password": "222",
            "admin": False, "expiration_date": "2019/12/29"}
    response = requests.post(url, json=data)
    data = {"login": "user_3", "password": "333",
            "admin": False, "expiration_date": "2019/12/29"}
    response = requests.post(url, json=data)
    data = {"login": "user_4", "password": "444",
            "admin": False, "expiration_date": "2019/12/29"}
    response = requests.post(url, json=data) # вносим тестовые данные в таблицу

    url = 'http://localhost:5000/users/{0}/{1}'.format(page_number, page_size)
    response = requests.get(url)
    response = response.json()
    with connect() as session:  # очищаем таблицу
        operation_result = session.query(User).delete()
    assert bool(response['data']) == expected


@pytest.mark.parametrize(
    "JSON_input, expected",
    [
        ('{}', "JSON does not contain required data"),
        ({ 'password': '111', "admin": False, 'expiration_date' : '2019/12/31'}, "JSON does not contain required data"),
        ({'login': 'user_1', "admin": False, 'expiration_date' : '2019/12/31'}, "JSON does not contain required data" ),
        ({'login': 'user_1', 'password': '111', 'expiration_date' : '2019/12/31'}, "JSON does not contain required data"),
        ({'login': 'user_1', 'password': '111', "admin": False}, "JSON does not contain required data"),
        ({'login': 'user_1', 'password': '111', "admin": '111', 'expiration_date': '2019/12/31'}, "Invalid format of admin status"),
        ({'login': 'user_1', 'password': '111', "admin": False, 'expiration_date': '20191231'},
         "Invalid expiration_date. Please enter expiration_date again in format YYYY/MM/DD"),
        ({'login': 'user_1', 'password': '111', "admin": False, 'expiration_date': '2019/12/31'},
         """Exception('This login is busy. Please create another')""")
    ]
)
def test_user_registration_negative(JSON_input, expected):
     url = 'http://localhost:5000/user'
     first_data = {'login': 'user_1', 'password': '111', "admin": False, 'expiration_date' : '2019/12/31'}
     requests.post(url, json=first_data)
     response = requests.post(url, json=JSON_input)
     response = response.json()
     with connect() as session:  # очищаем таблицу
         operation_result = session.query(User).delete()
     assert response['error'] == expected


def test_user_registration_positive():
    url = 'http://localhost:5000/user'
    data = {'login': 'user_1', 'password': '111', "admin": False, 'expiration_date': '2019/12/31'}
    response = requests.post(url, json=data)
    response = response.json()
    with connect() as session:  # очищаем таблицу
        operation_result = session.query(User).delete()
    assert response['data'] == 'new user has been registered successfully'


def test_get_user_id_positive ():
    url = 'http://localhost:5000/user'
    first_data = {"login": "user_2", "password": "111", "admin": False, "expiration_date": '2019/12/31'}
    requests.post(url, json=first_data)  # регистрируем юзера
    with connect() as session: # получаем ID по логину
        id = session.query(User.id).filter(User.login == "user_2").first()
    url = 'http://localhost:5000/user/{}'.format(id[0])
    response = requests.get(url)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['data'][0] == 'user_2'


def test_get_user_id_negative ():
    url = 'http://localhost:5000/user'
    first_data = {"login": "user_2", "password": "111", "admin": False, "expiration_date": '2019/12/31'}
    requests.post(url, json=first_data)  # регистрируем юзера
    with connect() as session: # получаем ID по логину
        id = session.query(User.id).filter(User.login == "user_2").first()
    id = int(id[0]) + 1
    url = 'http://localhost:5000/user/{}'.format(id)
    response = requests.get(url)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['error'] == """Exception('There is no such user in database')"""

@pytest.mark.parametrize(
    "json_input, expected",
    [
        ({}, "JSON does not contain field user_id" ),
        ({"user_id": ''}, "user_id should contain at least one symbol"),
        ({"user_id": '111222'}, """Exception('There is no such user in database')""" )
    ]
)
def test_delete_info_negative(json_input, expected):
    url = 'http://localhost:5000/user'
    response = requests.delete(url, json=json_input)
    response = response.json()
    assert response['error'] == expected

def test_delete_info_positive():
    url = 'http://localhost:5000/user'
    first_data = {"login": "user_2", "password": "111", "admin": False, "expiration_date": '2019/12/31'}
    requests.post(url, json=first_data)  # регистрируем юзера
    with connect() as session:
        id = session.query(User.id).filter(User.login == "user_2").first()

    url = 'http://localhost:5000/user'
    json = {'user_id': id[0]}
    response = requests.delete(url, json=json)
    response = response.json()
    assert response['data'] == 'user has been deleted'



@pytest.mark.parametrize(
     "json_input, expected",
    [
        ({}, "JSON does not contain required data" ),
        ({"user_id": '35'}, "JSON does not contain required data" ),
        ({"password": '35'}, "JSON does not contain required data" ),
        ({"user_id": "", "password": '35'}, "User_id should contain at least one symbol" ),
        ({"user_id": '35', "password": ''}, "Password should contain at least 3 symbols" ),
        ({"user_id": '351', "password": '3555'}, """Exception('There is no such user in database')""" )

    ]
)
def test_update_info_negative(json_input, expected):
    url = 'http://localhost:5000/user'
    response = requests.patch(url, json=json_input)
    response = response.json()
    assert response['error'] == expected


def test_update_info_positive():
    url = 'http://localhost:5000/user'
    first_data = {"login": "user_2", "password": "111", "admin": False, "expiration_date": '2019/12/31'}
    requests.post(url, json=first_data)  # регистрируем юзера
    with connect() as session:
        id = session.query(User.id).filter(User.login == "user_2").first()
    url = 'http://localhost:5000/user'
    data = {"user_id": id[0], "password": '222'}
    response = requests.patch(url, json=data)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['data'] == 'password has been updated'


@pytest.mark.parametrize(
    "JSON_input, expected",
    [
        ('{}', "JSON does not contain required data"),
        ({ 'password': '111'}, "JSON does not contain required data"),
        ({'login': 'user_1'}, "JSON does not contain required data" ),
        ({'login': 'user_2', 'password': '222'}, """Exception('Access denied. This login does not exist')"""),
        ({'login': 'user_1', 'password': '112'}, """Exception('Access denied. Invalid password')"""),
        ({'login': 'user_1', 'password': '111'}, """Exception('Access denied. Subscribe expired')""")
    ]
)
def test_auth_negative(JSON_input, expected):
    url = 'http://localhost:5000/user'
    first_data = {"login": "user_1", "password": "111", "admin": False, "expiration_date": '2019/11/30'}
    requests.post(url, json=first_data)  # регистрируем юзера

    url = 'http://localhost:5000/login'
    response = requests.post(url, json=JSON_input)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['error'] == expected


def test_auth_positive():
    url = 'http://localhost:5000/user'
    first_data = {"login": "user_1", "password": "111", "admin": False, "expiration_date": '2019/12/31'}
    requests.post(url, json=first_data)  # регистрируем юзера

    url = 'http://localhost:5000/login'
    data = {'login': 'user_1', 'password': '111'}
    response = requests.post(url, json=data)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert bool(response['data']) is True



