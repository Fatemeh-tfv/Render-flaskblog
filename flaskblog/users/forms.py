from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flaskblog.models import user

class RegistrationForm(FlaskForm):

    UserName = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    Email = StringField('Email',validators=[DataRequired(), Email()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Confirm_Password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('Password')])

    Submit = SubmitField('Sign up')

    def validate_UserName(self, UserName):
        User = user.query.filter_by(UserName = UserName.data).first()
        if User:
            raise ValidationError('That username is taken. please choose another one!')
        
    def validate_Email(self, Email):
        email = user.query.filter_by(Email = Email.data).first()
        if email:
            raise ValidationError('That email is taken. please choose another one!')

class LoginForm(FlaskForm):

    Email = StringField('Email',validators=[DataRequired(), Email()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Remember = BooleanField('Remember Me')

    Submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):

    UserName = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    Email = StringField('Email',validators=[DataRequired(), Email()])
    Picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])

    Submit = SubmitField('Update')

    def validate_UserName(self, UserName):
        if UserName.data != current_user.UserName:
            User = user.query.filter_by(UserName = UserName.data).first()
            if User:
                raise ValidationError('That username is taken. please choose another one!')
        
    def validate_Email(self, Email):
        if Email.data != current_user.Email:
            email = user.query.filter_by(Email = Email.data).first()
            if email:
                raise ValidationError('That email is taken. please choose another one!')
            
class RequestResetForm(FlaskForm):
    Email = StringField('Email',validators=[DataRequired(), Email()])
    Submit = SubmitField('Request Password Reset')

    
    def validate_Email(self, Email):
        email = user.query.filter_by(Email = Email.data).first()
        if email is None:
            raise ValidationError('There is no account with that email. You must register first.')
        
class ResetPasswordForm(FlaskForm):
    Password = PasswordField('Password', validators=[DataRequired()])
    Confirm_Password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('Password')])
    Submit = SubmitField('Reset Password')