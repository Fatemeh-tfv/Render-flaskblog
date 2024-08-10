from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import post, user
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import Save_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.Password.data).decode('utf-8')
        User = user(UserName= form.UserName.data, Email= form.Email.data, Password= hashed_pass)
        db.session.add(User)
        db.session.commit()
        flash('Your account has been created you are now able to log in', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title= 'Register', form= form)

@users.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        User = user.query.filter_by(Email= form.Email.data).first()
        if User and bcrypt.check_password_hash(User.Password, form.Password.data):
            login_user(User, remember=form.Remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('login unsuccessful, please check your email and password', 'danger')
    return render_template('login.html', title= 'Login', form= form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods= ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.Picture.data:
            picture_file = Save_picture(form.Picture.data)
            current_user.image_file = picture_file
        current_user.UserName= form.UserName.data
        current_user.Email= form.Email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.UserName.data = current_user.UserName
        form.Email.data = current_user.Email
    image_file = url_for('static', filename= 'P_pics/'+ current_user.image_file)
    return render_template('account.html', title= 'Account', image_file= image_file, form= form)

@users.route('/user/<string:UserName>')
def user_posts(UserName):
    page = request.args.get('page', 1, type=int)
    User = user.query.filter_by(UserName= UserName).first_or_404()
    posts = post.query.filter_by(author= User)\
        .order_by(post.date_posted.desc())\
        .paginate(page=page, per_page=4)
    return render_template('user_posts.html', posts= posts, User= User)

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        User = user.query.filter_by(Email= form.Email.data).first()
        send_reset_email(User)
        flash('An email has sent with instructions to reset your password', 'info')
        
        return redirect(url_for('users.login'))
    
    return render_template('reset_request.html', title= 'Reset Password', form= form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    User = user.verify_reset_token(token)
    if User is None:
        flash('That is an invalid or expire token', 'warning')
        return redirect(url_for('users.reset_request'))
    
    form= ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.Password.data).decode('utf-8')
        User.Password = hashed_pass
        db.session.commit()
        flash('Your Password has been updated! you are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title= 'Reset Password', form= form)