#!/usr/bin/python3

# # # # #
# RangiRangi
# A simple flask based Microblogging CMS written in Python
# Coded by AlefMim (github.com/alefmim)
# Contact me at mralefmim@gmail.com
# # # # # # # # # #

import os
import re
import datetime
import jdatetime
import json
import hashlib
import urllib.parse
import functools

from flask import (
	Flask, 
	render_template, 
	request,
	Response, 
	Markup, 
	redirect,
	url_for, 
	abort, 
	escape,
	session,
	flash,
)
from wtforms.validators import (
	InputRequired,
	DataRequired,
	Optional,
	Email,
	URL,
	Length,
	NumberRange,
	AnyOf,
	EqualTo,
	ValidationError
)
from wtforms.widgets import (
	HiddenInput,
	TextArea
)
from wtforms import (
	SelectField,
	StringField,
	IntegerField,
	PasswordField
)
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_inputs import Inputs
from sqlalchemy import or_
from random import randrange
from werkzeug.middleware.proxy_fix import ProxyFix

# Initializations and Basic Configurations
app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["3 per second"], # Maximum allowed number of requests per second
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' # Database connection string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Because we don't need it
# Assign a 32 bytes length random value to app.secret_key
app.secret_key = os.urandom(32)
app.wsgi_app = ProxyFix(app.wsgi_app)
csrf = CSRFProtect(app)
db = SQLAlchemy(app)

# Order Columns are currently not being used but we'll use them in the future!
# Category Object (Categories Table)
class dbcategory(db.Model):
	catid = db.Column('catid', db.Integer, primary_key = True, autoincrement=True)		# Category ID (Primary Key)
	name = db.Column('name', db.String(32), nullable=False, unique=True)			# Category Name
	order = db.Column('order', db.Integer, nullable=False)					# Category Order
	categories = db.relationship('dbpost', backref=db.backref("dbcategory", lazy=True)) 	# Defining a foreign key (backref to category in posts table!)
	# Constructor
	def __init__(self, name: str, order: int):
		self.name = name	# Category Name
		self.order = order 	# Category Order

# Post Object (Posts Table)
class dbpost(db.Model):
	postid = db.Column('postid', db.Integer, primary_key = True, autoincrement=True)		# Post ID (Primary Key)
	category = db.Column('category', db.Integer, db.ForeignKey('dbcategory.catid'), nullable=False)	# Defining a foreign key
	title = db.Column('title', db.String(32), nullable=True)					# Post Title
	content = db.Column('content', db.String(512), nullable=False) 					# Post Content
	gdatetime = db.Column('datetime', db.String(24), nullable=False)				# Post Date/Time
	comments = db.Column('comments', db.Integer, nullable=False)					# Number of comments on each post
	mediaaddr = db.Column('mediaaddr', db.String(256), nullable=True)				# Multimedia File (Image) Address
	posts = db.relationship('dbcomment', backref=db.backref("dbcomment", uselist=False))		# Defining a foreign key (backref to pid in comments table!)
	# Constructor
	def __init__(self, title: str, content: str, gdatetime: str, comments: int, category: int, mediaaddr: str):
		self.title = title		# Post Title
		self.content = content		# Post Content
		self.category = category	# Post Category
		self.gdatetime = gdatetime	# Post Date/Time
		self.comments = comments	# Number of comments on each post
		self.mediaaddr = mediaaddr	# Multimedia File (Image) Address
	
# Comment Object (Comments Table)
class dbcomment(db.Model):
	cmtid = db.Column('commentid', db.Integer, primary_key = True, autoincrement=True)	# Comment ID (Primary Key)
	pid = db.Column('postid', db.Integer, db.ForeignKey('dbpost.postid'), nullable=False)	# Post ID (Foreign Key)
	content = db.Column('content', db.String(256), nullable=False) 				# Comment Content
	gdatetime = db.Column('datetime', db.String(20), nullable=False)			# Comment Date/Time
	name = db.Column('name', db.String(24), nullable=False) 				# Comment's Author's Name
	website = db.Column('website', db.String(128), nullable=True) 				# Comment's Author's Website
	emailaddr = db.Column('emailaddr', db.String(40), nullable=True) 			# Comment's Author's EMail Address
	# Constructor
	def __init__(self, pid: int, content: str, gdatetime: str, name: str, website: str, emailaddr: str):
		self.pid = pid			# Post ID (Foreign Key)
		self.content = content		# Comment Content
		self.gdatetime = gdatetime	# Comment Date/Time
		self.name = name		# Comment Author's Name
		self.website = website		# Comment Author's Website
		self.emailaddr = emailaddr	# Comment Author's EMail Address

