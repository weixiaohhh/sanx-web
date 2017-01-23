# -*- coding: utf-8 -*-


import os
# SQLALCHEMY_DATABASE_URI ="mysql://root:1234@localhost:3306/flaskdb?charset=utf8mb4"
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI =os.environ.get('DATABASE_URL') or \
                          'sqlite:///' + os.path.join(basedir, 'sanx.sqlite')

SQLALCHEMY_COMMIT_ON_TEARDOWN= True
SECRET_KEY = 'hard to guess string'
FLASKY_POSTS_PER_PAGE = 5

SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))



# WHOOSH_BASE = 'C:\\Documents and Settings\\All Users\\Application Data\\MySQL\MySQL Server 5.7\\Data\\flaskdb'
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

# email
import os

MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 25
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
FLASKY_MAIL_SENDER = 'Admin <3060106630@qq.com>'
FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

USER_NAME = os.environ.get('USER_NAME')
USER_PASSWORD = os.environ.get('USER_PASSWORD')