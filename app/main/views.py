from flask import current_app, request, render_template, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from . import main
from ..models import User, Role, Permission, Post
from .. import db
from .forms import PostForm, EditProfileForm, EditProfileAdminForm
from ..decorators import admin_required


"""这个视图函数把表单和博客文章列表传给模板"""
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    """因为一开始输入的URL对应的就是这里，渲染index.html， 并且显示所有的文章。
    这里又加了文章分页阅读的功能。page为渲染的页数。paginate方法第一个参数是渲染的
    页数。per_page是每页显示的博客条数。"""
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


"""在显示用户页面的基础上添加用户的微博信息"""
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


"""用户的资料编辑路由"""
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        """向数据库提交current_user实例"""
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("个人主页已经更新！")
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data =current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


"""管理员的资料编辑路由，必须处于登录状态，必须是管理员"""
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        """因为在表单中不是用默认的字符串来初始化，而是用的int参数
        所以，这里要在Role类中查找到int所代表的字符串"""
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("个人主页已经更新（管理员）！！")
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    """这里必须要传入一个post列表，这样post.html引用的_post.html独立模块才能处理post。"""
    return render_template('post.html', posts=[post])

"""编辑微博文章的视图函数，只允许文章作者或管理员来编辑文章， 如果编辑了，那么去往编辑后的
微博文章主页。没有编辑时，显示的内容就是文章原来的内容"""
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("文章已经更新！")
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)