# Tag Object (Tags Table)
class dbtag(db.Model):
	tagid = db.Column('tagid', db.Integer, primary_key = True, autoincrement=True)	# Tag ID (Primary Key)
	keyword = db.Column('keyword', db.String(512), nullable=False, unique=True)	# Tag Keyword
	frequency = db.Column('frequency', db.Integer, nullable=False)			# Tag Frequency
	popularity = db.Column('popularity', db.Integer, nullable=False)		# Tag Popularity
	# Constructor
	def __init__(self, keyword: str, frequency: int, popularity: int):
		self.keyword = keyword		# Tag Keyword
		self.frequency = frequency	# Tag Frequency
		self.popularity = popularity	# Tag Popularity

# Link Object (Links Table)
class dblink(db.Model):
	linkid = db.Column('linkid', db.Integer, primary_key = True, autoincrement=True)	# Link ID (Primary Key)
	name = db.Column('name', db.String(24), nullable=False, unique=True)			# Link Name
	address = db.Column('address', db.String(256), nullable=False, unique=True)		# Link Address
	order = db.Column('order', db.Integer, nullable=False)					# Link Order
	# Constructor
	def __init__(self, name: str, address: str, order: int):
		self.name = name	# Link Name
		self.address = address	# Link Address
		self.order = order	# Link Order

# This function will look for translation of the given string in translation.json file
def tr(text: str) -> str:
	''' Looks for translation of 'text' in translation.json file
	
	Parameters
	----------
	text : str
		Persian/Farsi string to lookup in translation.json file
	
	Returns
	-------
	str
		mapped string to 'text' in translation.json file
	'''
	# This will prevent some errors!
	translate = {}
	# Open translation.json file
	try :
		with open('translation.json', 'r', encoding='utf-8') as translations :
			translate = json.load(translations) # Load translation.json file to memory as translate object
	except (FileNotFoundError, ValueError) : # This exception means there's no translation.json file
		# So We'll return the given persian/farsi text
		return text
	# Return mapped string to 'text' in the translation.json file
	try :
		# Return translation if it exists or return the given string if there's no translation!
		return translate[text] if translate[text] else text
	except KeyError : # This exception means there's no match for given string
		# So We'll return the given persian/farsi text
		return text

# Config page form
class ConfigForm (FlaskForm):
	title = StringField('title', validators=[DataRequired(), Length(min=1, max=64)], render_kw={'maxlength': 64})
	desc = StringField('desc', validators=[DataRequired(), Length(min=1, max=256)], render_kw={'maxlength': 256})
	dispname = StringField('dispname', validators=[DataRequired(), Length(min=1, max=32)], render_kw={'maxlength': 32})
	mailaddr = StringField('mailaddr', validators=[DataRequired(), Email(), Length(min=3, max=254)], render_kw={'maxlength': 254})
	dtformat = StringField('dtformat', validators=[DataRequired(), Length(min=2, max=32)], render_kw={'maxlength': 32})
	calendar = SelectField('calendar', validators=[DataRequired()], choices=[('Gregorian', tr('Gregorian')), ('Jalali', tr('Jalali'))])
	currpwd = PasswordField('currpwd', validators=[InputRequired(), Length(min=5, max=128)], render_kw={'minlength' : 5, 'maxlength': 128})
	newpwd = PasswordField('newpwd', validators=[Optional(), Length(min=8, max=128), EqualTo('confirmpwd')], id='pwd1' \
		, render_kw={'minlength' : 8, 'maxlength': 128})
	confirmpwd = PasswordField('confirmpwd', validators=[Optional(), Length(min=8, max=128), EqualTo('newpwd')], id='pwd2' \
		, render_kw={'minlength' : 8, 'maxlength': 128})
	ppp = IntegerField('ppp', validators=[InputRequired(), NumberRange(min=1, max=9999999999999999)], render_kw={'maxlength': 16})

# Comment page form
class CommentForm (FlaskForm):
	name = StringField('name', validators=[DataRequired(), Length(min=1, max=24)], render_kw={'maxlength': 24})
	mailaddr = StringField('mailaddr', validators=[Optional(), Email(), Length(min=3, max=40)], render_kw={'minlength' : 3, 'maxlength': 40})
	website = StringField('website', validators=[Optional(), URL(), Length(min=3, max=40)], render_kw={'minlength' : 3, 'maxlength': 40})
	content = StringField('content', validators=[DataRequired(), Length(min=1, max=255)], render_kw={'maxlength': 255})
	postid = IntegerField('postid', validators=[InputRequired(), NumberRange(min=1, max=9999999999999999)], widget=HiddenInput())

# Post page form
class PostForm (FlaskForm):
	category = SelectField('category', coerce=int, validators=[DataRequired()])
	title = StringField('title', validators=[DataRequired(), Length(min=1, max=32)], render_kw={'maxlength': 32})
	content = StringField('content', validators=[DataRequired(), Length(min=1, max=256)], widget=TextArea() \
		, render_kw={'rows': 5, 'maxlength': 256})
	mediaaddr = StringField('mediaaddr', validators=[Optional(), Length(min=1, max=256)], render_kw={'maxlength': 256})
	postid = IntegerField('postid', validators=[Optional(), NumberRange(min=1, max=9999999999999999)], widget=HiddenInput())

