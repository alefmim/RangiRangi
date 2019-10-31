#!/usr/bin/python3

# # # # #
# RangiRangi v191030alpha
# A simple flask based Microblogging CMS written in Python
# Coded by Amir Mohammad Anvari
# Contact me at AmirMohammad@Programmer.Net
# # # # # # # # #  #

from flup.server.fcgi import WSGIServer
from flask import Flask, render_template, request \
, Response, Markup, redirect ,url_for, abort, escape \
, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from random import randrange
import datetime
import re
import os
import locale
import jdatetime
import json
import hashlib
import urllib.parse

PPP = 10 # Number of Posts Per Page

# Initializations and Basic Configurations
app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["3 per second"], # Maximum allowed number of requests per second
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' # Database connection string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Because we don't need it
db = SQLAlchemy(app)

# Persian months
months = {1:'فروردین', 2:'اردیبهشت', 3:'خرداد', 4:'تیر', 5:'مرداد', 6:'شهریور', 7:'مهر', 8:'آبان', 9:'آذر', 10:'دی', 11:'بهمن', 12:'اسفند'}

# Order Columns are currently not being used but we'll use them in the future!
# Category Object (Categories Table)
class dbcategory(db.Model):
	catid = db.Column('catid', db.Integer, primary_key = True, autoincrement=True)		# Category ID (Primary Key)
	name = db.Column('name', db.String(32), nullable=False, unique=True)				# Category Name
	order = db.Column('order', db.Integer, nullable=False)								# Category Order
	categories = db.relationship('dbpost', backref=db.backref("dbcategory", lazy=True)) # Defining a foreign key (backref to category in posts table!)
	# Constructor
	def __init__(self, name, order):
		self.name = name	# Category Name
		self.order = order 	# Category Order

# Post Object (Posts Table)
class dbpost(db.Model):
	postid = db.Column('postid', db.Integer, primary_key = True, autoincrement=True)				# Post ID (Primary Key)
	category = db.Column('category', db.Integer, db.ForeignKey('dbcategory.catid'), nullable=False)	# Defining a foreign key
	title = db.Column('title', db.String(32), nullable=True)										# Post Title
	content = db.Column('content', db.String(512), nullable=False) 									# Post Content
	cdatetime = db.Column('datetime', db.String(24), nullable=False)								# Post Date/Time
	dispdate = db.Column('dispdate', db.String(24), nullable=False)									# Post Jalali Date/Time to display below each post!
	comments = db.Column('comments', db.Integer, nullable=False)									# Number of comments on each post
	mediaaddr = db.Column('mediaaddr', db.String(256), nullable=True)								# Multimedia File (Image) Address
	posts = db.relationship('dbcomment', backref=db.backref("dbcomment", uselist=False))			# Defining a foreign key (backref to pid in comments table!)
	# Constructor
	def __init__(self, title, content, cdatetime, dispdate, comments, category, mediaaddr):
		self.title = title			# Post Title
		self.content = content		# Post Content
		self.category = category	# Post Category
		self.cdatetime = cdatetime	# Post Date/Time
		self.dispdate = dispdate	# Post Jalali Date/Time to display below each post!
		self.comments = comments	# Number of comments on each post
		self.mediaaddr = mediaaddr	# Multimedia File (Image) Address
	
