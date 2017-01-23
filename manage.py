# -*- coding: utf-8 -*-
# @Author: wex
# @Date:   2016-12-23 10:14:53
# @Last Modified by:   wex
# @Last Modified time: 2016-12-23 16:11:38
from app import app,db
from app.models import User,Post,Category,Tag,tags
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand


manager = Manager(app)
# 创建数据库迁移
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# 创建表
@manager.command
def create_table():
    db.drop_all()
    db.create_all()
    # 添加分类
    Category.insert_categorys()
    u = User(username='admin@example.com',password='123')
    db.session.add(u)
    db.session.commit()

@manager.command
def deploy():

    """Run deployment tasks."""

    from flask_migrate import upgrade
    # 把数据库迁移到最新修订版本
    upgrade()

@manager.command
def create_user():


    Category.insert_categorys()
    u = User(username=app.config['USER_NAME'], password=app.config['USER_PASSWORD'])
    db.session.add(u)
    db.session.commit()


def make_shell_context():
    return dict(app=app, db=db, User=User, Post=Post,Category=Category,Tag=Tag,tags=tags)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()