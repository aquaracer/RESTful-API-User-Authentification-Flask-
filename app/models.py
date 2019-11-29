from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
import config


engine = create_engine(config.DevelopementConfig.SQLALCHEMY_DATABASE_URI)  # соединяемся с базой PostgresSQL

Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):  # Декларативное создание таблицы, класса и отображения за один раз
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    admin = Column(Boolean)
    expiration_date = Column(String)

    def __init__(self, login, password, admin, expiration_date):
        self.login = login
        self.password = password
        self.admin = admin
        self.expiration_date = expiration_date

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s')>" % (self.login, self.password, self.admin, self.expiration_date)

Base.metadata.create_all(engine)