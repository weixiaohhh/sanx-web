# -*- coding: utf-8 -*-
# @Author: wex
# @Date:   2016-12-23 16:12:30
# @Last Modified by:   wex
# @Last Modified time: 2016-12-23 16:12:36
from app import app,db,cache
from flask import render_template,url_for,redirect,request,g
from flask_login import login_user,login_required,logout_user,current_user
from models import User,Post,Tag,Category,tags
from forms import LoginForm,PostForm,SearchForm,ContactForm
from flask import flash,current_app
from datetime import datetime


@app.route('/')
@cache.cached(timeout=300)
def index():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.modified_date.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    all_tags = Tag.query.all()
    tags = set([tag.name for tag in all_tags])
    categories = Category.query.all()

    return render_template('index.html',
                           posts=posts,
                           tags=tags,
                           categories=categories,
                           form=form,
                           pagination=pagination,
                           )

# 图片区
@app.before_request
@cache.cached(timeout=300)
def before_request():
    g.pic_contents = [post for post in Post.query.order_by(Post.modified_date.desc()) if post.pic_url]

@app.route('/about')
def about():

    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('admin.index'))
        flash(u'不准捣乱')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# 错误模板
# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
#
# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('500.html'), 500


@app.route('/writepost', methods=['GET', 'POST'])
@login_required
def writepost():
    form = PostForm()
    if form.validate_on_submit():
        taglist = []
        tagtmp = form.tags.data.split(',')
        for tag in tagtmp:
            taglist.append(Tag(name=tag))
        post = Post(
            title = form.title.data,
            pic_url= form.pic_url.data,
            pic_desc = form.pic_desc.data,
            body = form.body.data,
            category_id = form.category_id.data,
            tags_name=form.tags.data,
            tags = taglist,
        )
        db.session.add(post)
        db.session.commit()
        flash(u'博客编写成功')
        return redirect(url_for('index'))
    return render_template('edit.html', form=form,)

# 文章修改
@app.route('/modifypost/<int:id>', methods=['GET', 'POST'])
@login_required
def modifypost(id):
    post = Post.query.get_or_404(id)

    form = PostForm()


    if form.validate_on_submit():

        taglist = []
        tagtmp = form.tags.data.split(',')
        for tag in tagtmp:
            taglist.append(Tag(name=tag))
        post.title = form.title.data
        post.body = form.body.data
        post.tags=taglist
        post.category_id = form.category_id.data
        post.modified_date = datetime.utcnow()

        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('index'))
    form.title.data= post.title
    form.body.data = post.body
    tagtmp = [str(tag) for tag in post.tags]
    form.tags.data = ','.join(tagtmp)
    form.category_id.data = post.category_id

    return render_template('edit.html', form=form, )


@app.route('/post/<int:id>')
@cache.cached(timeout=300)
def post(id):
    post = Post.query.get_or_404(id)


    return render_template('post.html',post=post)

@app.route('/category/<string:name>')
def category_post(name):
    category= Category.query.filter_by(category_name=name).first()
    posts = Post.query.filter_by(category_id=category.id)
    return render_template('change_post.html',posts=posts)

@app.route('/tag/<string:name>')
def tag_post(name):
    tag = Tag.query.filter_by(name=name).first()
    posts = []
    postlist = Post.query.all()
    for post in postlist:
        if tag in post.tags:
            posts.append(post)
    return render_template('change_post.html',posts=posts)

# 搜索
MAX_SEARCH_RESULTS = 50
@app.route('/search', methods = ['POST'])
@cache.cached(timeout=300)
def search():
    form = SearchForm()
    if form.validate_on_submit():

        info = form.search.data
        results = Post.query.whoosh_search(info, MAX_SEARCH_RESULTS,like=True).all()
        return render_template('search_results.html',
                               info=info,
                               results=results)
    flash(u'输入错误')
    return redirect(url_for('index'))

# 邮件配置
from flask_mail import Message
from app import mail

from threading import Thread
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
def send_email(to, subject, template, **kwargs):
    msg = Message(subject,sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)

    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

@app.route('/contact',methods=['GET', 'POST'])
@cache.cached(timeout=300)
def contact():
    form = ContactForm()
    if form.validate_on_submit():

        name = form.name.data
        email = form.email.data
        website = form.website.data
        message = form.website.data
        send_email(app.config['FLASKY_ADMIN'], 'New Friend',
                    'mail/New_contact', name=name,email=email,website=website,message=message)
        flash(u'发送成功')
        return redirect(url_for('index'))


    return render_template('contact.html',form=form)

# flask-admin 配置
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView

from flask_admin import BaseView,expose,AdminIndexView,Admin

import os.path as op

# 身份认证
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin.html')

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))
admin = Admin(app, u'后台管理', template_mode='bootstrap3', index_view=MyAdminIndexView())


# 文章编辑
class WriteView(BaseView):
    #这里类似于app.route()，处理url请求
    @expose('/')
    def index(self):
        return redirect(url_for('writepost'))

admin.add_view(WriteView(name=u'题写文章',endpoint='writepost'))



# 文章视图模型
class PostView(ModelView):
    page_size = 50  # the number of entries to display on the list view
    can_create = False

    # 登录验证
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

admin.add_view(PostView(Post, db.session))


# 文件上传 配置

class FileAdminView(FileAdmin):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

path = op.join(op.dirname(__file__), 'static')
admin.add_view(FileAdminView(path, '/static/', name='Static Files'))