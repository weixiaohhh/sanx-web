# coding:utf-8
from flask_wtf import Form
from wtforms import StringField, SubmitField,PasswordField,BooleanField,TextAreaField
from wtforms import DateTimeField,SelectField
from wtforms.validators import Required,Email,Length,DataRequired
from models import Category
from flask_pagedown.fields import PageDownField
class LoginForm(Form):

    username = StringField(u'账号',  validators=[Required(), Length(1, 64),Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'记住我')
    login = SubmitField(u'登入')

class PostForm(Form):
    title = StringField(u'标题',validators=[Required()])
    pic_url = StringField(u'图片地址')
    pic_desc = StringField(u'图片描述')
    body = PageDownField(u'内容',validators=[Required()])
    category_id = SelectField(u'文章类别', coerce=int, validators=[Required()])
    tags = StringField(u'标签')
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):  # 定义下拉选择表
        super(PostForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(category.id, category.category_name)
                                 for category in Category.query.order_by(Category.category_name).all()]

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])

class ContactForm(Form):
    name = StringField(u'名字',validators=[Required()])
    email = StringField(u'联系邮箱', validators=[Required(), Length(1, 64), Email()])
    website = StringField(u'网站')
    text = TextAreaField(u'Message',validators=[Required()])
    submit = SubmitField(u'发送')