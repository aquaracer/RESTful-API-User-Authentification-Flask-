import requests
import json
import pytest


@pytest.mark.parametrize("page_number, page_size, expected",
    [('1', '10', True),
     ('3', '1', True),
     ('5', '5', False) ])
def test_users_list(page_number, page_size, expected):
    url = 'http://localhost:5000/users/{0}/{1}'.format(page_number, page_size)
    response = requests.get(url)
    response = response.json()
    assert bool(response['data']) == expected


@pytest.mark.parametrize("login_input, password_input, admin_status_input, expiration_date_input, key_input, expected",
                        [("Kolya", "444", True, "2019/11/29", "data", 'new user has been registered successfully'),
                         ("Olya333", "7772777", False, "2019/11/29", "error", """Exception('This login is busy. Please create another')"""),
                         ("Masha", "7772777", "admin", "2019/11/29", "error", """Exception('invalid format of admin_status')"""),
                         ("Lena", "", True, "2019/11/29", "error", """Exception('invalid format of password. password should contain at least 3 symbols')"""),
                         ])
def test_user_registration(login_input, password_input, admin_status_input, expiration_date_input, key_input, expected):
    url = 'http://localhost:5000/user'
    data = {'login': login_input, 'password': password_input, "admin": admin_status_input, 'expiration_date' : expiration_date_input}
    response = requests.post(url, json=data)
    response = response.json()
    assert response[key_input] == expected


@pytest.mark.parametrize("id_input, type_of_assertion, key_input, expected",
                         [(1, 'logical', 'data', True),
                          (32, 'string', 'error', """Exception('There is no such user in database')""")
                         ])
def test_get_user_id(id_input, type_of_assertion, key_input, expected):
    url = 'http://localhost:5000/user/{}'.format(id_input)
    response = requests.get(url)
    response = response.json()
    if type_of_assertion == 'logical':
        assert bool(response[key_input]) == expected
    else:
        assert response[key_input] == expected


@pytest.mark.parametrize("login_input, password_input, key_input, expected",
    [('222', '333', 'error', """Exception('Access denied. This login does not exist')"""),
     ("Olya333", "7772777", 'data',  "b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjpbMV0sImlzX2FkbWluIjpbZmFsc2VdLCJpc3MiOiJmbGFza19hdXRoX2FwcGxpY2F0aW9uIiwiZXhwIjoxNTc3NTc3NjAwfQ.ZqvZ2Zm2DXH_CMzTJkg0xtBqpr15128-l4B8McGdY_I'"),
     ("Vasya", "111", 'error', """Exception('Access denied. Subscribe expired')""" )                         ])
def test_auth(login_input, password_input, key_input, expected):
    url = 'http://localhost:5000/login'
    data = {'login': login_input, 'password': password_input}
    response = requests.post(url, json=data)
    response = response.json()
    assert response[key_input] == expected



# def test_delete_info():
#     pass
#
# def test_update_info():
#     pass