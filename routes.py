import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
								 PostForm, SubscribeForm, FollowingForm)
from flaskblog.models import User, Post, Subscriber
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
#WE CAN REPRESENT DATABASE STRUCTURE AS CLASSES OR CALLED MODELS. THESE CAN BE PUT INTO DIFFERENT FILE

#--------------------------------------------HOME PAGE ROUTE--------------------------------------------------

@app.route("/")

@app.route("/home")
@login_required
def home():
	posts = Post.query.order_by(Post.date_posted.desc())
	subscribee = Subscriber.query.filter_by(subscriber_id=current_user.id)
	subs = []
	for x in subscribee:
		subs.append(x.poster_id)

	return render_template('home.html', posts=posts, current_user=current_user,subs=subs)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated: #CHECKS IF USER IS ALREADY LOGGED IN
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #ASSIGNS HASHED PASSWORD TO VARIABLE
		user = User(username=form.username.data, email=form.email.data, password=hashed_password) #CREATING A NEW INSTANCE OF USER
		db.session.add(user) #ADD ABOVE CHANGES TO DATABASE
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success') #success is category for successful form validation
		return redirect(url_for('login')) #AFTER SUCCESSFUL ACCOUNT CREATION USER IS REDIRECTED TO LOGIN PAGE
	return render_template('register.html', title='Register', form=form)

#--------------------------------------------USER MY POSTS ROUTE----------------------------------------------
@app.route("/myposts", methods=['GET', 'POST'])
def my_posts():
	
	posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc())
	return render_template('my_posts.html', title='My Posts', posts=posts)

#--------------------------------------------LOGIN ROUTE----------------------------------------------

@app.route("/login", methods=['GET', 'POST']) #WE NEED TO ACCEPT GET/POST REQUEST OTHER IT WILL THROW METHOD NOT FOUND ERROR
def login():
	if current_user.is_authenticated: #CHECKS IF USER IS ALREADY LOGGED IN
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit(): #THIS IS FOR FORM VALIDATION
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger') #THIS MESSAGE GETS TO LAYOUT PAGE
	return render_template('login.html', title='Login', form=form)

#--------------------------------------------LOGOUT ROUTE----------------------------------------------

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('login'))

#--------------------------------------------SAVE PICTURE FUNCTION----------------------------------------------

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	output_size = (125,125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn

#--------------------------------------------ACCOUNT ROUTE----------------------------------------------

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data #UPDATES ACCOUNT INFO
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET': #DISPLAYS INFO IN ACCOUNT BEFORE UPDATING IT
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)

#--------------------------------------------NEW POST ROUTE----------------------------------------------

def post_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)
	
	i = Image.open(form_picture)
	i.save(picture_path)

	return picture_fn

def send_post_email(user,post_id,subs):
	msg = Message(f'New Post by {user.username}',sender='noreply@gmail.com',recipients=subs)
	msg.body = f'''To see the new post, visit the following link:
{url_for('post', post_id=post_id, _external=True)}
'''
	mail.send(msg)

@app.route("/post/new", methods=['GET', 'POST']) #FOR POSTS BY USER IN BLOG
@login_required #BECAUSE CREATING POST REQUIRES USER TO LOGIN
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = post_picture(form.picture.data)
		else:
			picture_file = None
			
		post = Post(title=form.title.data,content=form.content.data,
					author=current_user,image_file=picture_file,category=form.category.data)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		
		post = Post.query.filter_by(title=form.title.data,content=form.content.data,author=current_user,category=form.category.data).first()
		post_id = post.id
		subscribers = Subscriber.query.filter_by(poster_id=current_user.id,poster_name=current_user.username)
		subs = []
		for x in subscribers:
			subs.append(x.poster.email)
		if subs:
			send_post_email(current_user, post_id, subs)
		return redirect(url_for('home'))

	return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')
		
#--------------------------------------------POST ROUTE-----------------------------------------------------

@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

