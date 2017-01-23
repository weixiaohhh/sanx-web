# coding:utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import  Bootstrap
from flask_pagedown import  PageDown
from flask_mail import Mail
from flask_cache import Cache





app = Flask(__name__)
app.config.from_object('config')

if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
    from flask_sslify import SSLify
    sslify = SSLify(app)



# 登录配置
login_manager = LoginManager(app)
login_manager.login_message = u"请先登录"
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

# 初始化
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
pagedown = PageDown(app)
mail = Mail(app)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

from app import models,views