# This function replaces all hashtags in 'rawText' with linked hashtags 
# 'url' must only contain domain name and script path (send request.script_root as its value!)
def prcText(rawText: str, url: str) -> str:
	'''
	Replaces all hashtags in the 'rawText' with linked hashtags 
	(Adds html <a> tag to all hashtags in the 'rawText' and links them to their page!)
	for example calling prcText('hello #dear user!', 'https://www.site.com/blog/') will return the following string :
	"hello <a href='https://www.site.com/blog/?tag=dear' class='hashtag'>#dear</a> user!"
	
	Parameters
	----------
	rawText : str
		The raw string (usually post content which is stored in database) which may contain some hashtags
	url : str
		Address of our script including domain name (for example : https://www.site.com/blog/)
		Send request.script_root as its value if you don't know how to use it
	
	Returns
	-------
	str
		a string containing 'rawText' content but hashtags are replaced with linked (<a href="hashtag page">) hashtags!
	'''
	# Find all hashtags using regex
	hashTags = re.findall(r"#(\w+)", rawText)
	# Replace each hashtag with a link to that hashtag
	for hashTag in set(hashTags):
		rawText = rawText.replace('#' + hashTag, "<a href='" \
		+ url + "/?tag=" + hashTag + \
		"' class='hashtag'>#" + hashTag + "</a>")
		
	# Replace new lines with html <br> tag!
	rawText = rawText.replace('\n', '<br>')
	# Return the produced string to appear on the requested page
	return Markup(rawText)
	
# This function will format date/time
def formatDateTime(strDateTime: str, strFormat: str) -> str:
	'''
	Formats the 'strDateTime' using the 'strFormat' value
	Also converts the gregorian Date/Time to jalali Date/Time 
	
	Parameters
	----------
	strDateTime : str
		a string which must contain a Date/Time in '%Y-%m-%d %H:%M:%S' format
	strFormat : str
		a string which must contain a format string like '%Y-%m-%d %H:%M:%S'
	
	Returns
	-------
	str
		a string which contains a date/time equal to 'strDateTime' but formatted like 'strFormat'
	'''
	# Check if Jalali Calendar is enabled or not
	#We'll try opening the config file
	try :
		with open('config.json', 'r') as configFile :
			config = json.load(configFile) # This will load config file to the memory as config object
	except FileNotFoundError : # This exception means that our program is not installed and configured yet!
		# So we'll call install() to make the config and database files and redirect user to config page
		return render_template("config.html", config=install()) 
	# This is where we keep the result!
	result = ''
	
	days = {0:tr('Monday'), 1:tr('Tuesday') , 2:tr('Wednesday') \
		, 3:tr('Thursday'), 4:tr('Friday'), 5:tr('Saturday'), 6:tr('Sunday')}
	# Convert strDateTime to a date/time object
	gdt = datetime.datetime.strptime(strDateTime, '%Y-%m-%d %H:%M:%S')
	jdt = jdatetime.GregorianToJalali(gdt.year, gdt.month, gdt.day)
	
	if config['calendar'] == 'Jalali' : # If Jalali Calendar is enabled!
		# We'll use the Jalali Calendar
		# Jalali months
		jmonths = {1:tr('Farvardin'), 2:tr('Ordibehesht'), 3:tr('Khordad') \
			, 4:tr('Tir'), 5:tr('Mordad'), 6:tr('Shahrivar'), 7:tr('Mehr') \
			, 8:tr('Aban'), 9:tr('Azar'), 10:tr('Dey'), 11:tr('Bahman'), 12:tr('Esfand')}
		
		result = strFormat.replace('%Y', str(jdt.jyear))
		result = result.replace('%m', str(jdt.jmonth))
		result = result.replace('%B', jmonths[jdt.jmonth])
		result = result.replace('%d', str(jdt.jday))\
		
	elif config['calendar'] == 'Gregorian' : # If Jalali Calendar is disabled
		# We'll use the Gregorian Calendar
		# Gregorian months
		gmonths = {1:tr('January'), 2:tr('February'), 3:tr('March') \
			, 4:tr('April'), 5:tr('May'), 6:tr('June'), 7:tr('July') \
			, 8:tr('August'), 9:tr('September'), 10:tr('October') \
			, 11:tr('November'), 12:tr('December')}
		
		result = strFormat.replace('%Y', str(gdt.year))
		result = result.replace('%m', str(gdt.month))
		result = result.replace('%B', gmonths[gdt.month])
		result = result.replace('%d', str(gdt.day))
	
	result = result.replace('%A', days[gdt.weekday()])
	result = result.replace('%H', str(gdt.hour))
	result = result.replace('%M', str(gdt.minute))
	result = result.replace('%S', str(gdt.second))
	result = result.replace('%N', '')
	
	return result

