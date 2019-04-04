from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length, Email, Regexp
from flask_pagedown.fields import PageDownField
from ..models import Role, User

class NameForm(FlaskForm):
    name = StringField('姓名?', validators=[DataRequired()])
    submit = SubmitField('提交')

"""用户级别资料编辑列表"""
class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('提交')

"""管理员级别的资料编辑表单"""
class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    """必须在实例中的choice属性中设置各选项"""
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('提交')

    """初始化"""
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    """如果管理员要改变邮箱地址，那么必须得和数据库中原有的不一致"""
    def validate_email(self, field):
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已经被注册！！")

    def validate_username(self,field):
        if field.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已经被注册！！")

"""这里使用富文本编辑器"""
class PostForm(FlaskForm):
    body = PageDownField("新的想法", validators=[DataRequired()])
    submit = SubmitField("提交")


"""评论的表单"""
class CommentForm(FlaskForm):
    body = StringField("评论")
    submit = SubmitField("提交")