# Comment Object (Comments Table)
class dbcomment(db.Model):
	cmtid = db.Column('commentid', db.Integer, primary_key = True, autoincrement=True)		# Comment ID (Primary Key)
	pid = db.Column('postid', db.Integer, db.ForeignKey('dbpost.postid'), nullable=False)	# Post ID (Foreign Key)
	title = db.Column('title', db.String(32), nullable=True)								# Comment Title
	content = db.Column('content', db.String(256), nullable=False) 							# Comment Content
	cdatetime = db.Column('datetime', db.String(20), nullable=False)						# Comment Date/Time
	dispdate = db.Column('dispdate', db.String(24), nullable=False)							# Comment Jalali Date/Time to display above each comment!
	name = db.Column('name', db.String(24), nullable=False) 								# Comment's Author's Name
	website = db.Column('website', db.String(24), nullable=True) 							# Comment's Author's Website
	emailaddr = db.Column('emailaddr', db.String(40), nullable=True) 						# Comment's Author's EMail Address
	# Constructor
	def __init__(self, pid, title, content, cdatetime, dispdate, name, website, emailaddr):
		self.pid = pid				# Post ID (Foreign Key)
		self.title = title			# Comment Title
		self.content = content		# Comment Content
		self.cdatetime = cdatetime	# Comment Date/Time
		self.dispdate = dispdate	# Comment Jalali Date/Time to display above each comment!
		self.name = name			# Comment Author's Name
		self.website = website		# Comment Author's Website
		self.emailaddr = emailaddr	# Comment Author's EMail Address

# Tag Object (Tags Table)
class dbtag(db.Model):
	tagid = db.Column('tagid', db.Integer, primary_key = True, autoincrement=True)	# Tag ID (Primary Key)
	keyword = db.Column('keyword', db.String(512), nullable=False, unique=True)		# Tag Keyword
	frequency = db.Column('frequency', db.Integer, nullable=False)					# Tag Frequency
	popularity = db.Column('popularity', db.Integer, nullable=False)				# Tag Popularity
	# Constructor
	def __init__(self, keyword, frequency, popularity):
		self.keyword = keyword			# Tag Keyword
		self.frequency = frequency		# Tag Frequency
		self.popularity = popularity	# Tag Popularity

# Link Object (Links Table)
class dblink(db.Model):
	linkid = db.Column('linkid', db.Integer, primary_key = True, autoincrement=True)	# Link ID (Primary Key)
	name = db.Column('name', db.String(24), nullable=False, unique=True)				# Link Name
	address = db.Column('address', db.String(256), nullable=False, unique=True)			# Link Address
	order = db.Column('order', db.Integer, nullable=False)								# Link Order
	# Constructor
	def __init__(self, name, address, order):
		self.name = name		# Link Name
		self.address = address	# Link Address
		self.order = order		# Link Order


# This function replaces all hashtags in 'rawText' with linked hashtags 
# 'url' must only contain domain name and script path (send request.script_root as its value!)
def prcText(rawText, url):
	# Find all hashtags using regex
	hashTags = re.findall(r"#(\w+)", rawText)
	# Replace each hashtag with a link to that hashtag
	for hashTag in set(hashTags):
		rawText = rawText.replace('#' + hashTag, "<a href='" \
		+ url + "/?tag=" + hashTag + \
		"' class='hashtag'>#" + hashTag + "</a>")
	# Return the produced string to appear on the requested page
	return Markup(rawText)

# After deleting or editing a post we'll call this function to delete or reduce the frequncy of the removed hashtags
def deleteTag(hashTag):
	# Find the hashtag in database using its name
	tag = dbtag.query.filter(dbtag.keyword == hashTag)
	# Check if no hashtag is found
	if tag.count() == 0 :
		# Return if no hashtag is found!
		return
	# If we found a hashtag
	else :
		# Reduce hashtag frequncy if it's more than 1 or delete the hashtag if it's not being used in any post (frequncy <= 1)
		if tag.first().frequency > 1 :
			# Reduce the hashtag frequncy because it's used in another post
			tag.first().frequency = tag.first().frequency - 1
		else :
			# Delete the hashtag from the database because it's not used in any post
			tag.delete()
	# Save changes to the database
	db.session.commit()