# After deleting or editing a post we'll call this function to delete or reduce the frequncy of removed hashtags
def deleteTag(hashTag: str):
	'''
	Checks a hashtag's frequency in the database And performs the following tasks:
	If it's greater than 1 then decrease it by 1
	Else if it's less or equal to 1 then remove the hashtag from the database
	
	Parameters
	----------
	hashtag : str
		a string which must contain only a hashtag without # (for example : 'blog')
	'''
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

# We'll use this decorator before any function that requires to check user privileges
def authentication_required(func):
	'''
	A decorator which is used before any function that requires to check user privileges
	and check if user has admin privileges or not! if user doesn't have admin privileges
	then we'll continue serving them as a user and not admin
	Use this decorator before any function that requires to check session['logged_in'] value.
	'''
	@functools.wraps(func)
	def authenticate(*args, **kwargs):
		# If user didn't login yet then we'll save (logged_in = False) for his session!
		if not 'logged_in' in session :
			session['logged_in'] = False
		return func(*args, **kwargs)
	return authenticate

# We'll use this decorator before any function that requires admin privilages to check if user is admin or not
def login_required(func):
	'''
	A decorator which is used before any function that requires admin privileges to get executed!
	if user doesn't have admin privileges then we'll stop serving them and show them 403 error page
	instead of executing the requested function!
	'''
	@functools.wraps(func)
	@authentication_required
	def checkPrivileges(*args, **kwargs):
		# If 'logged_in' is False then user has no admin privileges
		if session['logged_in'] == False :
			# Render error page 403 and return error code 403 'Forbidden'
			return render_template('403.html'), 403
		return func(*args, **kwargs) 
	return checkPrivileges

# 400 error page
@app.errorhandler(400)
def error400(e):
	'''
	Renders our custom 400 error page and returns error code 400 'Bad Request' to the client
	'''
	return render_template('400.html'), 400

# 404 error page
@app.errorhandler(404)
def error404(e):
	'''
	Renders our custom 404 error page and returns error code 404 'Not Found' to the client
	'''
	return render_template('404.html'), 404

# This function handles our main page
@app.route("/")
@authentication_required
def index():
	'''
	Renders the main page or Calls install() if blog is not configured yet
	It also handles increasing the hashtags popularity if user clicks on a specific hashtag
	and requests its page
	'''
	# Check if config file exists (if application is already installed and configured)
	try :
		with open('config.json', 'r') as configFile :
			config = json.load(configFile) # This will load config file to the memory as config object
	except FileNotFoundError : # This exception means that our program is not installed and configured yet!
		# So we'll call install() to make the config and database files and redirect user to config page
		return render_template("config.html", config=install(), form=ConfigForm())
	# If someone looks for a specific hashtag we'll increase its popularity by 1 
	# Get the hashtag from the request
	tag  = request.args.get('tag', default = '', type = str)
	# Find the hashtag in database
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
	favtags = dbtag.query.order_by(dbtag.popularity.desc()).limit(4).all()
	# Find 4 most used hashtags and save it to 'frqtags' array
	frqtags = dbtag.query.order_by(dbtag.frequency.desc()).limit(4).all()
	# Find all links and save it to 'links' array
	links = dblink.query.order_by(dblink.order).all()
	# Render the page with the provided data!
	return render_template("index.html", config = config, categories = categories, favtags = favtags, frqtags = frqtags, links = links, admin=session['logged_in'])

# This function sends the posts to the client
@app.route("/page", methods=['GET'])
@limiter.limit("60/second")
@authentication_required
def page():
	'''
	Finds the posts which is requested by user and generates the requested page 
	'''
	# Get data from the request
	pageNum =  request.args.get('page', default = 2, type = int)
	search = request.args.get('search', default = '', type = str)
	category = request.args.get('category', default = -1, type = int)
	sort = request.args.get('sort', default = 'descdate', type = str)
	tag  = request.args.get('tag', default = '', type = str)
	# We'll use this object to execute database queries and find the posts which user requested!
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
	# Load config file to the memory as config object
	with open('config.json', 'r') as configFile :
		config = json.load(configFile)
		# Get ppp value from config object and save it in a variable (ppp means Posts Per Page) 
		ppp = config['ppp']
		# Get date/time format
		dtformat = config['dtformat']
	# Limit the results to the number of Posts Per Page
	results = query.offset(pageNum * ppp).limit(ppp)
	# Send "END." if there's no more results to send with status code 200 which means the request was successful
	if results.count() == 0 :
		return Response(response="END.", status=200, mimetype='text/html')
	# This small block of code will handle the positioning of the posts (should they appear on the right side or the left side of the timeline?!)
	if (ppp % 2) == 1 and (pageNum % 2) == 1 :
		c = 0
	else :
		c = 1
	# Array of our posts (results)
	posts = []
	# We'll use this loop to run the 'prcText' function on each post's content
	# and replace all hashtags in each post with linked hashtags and format its date/time
	for result in results :
		post = {} # A single post (we'll assign its values below!)
		# We'll replace hashtags with linked hashtags using the 'prcText' function
		post['content'] = prcText(result.__dict__['content'], request.script_root)
		# And format date/time using the 'formatDateTime' function
		post['datetime'] = formatDateTime(result.__dict__['gdatetime'], dtformat)
		post['gdatetime'] = result.__dict__['gdatetime']
		# Rest is the same without any modification!
		post['postid'] = result.__dict__['postid']
		post['title'] = result.__dict__['title']
		post['category'] = result.__dict__['category']
		post['comments'] = result.__dict__['comments']
		post['mediaaddr'] = result.__dict__['mediaaddr']
		# Put this post in our results
		posts.append(post)
	# Render results
	return render_template("page.html", posts=posts, c=c, mimetype="text/html", admin=session['logged_in'])

