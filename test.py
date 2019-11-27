import requests
import json
import pytest

def test_auth():
    url = 'http://127.0.0.1:5000/login'
    data = {'login': '222', 'password': '333'}
    res = requests.post(url, json=data)
    res_2 = eval(res.text)
    assert res_2['error'] == """Exception('Access denied. This login does not exist')"""



