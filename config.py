from os import getenv


class Config(object):
    SECRET_KEY = 'M<JZ7]6P-r_C0C3hNzY#gbOjY'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:{getenv("DATABASE_PW")}@localhost:3306/qtodo'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GLOBAL_ERROR_CODE = '400 401 403 404 500'