# This function handles config page and configurations
@app.route("/config", methods=['POST', 'GET'])
@login_required
def config(): # NOTE: Need more test!
	'''
	Renders the config page and stores new configs in the config file
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required

	# Create a new config object (we'll load data in it later!)
	config = {}
	# Load config file to the memory as config object
	with open('config.json', 'r') as configFile :
		config = json.load(configFile)
	# Form object which holds the request data 
	form = ConfigForm(request.form)
	# If user opened the config page without requesting to change the config
	if request.method == 'GET':
		# Fill the form with current config
		form.title.default = config['title']
		form.desc.default = config['desc']
		form.dispname.default = config['dispname']
		form.mailaddr.default = config['mailaddr']
		form.ppp.default = config['ppp']
		form.dtformat.default = config['dtformat']
		form.calendar.default = config['calendar']
		form.currpwd.default = config['pwd']
		form.process(data=config)
		# Render the config page and fill it with current (old) config values
		return render_template("config.html", form=form)
	# Validate the request data if there's a request to change the config
	if form.validate_on_submit():
		# We'll make a new config object
		newconfig = {}
		# And assign the user requested values to this new config object
		newconfig['title'] = form.title.data
		newconfig['desc'] = form.desc.data
		newconfig['dispname'] = form.dispname.data
		newconfig['mailaddr'] = form.mailaddr.data
		newconfig['ppp'] = form.ppp.data
		newconfig['dtformat'] = form.dtformat.data
		newconfig['calendar'] = form.calendar.data
		newpassword = form.newpwd.data
		# Hash the password entered by user
		currpwd = hashlib.md5(form.currpwd.data.encode('utf-8'))
		# Check if the current password is the same as the one entered by user
		if config['pwd'] != currpwd.hexdigest() :
			# Warn user if password doesn't match!
			flash(tr('Error! You have entered the wrong password, Please try again.'))
			# And render the config page without changing the config
			render_template("config.html", form=form), 401
		# If admin requested to change the password
		if newpassword != '' :
			# Hash the new password
			newpwd = hashlib.md5(newpassword.encode('utf-8'))
			# Save hash to config object
			newconfig['pwd'] = newpwd.hexdigest()
		else :
			# If admin didn't request to change the password then we'll use the current password in new config
			newconfig['pwd'] = config['pwd']
		# If everything goes well, we'll save the new config to the config file
		# Open config file for output and erase its data
		with open('config.json', 'w') as configFile:
			# Save new config
			json.dump(newconfig, configFile)
		# Render the config page and fill it with newconfig values
		return render_template("config.html", form=form)
	else: # If there was any problem during request validation
		# Raise 'ValidationError' exception and render 400 'Bad Request' error page!
		raise ValidationError
		return render_template('400.html'), 400

# This function handles viewing and saving comments
@app.route("/comments", methods=['POST', 'GET'])
@authentication_required
def comments(): # NOTE: Need more test and review!
	'''
	Renders the comments page for a specific post and stores new comments in the database
	'''
	# Get 'postid' from the request
	postid = request.args.get('postid', default=-1, type=int)
	# Find the post which this new comment belongs to
	post = dbpost.query.filter(dbpost.postid == postid).first()
	# Check if the post exists and it's not a bad request!
	if post is None:
		# Renders our custom 400 error page and returns error code 400 'Bad Request' to the client
		return render_template('400.html'), 400
	# Form object which holds the request data
	# We'll set postid value to hidden field
	form = CommentForm(request.form, postid=postid)
	# Validate the request data
	# and check if there's a new comment
	if form.validate_on_submit():
		# Get the data from the request
		name = form.name.data
		mailaddr = form.mailaddr.data
		website = form.website.data
		content = form.content.data
		postid = form.postid.data
		gdatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		# Create a new comment with the data provided above
		comment = dbcomment(postid, content, gdatetime, name, website, mailaddr)
		# Increase the number of comments of the post which this comment belongs to
		post.comments = post.comments + 1
		# Add this new comment to the database
		db.session.add(comment)
		# Save changes to database
		db.session.commit()
	# Load all comments that belong to a specific post from the database
	results = dbcomment.query.filter(dbcomment.pid == postid).all()
	# Load config file to the memory as config object
	with open('config.json', 'r') as configFile :
		config = json.load(configFile)
		# Get date/time format
		dtformat = config['dtformat']
	# Array of our comments (results)
	comments = []
	# We'll use this loop to run the 'formatDateTime' function on each comment to format its date/time
	for result in results :
		comment = {} # A single comment (we'll assign its values below!)
		# And format date/time using the 'formatDateTime' function
		comment['datetime'] = formatDateTime(result.__dict__['gdatetime'], dtformat)
		# Rest is the same without any modification!
		comment['content'] = result.__dict__['content']
		comment['cmtid'] = result.__dict__['cmtid']
		comment['name'] = result.__dict__['name']
		comment['website'] = result.__dict__['website']
		comment['emailaddr'] = result.__dict__['emailaddr']
		# Put this comment in our results
		comments.append(comment)
	return render_template("comments.html", comments=comments, postid=postid, form=form, admin=session['logged_in'])

# This function handles removing comments 
@app.route("/deletecomment", methods=['GET'])
@login_required
def deletecomment():
	'''
	Removes a comment from the database
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
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
	'''
	Renders the share page
	'''
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
	# Render 400 error page and returns error code 400 'Bad Request' to the client
	return render_template("400.html"), 400

