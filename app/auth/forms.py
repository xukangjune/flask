from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


"""登录用的表单"""
class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


"""注册用的表单"""
class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被使用！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用！')


"""改密码用的表单"""
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧的密码', validators=[DataRequired()])
    password = PasswordField('新的密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认密码',
                              validators=[DataRequired()])
    submit = SubmitField('修改密码')


"""忘记密码时，填写账号的表单"""
class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重设密码')


"""重设密码用的表单"""
class PasswordResetForm(FlaskForm):
    password = PasswordField('新的密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('重设密码')


"""重设邮箱的表单"""
class ChangeEmailForm(FlaskForm):
    email = StringField('新的邮箱', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('更改邮箱地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
