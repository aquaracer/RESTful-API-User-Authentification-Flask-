from flask import Flask, jsonify, request
from app import controller, models
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import config
from const import HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND


app = Flask(__name__)
app.debug = config.DevelopementConfig.DEBUG


def _process_errors(data:tuple):
    login, password, admin, expiration_date = data
    ret = {}
    if not len(login):
        ret['error'] = "Login should contain at least one symbol"
        print(result)  # выводим лог в stdout
    if len(password) < 3:
        ret['error'] = "Password should contain at least 3 symbols"
        print(result)  # выводим лог в stdout
    if type(admin) is not bool:
        ret['error'] = "Invalid format of admin status"
        print(result)  # выводим лог в stdout
    if len(expiration_date) != 10:
        ret['error'] = "Invalid expiration_date. Please enter expiration_date again in format YYYY/MM/DD"
        print(result)  # выводим лог в stdout
    status_code = HTTP_BAD_REQUEST
    if ret:
        return jsonify(result), status_code

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

   
HTTP_CREATED = 201

@app.route('/user', methods=['POST'])
def user_registration():
    result = {}
    status_code = HTTP_OK
    json = request.get_json() # получаем json из POST запроса
    try:
        login = json['login']
        password = json['password']
        admin = json['admin']
        expiration_date = json['expiration_date']
        error = _process_errors((login, password, admin, expiration_date))
        if error:
            return error
    except KeyError es ex:
        print(ex)
    except Exception as e:
        print(repr(e))  # выводим лог в stdout
    finally:
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


def take_action(func_name, *func_params):
    try:
        report = getattr(controller, func_name)(*func_params)  # пытаемся удалить информацию о пользователе по ID
        result['data'] = report
    except Exception as e:
        result['error'] = repr(e)
        print(result)  # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
    return result, status_code


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
    result, status_code = take_action('delete_user', json.get('user_id'))
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
    result, status_code = take_action('update_user', user_id, password)
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
    result, status_code = take_action('auth', login, password)
    return jsonify(result), status_code


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
