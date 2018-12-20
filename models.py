from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader #DECORATOR
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin): #TO CREATE USER MODEL
    id = db.Column(db.Integer, primary_key=True) #TO CREATE ID ATTRIBUTE OR COLUMN
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    subscribers = db.relationship('Subscriber', backref='poster', lazy=True)
    #POST ATTRIBUTE HAS RELATIONSHIP TO POST MODEL
    #BACKREF IS SIMILAR TO ADDING ANOTHER COLUMN TO POST MODEL
    #USING BACKREF WHEN WE HAVE ANY POST WE CAN USE THIS AUTHOR ATTRIBUTE TO GET USER WHO CREATED THE POST
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None 

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model): #TO CREATE POST MODEL
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #UTCNOW IS USED TO SAVE DATE AND TIME
    image_file = db.Column(db.String(20))
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    #IN FOREIGN KEY WE ARE REFERENCING TABLE NAME AND COLUMN NAME WHEREAS IN POST RELATIONSHIP WE ARE GIVING POST MODEL
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Subscriber(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.Integer, nullable=False)
    poster_name = db.Column(db.String(20), nullable=False)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscriber_name = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f"Subscribe('{self.poster_name}', '{self.subscriber_name}')" 