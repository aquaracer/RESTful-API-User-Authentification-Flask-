from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql+psycopg2://user_2:222@localhost/base_users')  # соединяемся с базой PostgresSQL
Session = sessionmaker(bind=engine)

Base = declarative_base()

class User(Base):  # Декларативное создание таблицы, класса и отображения за один раз
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.login, self.password)

Base.metadata.create_all(engine)