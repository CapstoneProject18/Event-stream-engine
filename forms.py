from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed #TO UPLOAD PROFILE PICTURE IN ACCOUNT PAGE
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User, Subscriber

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username): #THIS CHECK IF A USERNAME IS ALREADY IN THE DATABASE
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email): #THIS CHECK IF A EMAIL IS ALREADY IN THE DATABASE
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])]) #FOR PROFILE PICTURE UPLOAD
    submit = SubmitField('Update')

    def validate_username(self, username): #THIS CHECK IF A USERNAME IS ALREADY IN THE DATABASE
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email): #THIS CHECK IF A EMAIL IS ALREADY IN THE DATABASE
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField(u'Pick category:',
                                choices=[('sports','Sports'),('entertainment','Entertainment'),('arts','Arts'),
                                ('business','Business'),('science','Science'),('psychology','Psychology'),
                                ('health','Health'),('technology','Technology'),('politics','Politics'),
                                ('travel','Travel'),('fashion','Fashion')])
    picture = FileField('Add Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')

class SubscribeForm(FlaskForm):
    poster_id = StringField('Poster_Id', validators=[DataRequired()])
    poster_name = StringField('Poster_Name', validators=[DataRequired()])
    follow_unfollow = BooleanField('')

class FollowingForm(FlaskForm):
    poster_id = StringField('Poster_Id', validators=[DataRequired()])
    poster_name = StringField('Poster_Name', validators=[DataRequired()])
    follow_unfollow = BooleanField('')