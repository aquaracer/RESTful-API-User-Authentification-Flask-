from paginate_sqlalchemy import SqlalchemyOrmPage
import jwt
import datetime, calendar
from models import User, session

def list_of_users(current_page:int, current_items_per_page:int): # выдача списка пользователей с пагинацией
    query = session.query(User)  # загружаем всю базу из класса
    page = SqlalchemyOrmPage(query, page=current_page, items_per_page=current_items_per_page)
    list_of_users = page.items
    final_list = []
    for element in list_of_users:
        final_list.append(element.login)
    return final_list

def registration(login:str, password:str): # регистрация пользователя
    new_user_info = User(login, password)
    session.add(new_user_info)
    session.commit()

def get_user_info(current_id:str): #  просмотр данных о пользователе
    query = session.query(User) # загружаем всю базу из класса
    login = []
    login = session.query(User.login).filter(User.id == current_id).first()
    if login == None:
        flag = False
        report = '400'
        return flag, report
    else:
        flag = True
        report = login[0]
        return flag, report

def delete_user(current_id:str): # удаление пользователя
    query = session.query(User)  # загружаем всю базу из класса
    operation_result = session.query(User).filter(User.id == current_id).delete()
    session.commit()
    return operation_result

def update_user(current_id:str, new_password:str): # смена пароля
    query = session.query(User)  # загружаем всю базу из класса
    operation_result = session.query(User).filter(User.id == current_id).update({User.password: new_password})
    session.commit()
    return operation_result

def auth(current_login:str, current_password:str): # авторизация с выдачей токена
    query = session.query(User)  # загружаем всю базу из класса
    password = session.query(User.password).filter(User.login == current_login).first()
    if password == None:
        flag = False
        report = "400"
        return flag, report
    password = password[0]
    if current_password != password:
        flag = False
        report = "400"
        return flag, report
    else:
        user_id = session.query(User.id).filter(User.login == current_login).first()
        user_id = user_id[0]
        exp_date = datetime.datetime(2019, 12, 14, 0, 0, 0)
        unix_exp_date = calendar.timegm(exp_date.timetuple())
        payload = {"user_id": user_id, "iss": "flask_auth_application", "exp": unix_exp_date}
        token = jwt.encode(payload, '645645', algorithm='HS256')
        flag = True
        return flag, token
