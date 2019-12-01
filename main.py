from flask import Flask, jsonify, request
from app import controller, models
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import config
from const import HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND


app = Flask(__name__)
app.debug = config.DevelopementConfig.DEBUG


@app.route('/')
def index():
    return 'Welcome to User Authorization Page!'


@app.route('/users/<int:page_number>/<int:page_size>', methods=['GET'])
def users_list(page_number:int, page_size:int):
    result = {}
    status_code = HTTP_OK
    try:
        final_list = controller.list_of_users(page_number, page_size)
        result['data'] = final_list
    except Exception as e:
        result['error']=repr(e)
        print(result) # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
    return jsonify(result), status_code


@app.route('/user', methods=['POST'])
def user_registration():
    result = {}
    status_code = HTTP_OK
    json = request.get_json() # получаем json из POST запроса
    try:
        login = json['login']
        print('login ok')
        password = json['password']
        print('password ok')
        admin = json['admin']
        print('admin ok')
        expiration_date = json['expiration_date']
        print('exp ok')
        if len(login) < 1:
            result['error'] = "Login should contain at least one symbol"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
        if len(login) < 3:
            result['error'] = "Password should contain at least 3 symbols"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
        if type(admin) is not bool:
            result['error'] = "Invalid format of admin status"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
        if len(expiration_date) != 10:
            result['error'] = "Invalid expiration_date. Please enter expiration_date again in format YYYY/MM/DD"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
    except Exception as e:
        print(repr(e))  # выводим лог в stdout
        result['error'] = "JSON does not contain required data"
        status_code = HTTP_BAD_REQUEST
        return jsonify(result), status_code
    try:
        controller.registration(login, password, admin, expiration_date) # пытаемся зарегистрировать пользователя
        result['data'] = 'new user has been registered successfully'
    except Exception as e:
        result['error'] = repr(e)
        print(result) # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
    return jsonify(result), status_code


@app.route('/user/<int:id>', methods=['GET'])
def get_user_id(id:int):
    result = {}
    status_code = HTTP_OK
    try:
        login = controller.get_user_info(id)  # пытаемся получить информацию о пользователе по ID
        result['data'] = login
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        status_code = HTTP_NOT_FOUND
    return jsonify(result), status_code


@app.route('/user', methods=['DELETE'])
def delete_info():
    result = {}
    status_code = HTTP_OK
    json = request.get_json(force=True)
    try:
        user_id = json['user_id']
        if len(str(user_id)) < 1:
            result['error'] = "user_id should contain at least one symbol"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
    except Exception as e:
        result['error'] = "JSON does not contain field user_id"
        print(repr(e))  # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
        return jsonify(result), status_code
    try:
        report = controller.delete_user(user_id)  # пытаемся удалить информацию о пользователе по ID
        result['data'] = report
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
    return jsonify(result), status_code


@app.route('/user', methods=['PATCH'])
def update_info():
    result = {}
    status_code = HTTP_OK
    json = request.get_json(force=True)
    try:
        user_id = json['user_id']
        password = json['password']
        if len(str(user_id)) < 1:
            result['error'] = "User_id should contain at least one symbol"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
        if len(str(password)) < 3:
            result['error'] = "Password should contain at least 3 symbols"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
    except Exception as e:
        result['error'] = "JSON does not contain required data"
        print(repr(e))  # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
        return jsonify(result), status_code
    try:
        report = controller.update_user(user_id, password)  # пытаемся удалить информацию о пользователе по ID
        result['data'] = report
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
    return jsonify(result), status_code


@app.route('/login', methods=['POST'])
def user_auth():
    result = {}
    status_code = HTTP_OK
    json = request.get_json(force=True)
    try:
        login = json['login']
        password = json['password']
    except Exception as e:
        result['error'] = "JSON does not contain required data"
        print(repr(e))  # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
        return jsonify(result), status_code
    try:
        token = controller.auth(login, password)  # пытаемся пройти аутентификацию и получить JWT токен
        result['data'] = str(token)
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        status_code = HTTP_NOT_FOUND
    return jsonify(result), status_code


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()