# This function handles 'Post' page which is used for saving new posts and editing existing posts in the database
@app.route("/post", methods=['POST', 'GET'])
@login_required
def post(): # NOTE: Need more test and review!
	'''
	Renders the post page and stores new or edited posts in the database
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
	# If there's no category then we'll make one! (otherwise an error will occur!)
	if dbcategory.query.count() == 0 :
		category = dbcategory(tr('Other'), 0)
		db.session.add(category)
		# Save changes to the database
		db.session.commit()
	# Get list of categories
	categories = dbcategory.query.all()
	# Get 'id' from the requested url, if it's empty we'll assign it '-1' 
	id =  request.args.get('id', default = -1, type = int)
	# Create an empty post we'll fill it later
	# Find the post by its id
	post = dbpost.query.filter(dbpost.postid == id).first()
	# If there's a post with that id
	if post is not None:
		# Create a form and fill it with post data
		form = PostForm(request.form, postid=post.postid, title=post.title, \
			mediaaddr=post.mediaaddr, content=post.content, category=post.category)
	else:
		# Create an empty form
		form = PostForm(request.form)
	# Get list of all categories and put them in category select field
	form.category.choices = [(cat.catid, cat.name) for cat in dbcategory.query.all()]
	# If there's any data from user
	if form.validate_on_submit() :
		# Get data from the request
		category = form.category.data
		title = form.title.data
		content = form.content.data
		mediaaddr = form.mediaaddr.data
		postid = form.postid.data
		# If postid is not empty then user is editing an existing post
		if postid :
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
		# If postid is empty then it's a new post and user is not editing an existing post
		else :
			# Get the Date/Time
			gdatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			# New posts don't have any comment when they're getting published!
			comments = 0
			# Create a new post with the provided data
			newpost = dbpost(title=title, content=content, gdatetime=gdatetime, comments=comments \
				, category=category, mediaaddr=mediaaddr)
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
				# Increase its frequency by 1
				tag.frequency = tag.frequency + 1
			# Save changes to the database
			db.session.commit()
		# Return to index and let the user see the new post
		return redirect(url_for('index'))
	# Render the page and fill it with the available data
	return render_template("post.html", categories = categories, form=form, admin=session['logged_in'])
	
# This function Removes the post from the database and execute the 'deleteTag' function for its hashtags and remove its comments
def removepost(id: int):
	'''
	Removes a single post from the database
	
	Parameters
	----------
	id : int
		Post ID, We'll use this ID (Primary Key) to find the post on database 
	'''
	# Find the post in the database
	post = dbpost.query.filter(dbpost.postid == id)
	# Delete all the comments that belong to this specific post
	dbcomment.query.filter(dbcomment.pid == id).delete()
	# Get post content
	content = post.first().content
	# And find all the hashtags in this content
	hashTags = re.findall(r"#(\w+)", content)
	# Execute the 'deleteTag' function for all the hashtags found in the content
	for hashTag in set(hashTags):
		# remove the hashtag or reduce its frequency
		deleteTag(hashTag)
	# Delete the post
	post.delete()
	# Save changes to the database
	db.session.commit()

# This function handles requests for deleting posts
@app.route("/deletepost", methods=['GET'])
@login_required
def deletepost():
	'''
	Gets Post ID from the request and calls removepost(id) to remove that specific post from the database 
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
	# If it's not a bad request
	if 'id' in request.args :
		# Get postid
		id =  request.args.get('id', type = int)
		# Return "Failure!" if 'id' is wrong!
		if dbpost.query.filter(dbpost.postid == id).first() is None :
			return ('', 400)
		# Call the 'removepost' function to remove the post from the database
		removepost(id)
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles showing single posts
@app.route("/show", methods=['GET'])
@authentication_required
def show():
	'''
	Renders the show page which is used to show a single post and its details!
	'''
	# Get 'id' from the requested url, if it's empty we'll assign it '-1' 
	id =  request.args.get('id', default = -1, type = int)
	# Find the post which user requested
	result = dbpost.query.filter(dbpost.postid == id).first()
	# Check if the requested post exists
	if result is None :
		# Render 400 error page and returns error code 400 'Bad Request' to the client
		return render_template('400.html'), 400
	# Find its category
	category = dbcategory.query.filter(dbcategory.catid == result.category).first()
	# Load config file to the memory as config object
	with open('config.json', 'r') as configFile :
		config = json.load(configFile)
		# Get date/time format
		dtformat = config['dtformat']	
	# Create an empty post! We'll use it to send data to the client
	post = {}
	# Replace hashtags with linked hashtags!
	post['content'] = prcText(result.content, request.script_root)
	# Format date/time
	post['datetime'] = formatDateTime(result.gdatetime, dtformat)
	# Copy rest of the data
	post['postid'] = result.__dict__['postid']
	post['gdatetime'] = result.__dict__['gdatetime']
	post['title'] = result.__dict__['title']
	post['category'] = result.__dict__['category']
	post['comments'] = result.__dict__['comments']
	post['mediaaddr'] = result.__dict__['mediaaddr']
	# Show the post which was requested by user
	return render_template("show.html", post=post, category=category, admin=session['logged_in'])

