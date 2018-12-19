import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #SET URI FOR WHERE DATABASE IS LOCATED AND WE ARE USING SQLITE DATABASE
db = SQLAlchemy(app) #CREATE DATABASE INSTANCE
bcrypt = Bcrypt(app) #HASHED PASSWORD
login_manager = LoginManager(app) #FOR LOGIN AUTHENTICATION
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'aalind84@gmail.com'#os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = '11071997#Aadi'#os.environ.get('EMAIL_PASS')
mail = Mail(app)

from flaskblog import routes