# This function handles our main page
@app.route("/")
def index():
	# Check if admin logged in
	login()
	# Check if config file exists
	try :
		with open('config.json', 'r') as configFile :
			config = json.load(configFile) # This will load config file to memory as config object
	except FileNotFoundError : # This exception means that our program is not installed and configured yet!
		# So we'll call install() to make the config file and database file and redirect user to config page
		return render_template("config.html", config=install()) 
	# If someone looks for a specific hashtag we'll increase it's popularity by 1 
	# Get the hashtag from the request
	tag  = request.args.get('tag', default = '', type = str)
	# Find the hashtag on databse
	t = dbtag.query.filter(dbtag.keyword == tag)
	# If it's not a bad request and hashtag exists in the database
	if t.count() != 0 :
		# Increase its popularity by 1
		t.first().popularity = t.first().popularity + 1
		# Save changes to the database
		db.session.commit()
	# Find all categories and save it to 'categories' array
	categories = dbcategory.query.all()
	# We'll show 4 most popular hashtags (favtags) and 4 most used hashtags (frqtags)
	# Find 4 most popular hashtags and save it to 'favtags' array 
	favtags = dbtag.query.order_by(dbtag.popularity.desc()).limit(4)
	# Find 4 most used hashtags and save it to 'frqtags' array
	frqtags = dbtag.query.order_by(dbtag.frequency.desc()).limit(4)
	# Find all links and save it to 'links' array 
	links = dblink.query.order_by(dblink.order).all()
	# Render the page with the provided data!
	return render_template("index.html", config = config, categories = categories, favtags = favtags, frqtags = frqtags, links = links, admin=session['logged_in'])

# This function sends the posts to the client
@app.route("/page", methods=['GET'])
@limiter.limit("60/second")
def page():
	# Get the data from the request
	pageNum =  request.args.get('page', default = 2, type = int)
	search = request.args.get('search', default = '', type = str)
	category = request.args.get('category', default = -1, type = int)
	sort = request.args.get('sort', default = 'ascdate', type = str)
	tag  = request.args.get('tag', default = '', type = str)
	# We'll use this object to execute database queries
	query = dbpost.query
	# Handle the requested arguments
	if category > -1 : # Find all posts in a specific category
		query = query.filter(dbpost.category == category)
	if search != '' : # Find all posts that contain search string
		query = query.filter(or_(dbpost.content.contains(search), dbpost.title.contains(search)))
	if tag != '' :
		# Find all posts that contain a specific hashtag (We'll put a # before the tag because it's not included in request string! /?tag=python)
		query = query.filter(dbpost.content.contains('#' + tag))
	if sort == 'ascdate' : # Sort by Date (Ascending Order)
		query = query.order_by(dbpost.postid)
	if sort == 'descdate' or sort == '' : # Sort by Date (Descending Order)
		query = query.order_by(dbpost.postid.desc())
	if sort == 'asccomments' : # Sort by Number of Comments (Ascending Order)
		query = query.order_by(dbpost.comments)	
	if sort == 'desccomments' : # Sort by Number of Comments (Descending Order)
		query = query.order_by(dbpost.comments.desc())
		
	# Limit results to the number of Posts Per Page
	results = query.offset(pageNum * PPP).limit(PPP)
	
	# Send "END." if there's no more results to send with status code 200 which means request was successful
	if results.count() == 0 :
		return Response(response="END.", status=200, mimetype='text/html')
	
	# This small block of code will handle the positioning of the posts (should they appear on the right side or the left side of the timeline?!)
	if (PPP % 2) == 1 and (pageNum % 2) == 1 :
		c = 0
	else :
		c = 1
	
	# Array of our posts (results)
	posts = []
	
	# We'll use this loop to run 'prcText' function on each post's content
	# and replace all hashtags in each post with linked hashtags! 
	for result in results :
		post = {} # A single post (we'll assign its values below!)
		
		# This is why we created this loop
		# We'll replace hashtags with linked hashtags using the 'prcText' function
		post['content'] = prcText(result.__dict__['content'], request.script_root)
		# Rest is the same without any modification!
		post['postid'] = result.__dict__['postid']
		post['title'] = result.__dict__['title']
		post['category'] = result.__dict__['category']
		post['dispdate'] = result.__dict__['dispdate']
		post['comments'] = result.__dict__['comments']
		post['mediaaddr'] = result.__dict__['mediaaddr']
		# Put this post in our results
		posts.append(post)
	
	return render_template("page.html", posts=posts, c=c, mimetype="text/html", admin=session['logged_in'])

