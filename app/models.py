# -*- coding: utf-8 -*-

from app import db,app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from . import login_manager
from markdown import markdown
import bleach

class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

import sys
# whooshalchemy 只支持Python3 版本以下
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemyplus as whooshalchemyplus
from jieba.analyse import ChineseAnalyzer


class Post(db.Model):
    #文章对象,标签是多对多
    __tablename__ = 'post'
    __searchable__ = ['title','body']
    __analyzer__ = ChineseAnalyzer()

    id = db.Column(db.Integer, primary_key=True)
    # 与标签形成多对多的关系
    tags = db.relationship('Tag', secondary=tags,backref=db.backref('posts', lazy='dynamic'))
    tags_name = db.Column(db.String(64))
    pic_url = db.Column(db.UnicodeText)
    pic_desc = db.Column(db.UnicodeText)
    title = db.Column(db.String(200), unique=True)
    body = db.Column(db.UnicodeText)
    body_html = db.Column(db.UnicodeText)
    pub_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow)
    # 与分类形成 多对一的关系
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # 类型id
    category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'), lazy='select')

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Post %r>' % self.title

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'ul','pre', 'strong', 'ul','img',
                        'h1', 'h2', 'h3', 'p']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src'],
        }

        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attrs, strip=True))
db.event.listen(Post.body, 'set', Post.on_changed_body)

if enable_search:
    whooshalchemyplus.whoosh_index(app, Post)


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '%s' % self.name

# # 定义标签查询函数
# class TagQuery(BaseQuery):
#     def getall(self):
#         return self.all()
#
#     def gettag_id(self, id):
#         return self.get(id)

class Category(db.Model):
    __tablename__ = 'category'  # 表名
  #  query_class = CategoryQuery  # 指定的查询类名
    id = db.Column(db.Integer, primary_key=True)  # id
    category_name = db.Column(db.String(200), unique=True)  # name

    # 下面的内容可以自由选择

    def __init__(self,category_name):
        self.category_name = category_name

    @staticmethod
    def insert_categorys():
        categorylist = [u"Python", u"Web", u"Linux", u"编辑器/IDE", u"数据库", u"前端", u"其他"]
        for category in categorylist:
            postcategory = Category.query.filter_by(category_name=category).first()
            if postcategory is None:
                postcategory = Category(category_name=category)
                db.session.add(postcategory)
        db.session.commit()
    def __repr__(self):
        return '<category name="" %r="">' % self.category_name

# 定义分类查询函数
# class CategoryQuery(BaseQuery):
#     def getall(self):
#         return self.all()
#
#     def getcategory_id(self, id):
#         return self.get(id)




