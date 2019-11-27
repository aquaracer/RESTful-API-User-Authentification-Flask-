import requests
import json
import pytest


HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404


def test_auth():
    url = 'http://127.0.0.1:5000/login'
    data = {'login': '222', 'password': '333'}
    response = requests.post(url, json=data)
    response_data = response.json()
    assert response_data['error'] == """Exception('Access denied. This login does not exist')"""
    assert response.status_code == HTTP_NOT_FOUND