# This function handles creating new categories
@app.route("/newcategory", methods=['GET'])
@login_required
def newcategory():
	'''
	Creates a new category using the data sent by user
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
	# If it's not a bad request
	if 'name' in request.args :
		# Get 'name' from request
		name = request.args.get('name')
		order = 0
		# Return "Failure!" if name is empty
		if name == '' :
			return ('', 400)
		# Warn user if a category with the same name already exists!
		if dbcategory.query.filter(dbcategory.name == name).first() is not None :
			flash(tr("Error! A category with the same name '%s' already exists. Please choose a new name!") % name)
			# Return "Success!"
			return ('', 200)
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
@login_required
def editcategory():
	'''
	Changes a category values to the values sent by user
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
	# If it's not a bad request
	if 'id' in request.args :
		# Get new category name from the request
		id =  request.args.get('id', type=int)
		name = request.args.get('name', type=str, default='')
		order = 0
		# Return "Failure!" if 'id' is wrong!
		if dbcategory.query.filter(dbcategory.catid == id).first() is None :
			return ('', 400)
		# Return "Failure!" if name is empty
		if name == '' :
			return ('', 400)
		# Return "Success!" if there's no change!
		if dbcategory.query.filter(dbcategory.catid == id).first().name == name :
			# Return "Success!"
			return ('', 200)
		# Warn user if a category with the same name already exists!
		if dbcategory.query.filter(dbcategory.name == name).first() is not None :
			flash(tr("Error! A category with the same name '%s' already exists. Please choose a new name!") % name)
			# Return "Success!"
			return ('', 200)
		# Find the category
		category = dbcategory.query.filter(dbcategory.catid == id).first()
		# Change the category name to the one requested by user 
		category.name = name
		# Save changes to the database
		db.session.commit()
		# Return "Success!"
		return ('', 200)

