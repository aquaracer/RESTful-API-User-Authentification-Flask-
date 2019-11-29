from paginate_sqlalchemy import SqlalchemyOrmPage
import jwt
import datetime, calendar
from app.models import User, Session
import bcrypt
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


def list_of_users(current_page:int, current_items_per_page:int): # выдача списка пользователей с пагинацией
    with connect() as session:
        query = session.query(User)  # загружаем всю базу из класса
    page = SqlalchemyOrmPage(query, page=current_page, items_per_page=current_items_per_page)
    list_of_users = page.items
    return [element.login for element in list_of_users]


def registration(login:str, password:str, admin:bool, expiration_date:str): # регистрация пользователя
    with connect() as session:
        existed_user = session.query(User.login).filter(User.login == login).first() # проверяем есть ли уже в базе пользователь с заданным логином
    if existed_user != None:
        raise Exception('This login is busy. Please create another')
    if type(admin) is not bool:
        raise Exception('invalid format of admin_status')
    if type(password) is not str:
        raise Exception('invalid format of password')
    if len(password) < 3:
        raise Exception('invalid format of password. password should contain at least 3 symbols')
    password = password.encode('utf-8') # переводим в кодировку utf-8 (необходимо для хеширования)
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()) # хешируем пароль
    hashed_password = hashed_password.decode('utf-8')
    try:
        expiration_date = expiration_date.split('/')
        expiration_date = str(datetime.date(int(expiration_date[0]), int(expiration_date[1]), int(expiration_date[2])))
    except Exception as e:
        print('invalid format of Expiration Date')
        print(repr(e))
    new_user_info = User(login, hashed_password, admin, expiration_date)
    with connect() as session:
        session.add(new_user_info) # добавляем в базу


def get_user_info(current_id:int): #  просмотр данных о пользователе
    with connect() as session:
        login = session.query(User.login).filter(User.id == current_id).first()
    if login == None:
        raise Exception('There is no such user in database')
    else:
        return login


def delete_user(current_id:str): # удаление пользователя
    with connect() as session:
        operation_result = session.query(User).filter(User.id == current_id).delete()
    if operation_result == 0:
        raise Exception('There is no such user in database')
    else:
        report = 'user has been deleted'
        return report


def update_user(current_id:str, new_password:str): # смена пароля
    new_password = new_password.encode('utf-8')  # переводим в кодировку utf-8 (необходимо для хеширования)
    hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())  # хешируем пароль
    hashed_password = hashed_password.decode('utf-8')
    with connect() as session:
        password = session.query(User.password).filter(User.id == current_id).first() # ищем пароль по ID
    if password == None:
        raise Exception('There is no such user in database')
    else:
        with connect() as session:
            session.query(User).filter(User.id == current_id).update({ User.password: hashed_password})  # обновляем пароль
        report = 'password has been updated'
        return report


def auth(current_login:str, current_password:str): # авторизация с выдачей токена
    with connect() as session:
        password = session.query(User.password).filter(User.login == current_login).first() # проверяем есть ли пользователь с заданным логином. если да получаем хеш пароля данного пользователя
    if password == None:
        raise Exception('Access denied. This login does not exist')
    else:
        expiration_date = session.query(User.expiration_date).filter(User.login == current_login).first()
        expiration_date = expiration_date[0]
        print('exp_date:', expiration_date)
        current_date = str(datetime.date.today())
        print('current_date:', expiration_date)
        print(current_date)
        password = password[0]
        password = password.encode('utf-8') # переводим в кодировку utf-8
        current_password = current_password.encode('utf-8')  # переводим в кодировку utf-8
        if not bcrypt.checkpw(current_password, password): # сверяем введенный пароль и пароль из базы
            raise Exception('Access denied. Invalid password')
        elif current_date > expiration_date:
            raise Exception('Access denied. Subscribe expired')
        else:
            with connect() as session:
                user_id = session.query(User.id).filter(User.login == current_login).first()
                is_admin = session.query(User.admin).filter(User.login == current_login).first()

            expiration_date = expiration_date.split('-')

            exp_date = datetime.datetime(int(expiration_date[0]), int(expiration_date[1]), int(expiration_date[2]), 0, 0, 0)
            unix_exp_date = calendar.timegm(exp_date.timetuple())
            payload = {"user_id": user_id, "is_admin": is_admin, "iss": "flask_auth_application", "exp": unix_exp_date}
            token = jwt.encode(payload, '645645', algorithm='HS256')
            token = str(token)
            return token