#--------------------------------------------UPDATE POST ROUTE----------------------------------------------

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = post_picture(form.picture.data)
			post.image_file = picture_file
		post.title = form.title.data
		post.content = form.content.data
		post.category = form.category.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
		form.category.data = post.category
	return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

#--------------------------------------------DELETE POST ROUTE----------------------------------------------

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

#--------------------------------------------USER ROUTE----------------------------------------------

@app.route("/user/<string:username>") # GIVES POSTS BY USER BY CLICKING ON USER NAME
def user_posts(username):
	
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user)\
			.order_by(Post.date_posted.desc())
	return render_template('user_posts.html', posts=posts, user=user)

#--------------------------------------------SUBSCRIBER ROUTE--------------------------------------------------

@app.route("/subscribe", methods=['GET', 'POST'])
@login_required
def subscribe():
	form = SubscribeForm()
	users = User.query.order_by(User.id.asc())
	subscribee = Subscriber.query.filter_by(subscriber_id=current_user.id)
	subs = []
	for x in subscribee:
		subs.append(x.poster_id)

	poster_id = request.args.get('poster_id', default=None)
	poster_name = request.args.get('poster_name', default=None)
	subscribe_checkbox = form.follow_unfollow.data

	if subscribe_checkbox == True:
		subscriber = Subscriber(subscriber_id=current_user.id,subscriber_name=current_user.username,poster_id=poster_id,poster_name=poster_name)
		db.session.add(subscriber)
		db.session.commit()
		flash(f'You have been subscribed to {poster_name}', 'success')
		return redirect(url_for('home'))
			
	return render_template('subscribe.html',title='Subscribe',users=users,current_user=current_user,form=form,subs=subs)

#--------------------------------------------FOLLOWING ROUTE--------------------------------------------------

@app.route("/following", methods=['GET', 'POST'])
@login_required
def following():
	form = FollowingForm(follow_unfollow=True)
	users = User.query.order_by(User.id.asc())
	followings = Subscriber.query.filter_by(subscriber_id=current_user.id)
	subs = []
	for x in followings:
		subs.append(x.poster_id)
	
	poster_id = request.args.get('poster_id', default=None)
	poster_name = request.args.get('poster_name', default=None)
	subscribe_checkbox = form.follow_unfollow.data

	if subscribe_checkbox == False:
		following = Subscriber.query.filter_by(subscriber_id=current_user.id,subscriber_name=current_user.username,poster_id=poster_id,poster_name=poster_name).first()
		db.session.delete(following)
		db.session.commit()
		flash(f'You have been unsubscribed to {poster_name}', 'success')
		return redirect(url_for('home'))
	
	return render_template('following.html',title='Following',users=users,current_user=current_user,form=form,subs=subs)

#--------------------------------------------FOLLOWERS ROUTE--------------------------------------------------

@app.route("/followers", methods=['GET', 'POST'])
@login_required
def followers():
	
	users = User.query.order_by(User.id.asc())
	followings = Subscriber.query.filter_by(poster_id=current_user.id)
	subs = []
	for x in followings:
		subs.append(x.subscriber_id)
	
	return render_template('followers.html',title='Followers',users=users,current_user=current_user,subs=subs)

#--------------------------------------------CATEGORY ROUTE--------------------------------------------------

@app.route("/category/<category_type>", methods=['GET', 'POST'])
@login_required
def category(category_type):
	posts = Post.query.filter_by(category=category_type).order_by(Post.date_posted.desc())
	followings = Subscriber.query.filter_by(subscriber_id=current_user.id)
	subs = []
	for x in followings:
		subs.append(x.poster_id)
	
	poster_id = request.args.get('poster_id', default=None)
	post_id = request.args.get('post_id', default=None)
	
	if poster_id:
		if int(poster_id) in subs:
			return redirect(url_for('post', post_id=post_id))
		else:
			return redirect(url_for('subscribe'))
	
	return render_template('category.html', title=category_type, posts=posts, current_user=current_user)