# This function handles removing the categories
@app.route("/removecategory", methods=['GET'])
@login_required
def removecategory():
	'''
	Removes a category from the database
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
	# If it's not a bad request
	if 'id' in request.args :
		# Get the category id from the request
		id = request.args.get('id', type=int)
		# Return "Failure!" if 'id' is wrong!
		if dbcategory.query.filter(dbcategory.catid == id).first() is None :
			return ('', 400)
		# Find the category by its id in the database and delete it
		dbcategory.query.filter(dbcategory.catid == id).delete()
		# After deleting the category we'll delete all the posts that belong to that category too
		# There's no Do..While in python so we'll use an endless While(True) Loop
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
			category = dbcategory(tr('Other'), 0)
			db.session.add(category)
		# Save changes to the database
		db.session.commit()
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles adding new links to the link box
@app.route("/addlink", methods=['GET'])
@login_required
def addlink():
	'''
	Creates a new link using the data sent by user
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
	# If it's not a bad request
	if 'address' in request.args \
	and 'name' in request.args :
		# Get the data from the request
		name = request.args.get('name', type=str)
		addr = request.args.get('address', type=str)
		address = urllib.parse.unquote(addr)
		order = 0
		# Return "Failure!" if name or address is empty
		if name == '' or address == '' :
			return ('', 400)
		# Warn user if a link with the same name already exists!
		if dblink.query.filter(dblink.name == name).first() is not None :
			flash(tr("Error! A link with the same name '%s' already exists. Please choose a new name!") % name)
			# Return "Success!"
			return ('', 200)
		# Warn user if a link with the same address already exists!
		if dblink.query.filter(dblink.address == address).first() is not None:
			flash(tr("Error! A link with the same address '%s' already exists. Please enter a new address!") % address)
			# Return "Success!"
			return ('', 200)
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
@login_required
def editlink():
	'''
	Changes a link values to the values sent by user
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
	# If it's not a bad request
	if 'id' in request.args :
		# Get the data from the request
		id =  request.args.get('id', type=int)
		name = request.args.get('name', type=str)
		addr = request.args.get('address', type=str)
		address = urllib.parse.unquote(addr)
		order = 0
		# Return "Failure!" if 'id' is wrong!
		if dblink.query.filter(dblink.linkid == id).first() is None :
			return ('', 400)
		# Return "Failure!" if name or address is empty
		if name == '' or address == '' :
			return ('', 400)
		# Return "Success!" if there's no change!
		if dblink.query.filter(dblink.linkid == id).first().name == name \
		and dblink.query.filter(dblink.linkid == id).first().address == address:
			# Return "Success!"
			return ('', 200)
		# Warn user if a different link with the same name already exists!
		if dblink.query.filter(dblink.linkid == id).first().name != name \
		and dblink.query.filter(dblink.name == name).first() is not None :
			flash(tr("Error! A link with the same name '%s' already exists. Please choose a new name!") % name)
			# Return "Success!"
			return ('', 200)
		# Warn user if a different link with the same address already exists!
		if dblink.query.filter(dblink.linkid == id).first().address != address \
		and dblink.query.filter(dblink.address == address).first() is not None:
			flash(tr("Error! A link with the same address '%s' already exists. Please enter a new address!") % address)
			# Return "Success!"
			return ('', 200)
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
@login_required
def removelink():
	'''
	Removes a link from the database
	'''
	# This page requires admin privileges so we'll check if it's requested by admin or not by using @login_required
	
	# If it's not a bad request
	if 'id' in request.args :
		# Get link's id from the request
		id = request.args.get('id', type=int)
		# Return "Failure!" if 'id' is wrong!
		if dblink.query.filter(dblink.linkid == id).first() is None :
			return ('', 400)
		# Find the link by its id and delete it
		dblink.query.filter(dblink.linkid == id).delete()
		# Save changes to the database
		db.session.commit()
		# Return "Success!"
		return ('', 200)
	# Return "Failure!"
	return ('', 400)

# This function handles the login process and user authentication 
@app.route("/login", methods=['POST'])	# Limit the number of allowed requests to 
@limiter.limit("3/minute") 		# 3	per minute
@limiter.limit("15/hour")		# 15	per hour
@limiter.limit("45/day")		# 45	per day
def login():
	'''
	Gets the password sent by user and compare it with the password stored in the config file
	If they're the same then sets session['logged_in'] value to true which will grant user
	admin privileges. (the password which is stored in the config file is hashed using the md5 algorithm!)
	'''
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
			# Ask user to enter the password again
			flash(tr('Error! You have entered the wrong password, Please try again.'))
	# Return to the main page
	return redirect(url_for('index'))

# This function handles the logout process
@app.route("/logout")
def logout():
	'''
	Removes 'logged_in' from session which will revoke all admin privileges
	'''
	# Remove logged_in from the session
	session.pop('logged_in', None)
	# Return to the main page
	return redirect(url_for('index'))

# This function handles the installation process and creating the config file and the database
def install():
	'''
	Calls db.create_all() to create the database and its tables
	And creates a basic config and return it as result
	
	Returns
	-------
	dictionary
		a Dictionary which contains the default config
	'''
	# Create the database file and its tables
	db.create_all()
	# Create a category (to prevent errors!)
	if dbcategory.query.count() == 0 :
		category = dbcategory(tr('Other'), 0)
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
		newconfig['dispname'] = tr('Admin')
		newconfig['mailaddr'] = ''
		newconfig['ppp'] = 10
		newconfig['dtformat'] = '%Y %B %d'
		newconfig['calendar'] = 'Jalali'
		# Save the default password (md5 hash of 'admin') in our new config
		newpwd = hashlib.md5('admin'.encode('utf-8'))
		newconfig['pwd'] = newpwd.hexdigest()
		# Create a config file using our new config
		json.dump(newconfig, configFile)
		# Give user admin's password!
		flash(tr('Password') + ' :\n\nadmin')
		# Return this new config object so we can use it to fill the config page fields
		return newconfig

app.register_error_handler(ValidationError, error400)

# If this module is the main program!
if __name__ == '__main__':
	# Run the program (Only for development purposes!)
	app.run(debug=True)