# This function handles config page and configurations 
@app.route("/config", methods=['POST', 'GET'])
def config():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	# Create a new config (we'll load data in it later!)
	config = {}
	# Load config file to the memory as config object
	with open('config.json', 'r') as configFile :
		config = json.load(configFile)
		
	# If there's any request from client to change the config
	if 'title' in request.form :
		with open('config.json', 'w') as configFile: 
			# We'll make a new config object
			newconfig = {}
			# And assign new values to this new config object
			newconfig['title'] = request.form.get('title')
			newconfig['desc'] = request.form.get('desc')
			newconfig['dispname'] = request.form.get('dispname')
			newconfig['mailaddr'] = request.form.get('mailaddr')
			# Check password
			if 'oldpwd' in request.form and 'newpwd' in request.form :
				# Hash the password entered by admin
				currpwd = hashlib.md5(request.form.get('oldpwd').encode('utf-8'))
				# And check if the current password is the same as the one entered by admin
				if  config['pwd'] == currpwd.hexdigest() :
					# If admin requested to change the password 
					if request.form.get('newpwd') != '' :
						# Hash new password
						newpwd = hashlib.md5(request.form.get('newpwd').encode('utf-8'))
						# Save hash to config object
						newconfig['pwd'] = newpwd.hexdigest()
					else :
						# If admin didn't request to change the password then we'll use the old password in new config too
						newconfig['pwd'] = config['pwd']
				else : # If password was wrong!
					json.dump(config, configFile)
					flash('خطا! گذرواژه صحیح نیست، لطفاً دوباره تلاش کنید.')
					return render_template("config.html", config=config)
			# If everything goes well, we'll save new config to the config file
			json.dump(newconfig, configFile)
			# Fill the page with new configs
			return render_template("config.html", config=newconfig)
	# Fill the page with old configs
	return render_template("config.html", config=config)

# This function handles viewing and saving comments
@app.route("/comments", methods=['POST', 'GET'])
def comments():
	# This function is necessary before running any code that's not intended to get executed by anyone except admin
	login()
	# Get 'postid' from the request
	postid = request.args.get('postid', default=-1, type=int)
	# Check if it's not a bad request!
	if postid < 1 and not 'content' in request.form:
		return ('', 400)
	# If there's a new comment
	if 'content' in request.form :
		# Find the post which this new comment belongs to
		post = dbpost.query.filter(dbpost.postid == postid).first()
		# We'll check if it's not a bad request again!
		if post is None :
			return ('', 400)
		# Get the data from the request
		name = request.form.get('name')
		mailaddr = request.form.get('mailaddr')
		website = request.form.get('website')
		content = request.form.get('content')
		postid = request.form.get('postid', type=int)
		cdatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		jdate = jdatetime.datetime.now() # This will assign current Jalali Date to jdate object 
		dispdate = str(jdate.day) + ' ' + months[jdate.month] + ' ' + str(jdate.year) # Replace the number of month with months's name
		title = '' # This attribute is not being used yet! we may use it in the future
		# Create a new comment with the data provided above
		comment = dbcomment(postid, title, content, cdatetime, dispdate, name, website, mailaddr)
		# Increase the number of comments of the post which this comment belongs to
		post.comments = post.comments + 1
		# Add this new comment to the database
		db.session.add(comment)
		
		db.session.commit()
	# Load all comments that belong to a specific post from the database
	comments = dbcomment.query.filter(dbcomment.pid == postid).all()
	
	return render_template("comments.html", comments = comments, postid = postid, admin=session['logged_in'])

