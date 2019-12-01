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
        
        
@pytest.fixture(autouse=True)
def clean_db():
    yield
    with connect() as session:  # очищаем таблицу
        operation_result = session.query(User).delete()
        
        
@pytest.fixture
def user(client):
    def wrapper(data):
        create_user_url = 'http://localhost:5000/user'
        response = client.post(create_user_url, data=data)
        return response.json()
    return wrapper
    


@pytest.mark.parametrize("page_number, page_size, expected",
    [('1', '10', True),
     ('3', '1', True),
     ('5', '5', False) ])
def test_users_list(page_number, page_size, expected, user, client):
    users = [
        {"login": "user_1", "password": "111", "admin" : False, "expiration_date" : "2019/12/29"},
        {"login": "user_2", "password": "222", "admin": False, "expiration_date": "2019/12/29"},
        {"login": "user_3", "password": "333", "admin": False, "expiration_date": "2019/12/29"},
        {"login": "user_4", "password": "444", "admin": False, "expiration_date": "2019/12/29"}
    ]
    [user(user_data) for user_data in users]

    user_list_url = 'http://localhost:5000/users/{0}/{1}'.format(page_number, page_size)
    response = client.get(user_list_url)
    response = response.json()
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
def test_user_registration_negative(JSON_input, expected, user):
     user({'login': 'user_1', 'password': '111', "admin": False, 'expiration_date' : '2019/12/31'})
     response = user(JSON_input)
     assert response['error'] == expected


def test_user_registration_positive(user):
    response = user({'login': 'user_1', 'password': '111', "admin": False, 'expiration_date': '2019/12/31'})
    assert response['data'] == 'new user has been registered successfully'


def test_get_user_id_positive (user):
    user({"login": "user_2", "password": "111", "admin": False, "expiration_date": '2019/12/31'})
    with connect() as session: # получаем ID по логину
        id = session.query(User.id).filter(User.login == "user_2").first()
    get_user_url = 'http://localhost:5000/user/{}'.format(id[0])
    response = requests.get(get_user_url)
    response = response.json()
    assert response['data'][0] == 'user_2'


def test_get_user_id_negative (user):
    user({"login": "user_2", "password": "111", "admin": False, "expiration_date": '2019/12/31'})
    with connect() as session: # получаем ID по логину
        id = session.query(User.id).filter(User.login == "user_2").first()
    invalid_id = int(id[0]) + 1
    get_user_url = 'http://localhost:5000/user/{}'.format(invalid_id)
    response = requests.get(get_user_url)
    response = response.json()
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
    delete_user_url = 'http://localhost:5000/user'
    response = requests.delete(delete_user_url, json=json_input)
    response = response.json()
    assert response['error'] == expected


def test_delete_info_positive(user):
    user({"login": "user_2", "password": "111", "admin": False, "expiration_date": '2019/12/31'})
    with connect() as session:
        id = session.query(User.id).filter(User.login == "user_2").first()

    delete_user_url = 'http://localhost:5000/user'
    json = {'user_id': id[0]}
    response = requests.delete(delete_user_url, json=json)
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
    update_user_password_url = 'http://localhost:5000/user'
    response = requests.patch(update_user_password_url, json=json_input)
    response = response.json()
    assert response['error'] == expected


def test_update_info_positive(user):
    user({"login": "user_2", "password": "111", "admin": False, "expiration_date": '2019/12/31'})
    with connect() as session:
        id = session.query(User.id).filter(User.login == "user_2").first()
    update_user_password_url = 'http://localhost:5000/user'
    data = {"user_id": id[0], "password": '222'}
    response = requests.patch(update_user_password_url, json=data)
    response = response.json()
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
def test_auth_negative(JSON_input, expected, user):
    user({"login": "user_1", "password": "111", "admin": False, "expiration_date": '2019/11/30'})
    get_user_login_url = 'http://localhost:5000/login'
    response = requests.post(get_user_login_url, json=JSON_input)
    response = response.json()
    assert response['error'] == expected


def test_auth_positive(user):
    user({"login": "user_1", "password": "111", "admin": False, "expiration_date": '2019/12/31'})
    get_user_login_url = 'http://localhost:5000/login'
    data = {'login': 'user_1', 'password': '111'}
    response = requests.post(get_user_login_url, json=data)
    response = response.json()
    assert bool(response['data']) is True



