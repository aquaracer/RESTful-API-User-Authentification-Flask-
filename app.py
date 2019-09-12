from flask import Flask, jsonify, request
import controller

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Welcome to User Authorization Page!'

@app.route('/users/<page_number>/<page_size>', methods=['GET'])
def users_list(page_number:str, page_size:str):
    page_number = int(page_number)
    page_size = int(page_size)
    final_list = controller.list_of_users(page_number, page_size)
    return jsonify({'list of users': final_list})

@app.route('/user', methods=['POST'])
def user_registration():
    json = request.get_json()
    login = json['login']
    password = json['password']
    controller.registration(login, password)
    return "200"

@app.route('/user/<id>', methods=['GET'])
def get_user_id(id:str):
    flag, report = controller.get_user_info(id)
    if flag:
        return report
    else:
        return "400"

@app.route('/user', methods=['DELETE'])
def delete_info():
    json = request.get_json(force=True)
    user_id = json['user_id']
    operation_result = controller.delete_user(user_id)
    if operation_result == 1:
        return "200"
    else:
        return "400"

@app.route('/user', methods=['PATCH'])
def update_info():
    json = request.get_json(force=True)
    user_id = json['user_id']
    password = json['password']
    operation_result = controller.update_user(user_id, password)
    if operation_result == 1:
        return "200"
    else:
        return "400"

@app.route('/login', methods=['POST'])
def user_auth():
    json = request.get_json(force=True)
    login = json['login']
    password = json['password']
    flag, report = controller.auth(login, password)
    if flag:
        return jsonify({'token': str(report)})
    else:
        return report

if __name__ == '__main__':
    app.run()
