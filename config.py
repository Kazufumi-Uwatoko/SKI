import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
class DevelopmentConfig:
    # Turn on debug mode in Flask
    DEBUG = True
    # Set SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/SKI?charset=utf8'.format(**{
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', ''),
        'host': os.environ.get('DB_HOST', 'localhost'),
    })
    SQLALCHEMY_TRACK_MODIFICATIONS = False      #  Good luck charm
    SQLALCHEMY_ECHO = False                     #  Good luck charm
Config = DevelopmentConfig