# This function handles removing comments 
@app.route("/deletecomment", methods=['GET'])
def deletecomment():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Return status code 401 'UNAUTHORIZED'
		return ('', 401)
	# Check if it's not a bad request
	if 'id' in request.args :
		# Get 'id' from the request
		id =  request.args.get('id', type = int)
		# Find the comment by its id
		comment = dbcomment.query.filter(dbcomment.cmtid == id)
		# Check if the comment exists
		if comment.first() is None :
			return ('', 400)
		# Find the post which this comment belongs to
		post = dbpost.query.filter(dbpost.postid == comment.first().pid).first()
		# Reduce the number of comments of the post which this comment belongs to
		post.comments = post.comments - 1
		# Delete the comment
		comment.delete()
		# Save changes to the database
		db.session.commit()
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles 'Share' page
@app.route("/share", methods=['GET'])
def share():
	# Check if it's not a bad request
	if 'postid' in request.args :
		# Get 'id' from the request
		id = request.args.get('postid', type=int)
		# Find the requested post
		post = dbpost.query.filter(dbpost.postid == id).first()
		# Check if the post exists and it's not a bad request
		if not post is None :
			# we'll send the post to the client so its data will appear on the 'Share' page
			return render_template("share.html", post = post)
	# Return "Failure!"
	return ('', 400)

# This function handles 'Post' page which is used for saving new posts and editing existing posts in the database
@app.route("/post", methods=['POST', 'GET'])
def post():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	
	# If there's no category then we'll make one! (otherwise an error will occur!)
	if dbcategory.query.count() == 0 :
		category = dbcategory('متفرقه', 0)
		db.session.add(category)
		# Save changes to the database
		db.session.commit()
	# Get the list of categories
	categories = dbcategory.query.all()
	# Make a new post!
	post = {}
	
	# Get 'id' from the requested url, if it's empty we'll assign it '-1' 
	id =  request.args.get('id', default = -1, type = int)
	
	# If user requests to edit a post then id will be more than zero
	if id > -1 :
		# Find the post which user requested to edit
		post = dbpost.query.filter(dbpost.postid == id).first()
	# If there's any data from user
	if 'content' in request.form :
		# Get the data from the request
		category = request.form.get('cat')
		title = request.form.get('title')
		content = request.form.get('content')
		mediaaddr = request.form.get('addr')
		postid = request.form.get('id')
		# If postid is not empty then user is editing an existing post
		if postid != '':
			# Find the post by its id
			post = dbpost.query.filter(dbpost.postid == int(postid)).first()
			# Find the hashtags in the post
			hashTags = re.findall(r"#(\w+)", post.content)
			# Execute deleteTag for each hashtag in our old post content (we'll add the hashtags that used in the new post content later!)
			for hashTag in set(hashTags):
				deleteTag(hashTag)
			# Save the data from request in the existing post
			post.category = category
			post.title = title
			post.mediaaddr = mediaaddr
			post.content = content
		# If postid is empty then it's a new post and user is not editing and existing post
		else :
			# Get the Date/Time
			cdatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			# New posts don't have any comment when they're getting published!
			comments = 0
			# Get Jalali Date
			jdate = jdatetime.datetime.now()
			# Replace Jalali month number with Jalali month name
			dispdate = str(jdate.day) + ' ' + months[jdate.month] + ' ' + str(jdate.year)
			# Create a new post with the provided data
			newpost = dbpost(title=title, content=content, cdatetime=cdatetime, dispdate=dispdate, comments=comments, category=category, mediaaddr=mediaaddr)
			# Save this new post to database
			db.session.add(newpost)
		# Save changes to the database
		db.session.commit()
		# Find all hashtags in the post content
		hashTags = re.findall(r"#(\w+)", content)
		# Process each hashtag in the content
		for hashTag in set(hashTags):
			# Find the hashtag in the database
			tag = dbtag.query.filter(dbtag.keyword == hashTag)
			# If it's a new hashtag
			if tag.count() == 0 :
				# It's the first time this hashtag appeared in a post so frequency will be 1
				frequency = 1
				# Nobody clicked on the hashtag yet so popularity is unknown, we'll assign 0 to the popularity for now
				popularity = 0
				# Create this new hashtag
				tag = dbtag(keyword=hashTag, frequency=frequency, popularity=popularity)
				# Save this hashtag to database
				db.session.add(tag)
			# If it's an existing hashtag
			else :
				# Find the hashtag in the database
				tag = tag.first()
				# Increase it's frequency by 1
				tag.frequency = tag.frequency + 1
			# Save changes to the database
			db.session.commit()
		# Return to index and let the user see the new post
		return redirect(url_for('index'))
	
	return render_template("post.html", post=post, categories = categories, admin=session['logged_in'])
	
