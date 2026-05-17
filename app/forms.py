from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField("用户名", validators=[
        DataRequired(message="用户名不能为空"),
        Length(min=3, max=20, message="用户名长度为3-20个字符")
    ])
    password = PasswordField("密码", validators=[
        DataRequired(message="密码不能为空")
    ])
    submit = SubmitField("登录")


class RecordForm(FlaskForm):
    """业务记录表单"""
    title = StringField("标题", validators=[
        DataRequired(message="标题不能为空"),
        Length(max=200, message="标题最多200个字符")
    ])
    content = TextAreaField("内容", validators=[
        Length(max=5000, message="内容最多5000个字符")
    ])
    submit = SubmitField("保存")


class RegisterForm(FlaskForm):
    """注册表单（管理员添加用户）"""
    username = StringField("用户名", validators=[
        DataRequired(message="用户名不能为空"),
        Length(min=3, max=20, message="用户名长度为3-20个字符")
    ])
    password = PasswordField("密码", validators=[
        DataRequired(message="密码不能为空"),
        Length(min=6, message="密码至少6个字符")
    ])
    password_confirm = PasswordField("确认密码", validators=[
        DataRequired(message="请确认密码"),
        EqualTo("password", message="两次密码不一致")
    ])
    submit = SubmitField("注册")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("用户名已存在")