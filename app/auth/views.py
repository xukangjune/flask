from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetForm, \
    PasswordResetRequestForm, ChangeNameForm


"""每接收一次request请求后都会优先进入此视图函数（auth.before_app_request的作用）"""
@auth.before_app_request
def before_request():
    """如果用户登录了，但是没有确认账户，而且请求的端点不在认证蓝本中。
    以上都满足的话，就会到auth.confirmed的视图函数中。更新已登录
    用户的访问时间。"""
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


"""登录，填写表单 """
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    """表单提交来验证"""
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            """next是登录后应该跳转的页面，如果没有就到main.index"""
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


"""注册新用户，在User中不用写db.session.add()等函数的，因为最后在这里会将数据提交给给数据库"""
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        """发送后跳转auth.login视图函数"""
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


"""login_required保护路由，要求你必须是在登陆状态才能访问这个页面"""
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


"""同样，必须在登录条件下进行"""
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            """如果密码验证合格，那么就可以改密码了，最后提交到数据库"""
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

@auth.route('/change-name', methods=['GET', 'POST'])
@login_required
def change_name():
    form = ChangeNameForm()
    if form.validate_on_submit():
        current_user.username = form.new_name.data
        db.session.add(current_user)
        db.session.commit()
        flash("你的用户名已修改！")
        return redirect(url_for('main.index'))
    return render_template("auth/change_name.html", form=form)



"""密码重设请求"""
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """如果当前用户已经登录了，说明不用重设密码了"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            """令牌"""
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
            flash('An email with instructions to reset your password has been '
                    'sent to you.')
        else:
            flash("无效的账号！")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


"""当用户点击了邮件的连接的时，URL就是下面route中的东西了，所以回到这里来。"""
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """如果当前用户已经登录了，说明不用重设密码了"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    """重新弄一个表单来存储新的密码"""
    form = PasswordResetForm()
    if form.validate_on_submit():
        """因为用了staticmethod装饰器，所以可以不用实例化User类，直接用类方法"""
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash("密码重设成功！")
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)