# This function Removes the post from the database and execute the 'deleteTag' function for its hashtags and remove its comments
def removepost(id):
	# Find the post in the database
	post = dbpost.query.filter(dbpost.postid == id)
	# Delete all the comments that belong to this specific post
	dbcomment.query.filter(dbcomment.pid == id).delete()
	# Get post content
	content = post.first().content
	# And find all the hashtags in this content
	hashTags = re.findall(r"#(\w+)", content)
	# Execute 'deleteTag' function for all the hashtags found in the content
	for hashTag in set(hashTags):
		# remove the hashtag or reduce its frequency
		deleteTag(hashTag)
	# Delete the post
	post.delete()
	# Save changes to the database
	db.session.commit()

# This function handles requests for deleting posts
@app.route("/deletepost", methods=['GET'])
def deletepost():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	# If it's not a bad request
	if 'id' in request.args :
		# Get postid
		id =  request.args.get('id', type = int)
		# Call 'removepost' function to remove the post from the database
		removepost(id)
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles creating new categories
@app.route("/newcategory", methods=['GET'])
def newcategory():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	# If it's not a bad request
	if 'name' in request.args :
		# Get 'name' from request
		name = request.args.get('name')
		order = 0
		# Return "Failure!" if name is empty
		if name == '' :
			return ('', 400)
		# Create a new category
		category = dbcategory(name, order)
		# Add this new category to the database
		db.session.add(category)
		# Save changes to the database
		db.session.commit()
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles editing existing categories
@app.route("/editcategory", methods=['GET'])
def editcategory():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	# If it's not a bad request
	if 'id' in request.args :
		# Get new category name from the request
		id =  request.args.get('id', type=int)
		name = request.args.get('name')
		order = 0
		# Find the category
		category = dbcategory.query.filter(dbcategory.catid == id)
		# If the category exists
		if category.count() > 0 :
			# Change the category name to the one requested by user 
			category.first().name = name
			# Save changes to the database
			db.session.commit()
			# Return "Success!"
			return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles removing the categories
@app.route("/removecategory", methods=['GET'])
def removecategory():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	# If it's not a bad request
	if 'id' in request.args :
		# Get the category id from the request
		id = request.args.get('id', type=int)
		# Find the category by its id in the database and delete it
		dbcategory.query.filter(dbcategory.catid == id).delete()
		# After deleting the category we'll delete all the posts that belong to that category too
		# There's no Do..While in python so we'll use and endless While(True) Loop
		while True:
			# Find the posts that belong the removed category
			post = dbpost.query.filter(dbpost.category == id).first()
			# If the post doesn't exists!
			if post is None :
				break # Break out of this endless loop
			# Call 'removepost' to delete the post and its comments and hashtags
			removepost(post.postid)
		# If there's no category in database we'll make one! (to prevent errors!)
		if dbcategory.query.count() == 0 :
			category = dbcategory('متفرقه', 0)
			db.session.add(category)
		# Save changes to the database
		db.session.commit()
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles adding new links to the link box
@app.route("/addlink", methods=['GET'])
def addlink():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	# If it's not a bad request
	if 'address' in request.args :
		# Get the data from the request
		name = request.args.get('name')
		addr = request.args.get('address')
		address = urllib.parse.unquote(addr)
		order = 0
		# Create a new link with the data provided by user
		link = dblink(name, address, order)
		# Add this new link to the database
		db.session.add(link)
		# Save changes to the database
		db.session.commit()
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles editing existing links
@app.route("/editlink", methods=['GET'])
def editlink():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	# If it's not a bad request
	if 'id' in request.args :
		# Get the data from the request
		id =  request.args.get('id', type=int)
		name = request.args.get('name')
		addr = request.args.get('address')
		address = urllib.parse.unquote(addr)
		order = 0
		# Find the link by its id
		link = dblink.query.filter(dblink.linkid == id)
		# If the link that we're looking for exists in the database
		if link.count() > 0 :
			# Change its values to the ones requested by user
			link.first().name = name
			link.first().address = address
			# Save changes to the database
			db.session.commit()
			# Return "Success!"
			return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles removing links
@app.route("/removelink", methods=['GET'])
def removelink():
	# This page requires admin privileges so we'll check if it's requested by admin or not
	login()
	# If 'logged_in' is False then user has no admin privileges
	if session['logged_in'] == False :
		# Ask the user to login first!
		flash('شما مجوز مورد نیاز برای دسترسی به این صفحه را ندارید!')
		# Redirect to the main page
		return redirect(url_for('index'))
	# If it's not a bad request
	if 'id' in request.args :
		# Get link's id from the request
		id = request.args.get('id', type=int)
		# Find the link by its id and delete it
		dblink.query.filter(dblink.linkid == id).delete()
		# Save changes to the database
		db.session.commit()
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles the login process and saving 
@app.route("/login", methods=['POST'])	# Limit the number of allowed requests to 
@limiter.limit("3/minute") 				# 3		per minute
@limiter.limit("15/hour")				# 15	per hour
@limiter.limit("45/day")				# 45	per day
def login():
	# If user didn't login yet then we'll save (logged_in = False) for his session!
	if not 'logged_in' in session :
		session['logged_in'] = False
	# If there's any login attempt without providing password then we'll redirect it to the main page and ignore it!
	if not 'pwd' in request.form :
		return redirect(url_for('index'))
	# Open config file to check the password stored in it
	with open('config.json', 'r') as configFile :
		# Load the config file to config object
		config = json.load(configFile)
		# Get password from the request
		pwd = request.form.get('pwd')
		# Hash the password
		pwd = hashlib.md5(pwd.encode('utf-8')).hexdigest()
		# If the password entered by the user is the same as the one in our config file 
		if config['pwd'] == pwd :
			 # Login was successful and we'll set 'logged_in' to true in our session, this will grant the user admin privileges!
			session['logged_in'] = True
		# If the password is wrong
		elif 'pwd' in request.form :
			# Ask the user to enter the password again
			flash('خطا! گذرواژه صحیح نیست، لطفاً دوباره تلاش کنید.')
	# Return to the main page
	return redirect(url_for('index'))

# This function handles the logout process
@app.route("/logout")
def logout():
	# Remove logged_in from the session
	session.pop('logged_in', None)
	# Return to the main page
	return redirect(url_for('index'))

# This function handles the installation process and creating the config file and the database
def install():
	# Create the database file and its tables
	db.create_all()
	# Create a category (to prevent errors!)
	if dbcategory.query.count() == 0 :
		category = dbcategory('متفرقه', 0)
		db.session.add(category)
		# Save changes to the database
		db.session.commit()
	# Set the admin logged_in status to True and grant the user admin privileges
	session['logged_in'] = True
	# Create the config file
	with open('config.json', 'w') as configFile: 
		# Create a new config
		newconfig = {}
		# Assign empty values to our configurations
		newconfig['title'] = ''
		newconfig['desc'] = ''
		newconfig['dispname'] = ''
		newconfig['mailaddr'] = ''
		# Save the default password (md5 hash of 'admin') in our new config
		newpwd = hashlib.md5('admin'.encode('utf-8'))
		newconfig['pwd'] = newpwd.hexdigest()
		# Create a config file using our new config file 
		json.dump(newconfig, configFile)
		# Give user admin's password!
		flash('گذرواژه :\n\nadmin')
		# Return this new config object so we can use it to fill the config page fields
		return newconfig

# If this module is the main program!
if __name__ == '__main__':
	# assign a 12 bytes length random value to app.secret_key
	app.secret_key = os.urandom(12)
	# Run the program (Only for development purposes!)
	app.run(debug=True)
	# Run the program (Uncomment the lines below on the deployment environment!)
	#WSGIServer(app, bindAddress='/tmp/blog-fcgi.sock-0').run()
	#WSGIServer(app).run()

