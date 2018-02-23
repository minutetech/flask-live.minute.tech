###################################################################################################################################################################
###################################################################################################################################################################
#########################################  MINUTE.TECH SOURCE CODE by: Douglas James with Minute.tech LLC #########################################################
###################################################################################################################################################################
###################################################################################################################################################################

###### INCLUDED LIBRARIES ######
import os, sys, os.path
from flask import Flask, render_template, flash, request, url_for, redirect, session, send_file, send_from_directory
# WTForms
from wtforms import Form, BooleanField, TextField, PasswordField, SelectField, RadioField, TextAreaField, DateField, DateTimeField, StringField, validators
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired
# Flask WTF 
# -different than WTForms!
# -has reCAPTCHA!
# -builds ontop of Flask and wtforms
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
# For secure file uploads
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
# To encrypt the password
from passlib.hash import sha256_crypt
# For SQL injection
from MySQLdb import escape_string as thwart
from functools import wraps
# My custom database connection function
from dbconnect import connection
# UPLOAD_FOLDER = '/var/www/FlaskApp/FlaskApp/static/user_info/prof_pic'
# ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])
app = Flask(__name__, static_folder='static')
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Key cross-referenced from flaskapp.wsgi
app.config['SECRET_KEY'] = 'quincyisthebestdog11'

## GLOBALS
# For selecting question from list
select_q = 0
# Checking if session.logged_in is set after a successfully login
password_confirm = 0
tech_password_confirm = 0

#############  FUNCTIONS  ##################

#temporary to ask questions on homepage
#will eventually want a new user to be able to type a question out, but directed to sign up page immediatly, but their question is still saved and placed in database
class AskForm(Form):
    # difficulty = RadioField('Difficulty Rating', choices = [('1','1'), ('2','2'),('3','3'),('4','4'),('5','5')])
    # title = TextField('Title:', [validators.Length(min=5, max=100)])
    body = TextAreaField('Desciption', [validators.Length(min=10, max=2000)])
    # tags = TextField('Tags:', [validators.Optional()])

############################ PAGES #################################
# #/var/www/FlaskApp/FlaskApp/static/user_info/prof_pic
# def allowed_file(filename):
# 	return '.' in filename and \
# 		filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/test/', methods=['GET','POST'])
# def test():
# 	if request.method == 'POST':
# 		if 'file' not in request.files:
# 			flash('No file part')
# 			return redirect(request.url)
# 		file = request.files['file']
# 		if file.filename == '':
# 			flash('No selected file')
# 			return redirect(request.url)
# 		if file and allowed_file(file.filename):
# 			filename = secure_filename(file.filename)
# 			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
# 			return redirect(url_for('test', filename = filename))
# 	return render_template("test.html")



@app.route('/', methods=['GET','POST'])
def homepage():
	#if user posts a question to the pool
	form = AskForm(request.form)
	if request.method == "POST" and form.validate():
		difficulty =  0
		title = 'Not provided'
		body = form.body.data
		tags = 'Not provided'
		priority = 500
		clientcid = session['clientcid']

		c, conn = connection()
		c.execute("INSERT INTO tickets (cid, difficulty, priority, title, tags) VALUES (%s, %s, %s, %s, %s)", (clientcid, difficulty, priority, title, tags))
		conn.commit()
		# Get qid after the ticket is generated after an initial "ask" page request
		c.execute("SELECT qid FROM tickets WHERE cid = (%s) AND title = (%s)", (clientcid, title))
		qid = c.fetchone()[0]
		conn.commit()
		c.execute("INSERT INTO threads (qid, cid, body) VALUES (%s, %s, %s)", (qid, clientcid, body))
		conn.commit()
		c.close()
		conn.close()
		flash("Submission successful. We have added your question to the pool!")
		return redirect(url_for('homepage'))

	else:
		error = "We couldn't post your question, please make sure you filled out all the fields properly and try again!"
		return render_template("main.html", form=form)

#NEED DATABASE FOR THIS

class ContactForm(Form):
    message = TextAreaField('Message', [validators.Length(min=10, max=2000)])
    email = TextField('Email', [validators.Optional()])

@app.route('/about/', methods=['GET','POST'])
def about():
	uid = 0
	try:
		form = ContactForm(request.form)
		if request.method == "POST" and form.validate():
			message = form.message.data
			# If user is logged in, set email to their email, otherwise, empty (on html side)
			email = form.email.data
			
			# Get user ID
			if session.get('logged_in') == True:
				if session['logged_in'] == 'client':
					uid = session['clientcid']
				if session['logged_in'] == 'tech':
					uid = session['techtid']

			# Throw data in database
			c, conn = connection()
			c.execute("INSERT INTO contact (message, email, uid) VALUES (%s, %s, %s)", (message, email, uid))
			conn.commit()
			c.close()
			conn.close()
			flash("Submission successful. We will get back to you as soon as possible!")
			return redirect(url_for('about'))

		else:
			error = "We couldn't post your comment, please make sure you filled out all the fields properly, or try reloading the page and asking again."
			return render_template("about.html", form=form)

	except Exception as e:
		return render_template("500.html", error = e)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_found(e):
    return render_template("405.html")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html")


############################################ TICKET SYSTEM #########################################################

############## CLIENT SECTION ##########################

@app.route('/ask/', methods=['GET','POST'])
def ask():
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST":
			cid = session['clientcid']
			c.execute("UPDATE cpersonals SET launch_email = 1 WHERE cid = (%s)", (cid,))
			conn.commit()
			c.close()
			conn.close()
			flash("Thanks, we got you down!")
			return redirect(url_for('ask'))

		return render_template("ask.html", error = error)

	except Exception as e:
		return render_template("500.html", error = e)

@app.route('/resolved/', methods=['GET','POST'])
def resolved():
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST":
			cid = session['clientcid']
			c.execute("UPDATE cpersonals SET launch_email = 1 WHERE cid = (%s)", (cid,))
			conn.commit()
			c.close()
			conn.close()
			flash("Thanks, we got you down!")
			return redirect(url_for('resolved'))

		return render_template("resolved.html", error = error)

	except Exception as e:
		return render_template("500.html", error = e)

@app.route('/pending/', methods=['GET','POST'])
def pending():
	error = ''
	try:
		c, conn = connection()
		flash(session['prof_pic'])
		if request.method == "POST":
			cid = session['clientcid']
			c.execute("UPDATE cpersonals SET launch_email = 1 WHERE cid = (%s)", (cid,))
			conn.commit()
			c.close()
			conn.close()
			flash("Thanks, we got you down!")
			return redirect(url_for('pending'))

		return render_template("pending.html", error = error)

	except Exception as e:
		return render_template("500.html", error = e)

##############  END CLIENT SECTION ##########################

##############  TECHNICIAN SECTION  ####################
@app.route('/answer/', methods=['GET','POST'])
def answer():
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST":
			tid = session['techtid']
			c.execute("UPDATE tpersonals SET launch_email = 1 WHERE tid = (%s)", (tid,))
			conn.commit()
			c.close()
			conn.close()
			flash("Thanks, we got you down!")
			return redirect(url_for('answer'))

		return render_template("answer.html", error = error)

	except Exception as e:
		return render_template("500.html", error = e)

@app.route('/techresolved/', methods=['GET','POST'])
def techresolved():
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST":
			tid = session['techtid']
			c.execute("UPDATE tpersonals SET launch_email = 1 WHERE tid = (%s)", (tid,))
			conn.commit()
			c.close()
			conn.close()
			flash("Thanks, we got you down!")
			return redirect(url_for('techresolved'))

		return render_template("techresolved.html", error = error)

	except Exception as e:
		return render_template("500.html", error = e)


@app.route('/techroom/?select_q=<select_q>', methods=['GET','POST'])
def techroom(select_q):
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST":
			tid = session['techtid']
			c.execute("UPDATE tpersonals SET launch_email = 1 WHERE tid = (%s)", (tid,))
			conn.commit()
			c.close()
			conn.close()
			flash("Thanks, we got you down!")
			return redirect(url_for('techroom'))

		return render_template("techroom.html", error = error)

	except Exception as e:
		return render_template("500.html", error = e)


@app.route('/techpending/', methods=['GET','POST'])
def techpending():
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST":
			tid = session['techtid']
			c.execute("UPDATE tpersonals SET launch_email = 1 WHERE tid = (%s)", (tid,))
			conn.commit()
			c.close()
			conn.close()
			flash("Thanks, we got you down!")
			return redirect(url_for('techpending'))

		return render_template("techpending.html", error = error)

	except Exception as e:
		return render_template("500.html", error = e)

##############  END TECHNICIAN SECTION  ####################

############################################ END TICKET SYSTEM #########################################################


############################################ ACCOUNT SYSTEM #########################################################
class EditAccountForm(Form):
	first_name = TextField('First Name', [validators.Length(min=1, max=50)])
	last_name = TextField('Last Name', [validators.Length(min=1, max=50)])
	email = TextField('Email Address', [validators.Length(min=6, max=50)])
	phone = TextField('Phone Number', [validators.Length(min=10, max=20)])
	address = TextField('Street Address', [validators.Length(min=6, max=100)])
	city = TextField('City', [validators.Length(min=2, max=50)])
	state = TextField('State', [validators.Length(min=2, max=2)])
	czip = TextField('ZIP', [validators.Length(min=2, max=16)])
	birth_month = TextField('Birthday', [validators.Length(min=2, max=16)])
	birth_day = TextField('&nbsp;', [validators.Length(min=1, max=2)])
	birth_year = TextField('&nbsp;', [validators.Length(min=4, max=4)])
	bio = TextAreaField('Personal Description', [validators.Length(min=1, max=2000)], widget=TextArea())
	# password = PasswordField('Password', [validators.Required(), validators.EqualTo('techconfirm', message ="Passwords must match.")])
	# confirm = PasswordField('Repeat Password')

@app.route('/account/', methods=['GET','POST'])
def account():
	error = ''
	try:
		# Declare form early on, so the form is referenced before assignment
		form = EditAccountForm(request.form)
		if session['logged_in'] == 'client':
			#grab all the clients info
			c, conn = connection()
			email = session['email']
			c.execute("SELECT cid FROM clients WHERE email = (%s)", (email,))
			clientcid = c.fetchone()[0]
			c.execute("SELECT phone FROM clients WHERE email = (%s)", (email,))
			phone = c.fetchone()[0]
			c.execute("SELECT rating FROM clients WHERE email = (%s)", (email,))
			rating = c.fetchone()[0]
			c.execute("SELECT first_name FROM cpersonals WHERE cid = (%s)", (clientcid,))
			first_name = c.fetchone()[0]
			c.execute("SELECT last_name FROM cpersonals WHERE cid = (%s)", (clientcid,))
			last_name = c.fetchone()[0]
			c.execute("SELECT address FROM cpersonals WHERE cid = (%s)", (clientcid,))
			address = c.fetchone()[0]
			c.execute("SELECT city FROM cpersonals WHERE cid = (%s)", (clientcid,))
			city = c.fetchone()[0]
			c.execute("SELECT state FROM cpersonals WHERE cid = (%s)", (clientcid,))
			state = c.fetchone()[0]
			c.execute("SELECT zip FROM cpersonals WHERE cid = (%s)", (clientcid,))
			czip = c.fetchone()[0]
			c.execute("SELECT birth_month FROM cpersonals WHERE cid = (%s)", (clientcid,))
			birth_month = c.fetchone()[0]
			c.execute("SELECT birth_day FROM cpersonals WHERE cid = (%s)", (clientcid,))
			birth_day = c.fetchone()[0]
			c.execute("SELECT birth_year FROM cpersonals WHERE cid = (%s)", (clientcid,))
			birth_year = c.fetchone()[0]
			c.execute("SELECT bio FROM cpersonals WHERE cid = (%s)", (clientcid,))
			bio = c.fetchone()[0]
			c.execute("SELECT reg_date FROM cpersonals WHERE cid = (%s)", (clientcid,))
			reg_date = c.fetchone()[0]
			# For now, just putting the prof_pic url into the BLOB
			c.execute("SELECT prof_pic FROM cpersonals WHERE cid = (%s)", (clientcid,))
			prof_pic = c.fetchone()[0]
			conn.commit()
			c.close()
			conn.close()
			session['clientcid'] = clientcid
			session['phone'] = phone
			session['rating'] = rating
			session['first_name'] = first_name
			session['last_name'] = last_name
			session['address'] = address
			session['city'] = city
			session['state'] = state
			session['czip'] = czip
			session['birth_month'] = birth_month
			session['birth_day'] = birth_day
			session['birth_year'] = birth_year
			session['bio'] = bio
			session['reg_date'] = reg_date
			session['prof_pic'] = prof_pic
			#//END grab all the clients info
			c, conn = connection()
			
			#Get value before placing into textarea-box... 
			#had to do this method because value=session.bio wasnt working in jinja
			form.bio.data = session['bio']
			if request.method == 'POST' and form.validate():
				first_name = form.first_name.data
				last_name = form.last_name.data
				email = form.email.data
				phone = form.phone.data
				address = form.address.data
				city = form.city.data
				state = form.state.data
				czip = form.czip.data
				birth_month = form.birth_month.data
				birth_day = form.birth_day.data
				birth_year = form.birth_year.data
				bio = request.form['bio']
				clientcid = session['clientcid']

				# Currently, when you change to an email that already exists, 
				# it will swap to that profile on page reload of the email you inserted, and will allow an illegal login!!
				# Need to be able to have the email field autofill, but first check if that email is in the database
				# Try using a SQL statement to get everything but the one in the session already
				# and checking the database with the email in session EXCLUDED
				# Could also swap to new page (lots of overhead)
				# Could show and hide it with uk-disabled
				# 

				#check if email already exists
				x = c.execute("SELECT * FROM clients WHERE email = (%s)", (thwart(email),))
				if int(x) > 0 and form.email.data:
					#redirect them if they need to recover an old email from and old account
					flash("That email already has an account, please try a a different email.")
					return render_template('account.html', form=form)

				c.execute("UPDATE clients SET email = %s, phone = %s WHERE cid = (%s)", (email, phone, clientcid))
				c.execute("UPDATE cpersonals SET first_name = %s, last_name = %s, address = %s, city = %s, state = %s, zip = %s, birth_month = %s, birth_day = %s, birth_year = %s, bio = %s WHERE cid = (%s)", (thwart(first_name), thwart(last_name), thwart(address), thwart(city), thwart(state), thwart(czip), birth_month, birth_day, birth_year, bio, clientcid))
				conn.commit()
				c.close()
				conn.close()
				session['first_name'] = first_name
				session['last_name'] = last_name
				session['email'] = email
				session['phone'] = phone
				session['address'] = address
				session['city'] = city
				session['state'] = state
				session['czip'] = czip
				session['birth_month'] = birth_month
				session['birth_day'] = birth_day
				session['birth_year'] = birth_year
				session['bio'] = bio
				flash("Your account is successfully updated.")
				return redirect(url_for('account'))
		else:
			flash("Try logging out and back in again!")

		return render_template("account.html", form=form, error = error)

	except Exception as e:
		return render_template("500.html", error = e)

# #### PROFILE PIC UPLOAD ####
# # Based after https://gist.github.com/greyli/81d7e5ae6c9baf7f6cdfbf64e8a7c037
# # For uploading files

# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# # /var/www/FlaskApp/FlaskApp/static/legal/MinutetechLLC_tos.pdf
# app.config['UPLOADED_PHOTOS_DEST'] = 'static/user_info/prof_pic'
# photos = UploadSet('photos', IMAGES)
# configure_uploads(app, photos)
# patch_request_class(app)  # set maximum file size, default is 16MB

# class ProfilePictureForm(FlaskForm):
# 	prof_pic = FileField(validators=[FileAllowed(photos, u'Image only!')])

# @app.route('/profile_picture_upload/', methods=['GET','POST'])
# def profile_picture_upload():
# 	form = ProfilePictureForm()
# 	cid = str(session['clientcid'])
# 	first_name = session['first_name']
# 	#default_prof_pic = 'app/uploads/photos/static/user_info/prof_pic/default.jpg'
# 	#user_prof_pic = cid+'_'+first_name+'_'+'.png'
# 	if form.validate_on_submit():
# 		# Checks if the prof_pic is set yet. if set, then dont need to delete the old picture on the server
# 		if session['prof_pic'] != url_for('static', filename='user_info/prof_pic/default.jpg'):
# 			#need to delete or move the old prof_pic if it was set! Prevents users from adding too many pictures
# 			os.remove('static/user_info/prof_pic/'+cid+'_'+first_name+'.png')
# 			flash("You already have a file on the server!")
# 		filename = photos.save(form.prof_pic.data, name=cid+'_'+first_name+'.png')
# 		file_url = photos.url(filename) 
# 		session['prof_pic'] = file_url
# 		c, conn = connection()
# 		c.execute("UPDATE cpersonals SET prof_pic = %s WHERE cid = (%s)", (file_url, cid))

# 		conn.commit()
# 		c.close()
# 		conn.close()
# 	else:
# 		file_url = None

# 	return render_template('profile_picture_upload.html', form=form, file_url=file_url)

# #### END PROFILE PIC UPLOAD ####

# TECH ACCOUNT
class TechEditAccountForm(Form):
	techfirst_name = TextField('First Name', [validators.Length(min=1, max=50)])
	techlast_name = TextField('Last Name', [validators.Length(min=1, max=50)])
	techemail = TextField('Email Address', [validators.Length(min=6, max=50)])
	techphone = TextField('Phone Number', [validators.Length(min=10, max=20)])
	techaddress = TextField('Street Address', [validators.Length(min=6, max=100)])
	techcity = TextField('City', [validators.Length(min=2, max=50)])
	techstate = TextField('State', [validators.Length(min=2, max=2)])
	techzip = TextField('ZIP', [validators.Length(min=2, max=16)])
	techbirth_month = TextField('Birthday', [validators.Length(min=2, max=16)])
	techbirth_day = TextField('&nbsp;', [validators.Length(min=1, max=2)])
	techbirth_year = TextField('&nbsp;', [validators.Length(min=4, max=4)])
	techbio = TextAreaField('Personal Description', [validators.Length(min=1, max=2000)], widget=TextArea())
	# password = PasswordField('Password', [validators.Required(), validators.EqualTo('techconfirm', message ="Passwords must match.")])

@app.route('/techaccount/', methods=['GET','POST'])
def techaccount():
	error = ''
	# Using this global variable is tough because each time I redirect, even to the same page, it forgets the value. Make it a session varaible maybe?
	try:
		# Declare form early on, so the form is referenced before assignment
		form = TechEditAccountForm(request.form)
		if session['logged_in'] == 'tech':
			#grab all the clients info
			c, conn = connection()
			techemail = session['techemail']
			c.execute("SELECT tid FROM technicians WHERE email = (%s)", (techemail,))
			techtid = c.fetchone()[0]
			c.execute("SELECT phone FROM technicians WHERE email = (%s)", (techemail,))
			techphone = c.fetchone()[0]
			c.execute("SELECT rating FROM technicians WHERE email = (%s)", (techemail,))
			techrating = c.fetchone()[0]
			c.execute("SELECT first_name FROM tpersonals WHERE tid = (%s)", (techtid,))
			techfirst_name = c.fetchone()[0]
			c.execute("SELECT last_name FROM tpersonals WHERE tid = (%s)", (techtid,))
			techlast_name = c.fetchone()[0]
			c.execute("SELECT address FROM tpersonals WHERE tid = (%s)", (techtid,))
			techaddress = c.fetchone()[0]
			c.execute("SELECT city FROM tpersonals WHERE tid = (%s)", (techtid,))
			techcity = c.fetchone()[0]
			c.execute("SELECT state FROM tpersonals WHERE tid = (%s)", (techtid,))
			techstate = c.fetchone()[0]
			c.execute("SELECT zip FROM tpersonals WHERE tid = (%s)", (techtid,))
			techzip = c.fetchone()[0]
			c.execute("SELECT birth_month FROM tpersonals WHERE tid = (%s)", (techtid,))
			techbirth_month = c.fetchone()[0]
			c.execute("SELECT birth_day FROM tpersonals WHERE tid = (%s)", (techtid,))
			techbirth_day = c.fetchone()[0]
			c.execute("SELECT birth_year FROM tpersonals WHERE tid = (%s)", (techtid,))
			techbirth_year = c.fetchone()[0]
			c.execute("SELECT bio FROM tpersonals WHERE tid = (%s)", (techtid,))
			techbio = c.fetchone()[0]
			c.execute("SELECT reg_date FROM tpersonals WHERE tid = (%s)", (techtid,))
			techreg_date = c.fetchone()[0]
			# For now, just putting the prof_pic url into the BLOB
			c.execute("SELECT prof_pic FROM tpersonals WHERE tid = (%s)", (techtid,))
			techprof_pic = c.fetchone()[0]
			conn.commit()
			c.close()
			conn.close()
			session['techtid'] = techtid
			session['techphone'] = techphone
			session['techrating'] = techrating
			session['techfirst_name'] = techfirst_name
			session['techlast_name'] = techlast_name
			session['techaddress'] = techaddress
			session['techcity'] = techcity
			session['techstate'] = techstate
			session['techzip'] = techzip
			session['techbirth_month'] = techbirth_month
			session['techbirth_day'] = techbirth_day
			session['techbirth_year'] = techbirth_year
			session['techbio'] = techbio
			session['techreg_date'] = techreg_date
			session['techprof_pic'] = techprof_pic
			#//END grab all the clients info
			c, conn = connection()
			
			#Get value before placing into textarea-box... 
			#had to do this method because value=session.bio wasnt working in jinja
			form.techbio.data = session['techbio']
			if request.method == 'POST' and form.validate():
				techfirst_name = form.techfirst_name.data
				techlast_name = form.techlast_name.data
				techemail = form.techemail.data
				techphone = form.techphone.data
				techaddress = form.techaddress.data
				techcity = form.techcity.data
				techstate = form.techstate.data
				techzip = form.techzip.data
				techbirth_month = form.techbirth_month.data
				techbirth_day = form.techbirth_day.data
				techbirth_year = form.techbirth_year.data
				techbio = request.form['techbio']
				techtid = session['techtid']

				# email_check = session['techemail']
				# #check if email already exists
				# x = c.execute("SELECT * FROM technicians WHERE email = (%s) EXCEPT (%s)", (thwart(techemail), email_check))
				# if int(x) > 0:
				# 	#redirect them if they need to recover an old email from and old account
				# 	flash("That email already has an account, please try a a different email.")
				# 	return render_template('techaccount.html', form=form)

				c.execute("UPDATE technicians SET email = %s, phone = %s WHERE tid = (%s)", (techemail, techphone, techtid))
				c.execute("UPDATE tpersonals SET first_name = %s, last_name = %s, address = %s, city = %s, state = %s, zip = %s, birth_month = %s, birth_day = %s, birth_year = %s, bio = %s WHERE tid = (%s)", (thwart(techfirst_name), thwart(techlast_name), thwart(techaddress), thwart(techcity), thwart(techstate), thwart(techzip), techbirth_month, techbirth_day, techbirth_year, techbio, techtid))
				conn.commit()
				c.close()
				conn.close()
				session['techfirst_name'] = techfirst_name
				session['techlast_name'] = techlast_name
				session['techemail'] = techemail
				session['techphone'] = techphone
				session['techaddress'] = techaddress
				session['techcity'] = techcity
				session['techstate'] = techstate
				session['techzip'] = techzip
				session['techbirth_month'] = techbirth_month
				session['techbirth_day'] = techbirth_day
				session['techbirth_year'] = techbirth_year
				session['techbio'] = techbio
				flash("Your account is successfully updated.")
				return redirect(url_for('techaccount'))

		else:
			flash("Try logging out and back in again!")
			return redirect(url_for('homepage'))

		return render_template("techaccount.html", form=form, error = error)

	except Exception as e:
		return render_template("500.html", error = e)

@app.route('/tech_duties/', methods=['GET','POST'])
def tech_duties():
	return render_template("tech_duties.html")
	
#CLIENT REGISTER
class TechSignatureForm(Form):
    signature = TextField('Signature (Please enter your full name)', [validators.Length(min=2, max=100)])

@app.route('/tech_signature/', methods=['GET','POST'])
def tech_signature():
	form = TechSignatureForm(request.form)
	if request.method == "POST" and form.validate():
		signature = form.signature.data
		techtid = session['techtid']
		c, conn = connection()
		c.execute("UPDATE tpersonals SET signature = %s WHERE tid = (%s)", (thwart(signature), techtid))
		conn.commit()
		c.close()
		conn.close()
		flash("Submission successful. We will contact you soon.")
		return redirect(url_for('techaccount'))

	else:
		error = "Please enter your name!"
		return render_template("tech_signature.html", form=form)

# #### PROFILE PIC UPLOAD ####
# # Based after https://gist.github.com/greyli/81d7e5ae6c9baf7f6cdfbf64e8a7c037
# # For uploading files
# TECH_PROF_PIC_UPLOAD_FOLDER = 'static/tech_user_info/prof_pic'
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# app.config['TECH_UPLOADED_PHOTOS_DEST'] = os.getcwd()
# photos = UploadSet('photos', IMAGES)
# configure_uploads(app, photos)
# patch_request_class(app)  # set maximum file size, default is 16MB

# class TechProfilePictureForm(FlaskForm):
# 	techprof_pic = FileField(validators=[FileAllowed(photos, u'Image only!')])

# @app.route('/tech_profile_picture_upload/', methods=['GET','POST'])
# def tech_profile_picture_upload():
# 	form = TechProfilePictureForm()
# 	techtid = str(session['techtid'])
# 	techfirst_name = session['techfirst_name']
# 	default_prof_pic = url_for('static', filename='user_info/prof_pic/default.jpg')
# 	user_prof_pic = techtid+'_'+techfirst_name+'_'+'.png'
# 	if form.validate_on_submit():
# 		filename = photos.save(form.techprof_pic.data, folder=TECH_PROF_PIC_UPLOAD_FOLDER,name=techtid+'_'+techfirst_name+'_'+'.png')
# 		file_url = photos.url(filename)
# 		# Checks if the prof_pic is set yet. if set, then dont need to delete the old picture on the server
# 		# if session['techprof_pic'] != 'http://138.68.238.112/var/www/FlaskApp/FlaskApp/_uploads/photos/static/tech_user_info/prof_pic/default.jpg':
# 		# 	#need to delete or move the old prof_pic if it was set! Prevents users from adding too many pictures
# 		# 	flash("You already have a file on the server!")
# 		#If the user_prof_pic is there, then  
# 		session['techprof_pic'] = file_url
# 		c, conn = connection()
# 		c.execute("UPDATE tpersonals SET prof_pic = %s WHERE tid = (%s)", (file_url, techtid))
# 		conn.commit()
# 		c.close()
# 		conn.close()
# 	else:
# 		file_url = None

# 	return render_template('tech_profile_picture_upload.html', form=form, file_url=file_url)

def login_required(f):
    #not 100% how this works
    # techlogged_in doesnt look like its user anywhere, be sure of these and delete if not anywhere else
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' or 'techlogged_in') in session:
            #arguments and key word arguments
            return f(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for('login_page'))
    return wrap

@app.route('/logout/', methods=['GET','POST'])
@login_required
def logout():
	session.clear()
	flash("You have been logged out!")
	return redirect(url_for('homepage'))

    
#CLIENT LOGIN
@app.route('/login/', methods=['GET','POST'])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":
            c.execute("SELECT * FROM clients WHERE email = (%s)", (thwart(request.form['email']),))
            pdata = c.fetchone()[3]
                
            if sha256_crypt.verify(request.form['password'], pdata):
                email = request.form['email']
                #putting these close and commit 
                #functions outside the 'if' will break code
                conn.commit()
                c.close()
                conn.close()
                session['logged_in'] = 'client'
                session['email'] = thwart(email)
                flash("You are now logged in.")
                return redirect(url_for("account"))
            
            else:
                error = "Invalid credentials, try again."

        return render_template("login.html", error = error)
        
    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)

#PASSWORD CONFIRM
@app.route('/password_confirm/', methods=['GET','POST'])
def password_confirm():
    error = ''
    global password_confirm
    try:
        c, conn = connection()
        if request.method == "POST":
            c.execute("SELECT * FROM clients WHERE email = (%s)", (thwart(request.form['email']),))
            pdata = c.fetchone()[3]
                
            if sha256_crypt.verify(request.form['password'], pdata):
                #putting these close and commit 
                #functions outside the 'if' will break code
                conn.commit()
                c.close()
                conn.close()
                password_confirm = 1
                flash("Successfully authorized.")
                return redirect(url_for("password_reset"))
            
            else:
                error = "Invalid credentials, try again."

        return render_template("password_confirm.html", error = error)
        
    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("password_confirm.html", error = error)

#CLIENT REGISTER
class PasswordResetForm(Form):
    password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm', message ="Passwords must match.")])
    confirm = PasswordField('Repeat Password')

# PASSWORD RESET
@app.route('/password_reset/', methods=['GET','POST'])
def password_reset():
	error = ''
	global password_confirm
	try:
		if password_confirm == 1:
			form = PasswordResetForm(request.form)
			if request.method == "POST" and form.validate():
				cid = session['clientcid']
				password = sha256_crypt.encrypt((str(form.password.data)))
				c, conn = connection()
				c.execute("UPDATE clients SET password = %s WHERE cid = (%s)", (thwart(password), cid))
				conn.commit()
				flash("Password successfully changed!")
				c.close()
				conn.close()
				#so they cant get back in!
				password_confirm = 0
				return redirect(url_for('account'))

			return render_template("password_reset.html", form=form)
		else:
			flash("Not permitted.")
			return redirect(url_for('homepage'))

	except Exception as e:
		return(str(e))


#TECH LOGIN
@app.route('/techlogin/', methods=['GET','POST'])
def tech_login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":
            c.execute("SELECT * FROM technicians WHERE email = (%s)", (thwart(request.form['techemail']),))
            tpdata = c.fetchone()[3]
                
            if sha256_crypt.verify(request.form['techpassword'], tpdata):
                techemail = request.form['techemail']
                #putting these close and commit 
                #functions outside the 'if' will break code
                conn.commit()
                c.close()
                conn.close()
                session['logged_in'] = 'tech'
                session['techemail'] = thwart(techemail)
                flash("You are now logged in.")
                return redirect(url_for("techaccount"))
            
            else:
                error = "Invalid credentials, try again."

        return render_template("techlogin.html", error = error)
        
    except Exception as e:
        #flash(e)
        error = e
        return render_template("techlogin.html", error = error)

#PASSWORD CONFIRM
@app.route('/tech_password_confirm/', methods=['GET','POST'])
def tech_password_confirm():
    error = ''
    global tech_password_confirm
    try:
        c, conn = connection()
        if request.method == "POST":
            c.execute("SELECT * FROM technicians WHERE email = (%s)", (thwart(request.form['techemail']),))
            tpdata = c.fetchone()[3]
                
            if sha256_crypt.verify(request.form['techpassword'], tpdata):
                #putting these close and commit 
                #functions outside the 'if' will break code
                conn.commit()
                c.close()
                conn.close()
                tech_password_confirm = 1
                flash("Successfully authorized.")
                return redirect(url_for("tech_password_reset"))
            
            else:
                error = "Invalid credentials, try again."

        return render_template("tech_password_confirm.html", error = error)
        
    except Exception as e:
        #flash(e)
        error = e
        return render_template("tech_password_confirm.html", error = error)

#CLIENT REGISTER
class TechPasswordResetForm(Form):
    techpassword = PasswordField('Password', [validators.Required(), validators.EqualTo('techconfirm', message ="Passwords must match.")])
    techconfirm = PasswordField('Repeat Password')

# PASSWORD RESET
@app.route('/tech_password_reset/', methods=['GET','POST'])
def tech_password_reset():
	error = ''
	global tech_password_confirm
	try:
		if tech_password_confirm == 1:
			form = TechPasswordResetForm(request.form)
			if request.method == "POST" and form.validate():
				tid = session['techtid']
				techpassword = sha256_crypt.encrypt((str(form.techpassword.data)))
				c, conn = connection()
				c.execute("UPDATE technicians SET password = %s WHERE tid = (%s)", (thwart(techpassword), tid))
				conn.commit()
				flash("Password successfully changed!")
				c.close()
				conn.close()
				#so they cant get back in!
				tech_password_confirm = 0
				return redirect(url_for('techaccount'))

			return render_template("tech_password_reset.html", form=form)
		else:
			flash(tech_password_confirm)
			return redirect(url_for('homepage'))

	except Exception as e:
		return(str(e))
    
#CLIENT REGISTER
class RegistrationForm(Form):
    first_name = TextField('First Name', [validators.Length(min=1, max=50)])
    last_name = TextField('Last Name', [validators.Length(min=1, max=50)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    phone = TextField('Phone Number', [validators.Length(min=10, max=20)])
    czip = TextField('ZIP', [validators.Length(min=2, max=16)])
    password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm', message ="Passwords must match.")])
    confirm = PasswordField('Repeat Password')

@app.route('/register/', methods=['GET','POST'])
def register_page():
	error = ''
	try:
		form = RegistrationForm(request.form)
		if request.method == "POST" and form.validate():
			first_name = form.first_name.data
			last_name = form.last_name.data
			email = form.email.data
			phone = form.phone.data
			address = "Not provided"
			city = "Not provided"
			state = "NA"
			czip = form.czip.data
			bio = "Not provided"
			password = sha256_crypt.encrypt((str(form.password.data)))
			c, conn = connection()

			#check if already exists
			x = c.execute("SELECT * FROM clients WHERE email = (%s)", (thwart(email),))

			if int(x) > 0:
				flash("That email already has an account, please try a new email or sign in.")
				return render_template('register.html', form=form)
			else:
				#make sure this default pic is in the correct folder!!
				default_prof_pic = url_for('static', filename='user_info/prof_pic/default.jpg')
				c.execute("INSERT INTO clients (email, phone, password) VALUES (%s, %s, %s)", (thwart(email), thwart(phone), thwart(password)))
				c.execute("INSERT INTO cpersonals (first_name, last_name, address, city, state, zip, bio, prof_pic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (thwart(first_name), thwart(last_name), address, city, state, thwart(czip), bio, default_prof_pic))
				conn.commit()
				flash("Thanks for registering!")
				c.close()
				conn.close()

				session['logged_in'] = 'client'
				#we get the client ID on the first page after it is generated, dont worry
				session['clientcid'] = 0
				session['email'] = email
				session['phone'] = phone
				session['rating'] = 500
				session['first_name'] = first_name
				session['last_name'] = last_name
				session['address'] = address
				session['city'] = city
				session['state'] = state
				session['czip'] = czip
				session['reg_date'] = 0
				session['bio'] = bio
				#change this when the server goes live to the proper folder
				session['prof_pic'] = default_prof_pic
				return redirect(url_for('account'))

		return render_template("register.html", form=form)


	except Exception as e:
		return(str(e))

#TECH REGISTER
class TechRegistrationForm(Form):
    techfirst_name = TextField('First Name', [validators.Length(min=1, max=50)])
    techlast_name = TextField('Last Name', [validators.Length(min=1, max=50)])
    techemail = TextField('Email Address', [validators.Length(min=6, max=50)])
    techphone = TextField('Phone Number', [validators.Length(min=10, max=20)])
    techaddress = TextField('Street Address', [validators.Length(min=6, max=100)])
    techcity = TextField('City', [validators.Length(min=2, max=50)])
    #('what we see','what they see')
    techstate = TextField('State', [validators.Length(min=2, max=2)])
    techzip = TextField('ZIP', [validators.Length(min=2, max=16)])
    techpassword = PasswordField('Password', [validators.Required(), validators.EqualTo('techconfirm', message ="Passwords must match.")])
    techconfirm = PasswordField('Repeat Password')
    
@app.route('/techregister/', methods=['GET','POST'])
def tech_register_page():
	error = ''
	try:
		form = TechRegistrationForm(request.form)
		if request.method == "POST" and form.validate():
			techfirst_name = form.techfirst_name.data
			techlast_name = form.techlast_name.data
			techemail = form.techemail.data
			techphone = form.techphone.data
			techaddress = form.techaddress.data
			techcity = form.techcity.data
			techstate = form.techstate.data
			techzip = form.techzip.data
			techbio = "Not provided"
			techpassword = sha256_crypt.encrypt((str(form.techpassword.data)))
			c, conn = connection()

			#check if already exists
			x = c.execute("SELECT * FROM technicians WHERE email = (%s)", (thwart(techemail),))

			if int(x) > 0:
				flash("That email already has an account, please try a new email or sign in.")
				return render_template('techregister.html', form=form)
			else:
				default_prof_pic = url_for('static', filename='tech_user_info/prof_pic/default.jpg')
				c.execute("INSERT INTO technicians (email, phone, password) VALUES (%s, %s, %s)", (thwart(techemail), thwart(techphone), thwart(techpassword)))
				c.execute("INSERT INTO tpersonals (first_name, last_name, address, city, state, zip, bio, prof_pic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (thwart(techfirst_name), thwart(techlast_name), thwart(techaddress), thwart(techcity), techstate, thwart(techzip), techbio, default_prof_pic))
				conn.commit()
				flash("Thanks for registering!")
				c.close()
				conn.close()

				session['logged_in'] = 'tech'
				#tid will be inputted once generated
				session['techtid'] = 0
				session['techemail'] = techemail
				session['techphone'] = techphone
				session['techrating'] = 500
				session['techfirst_name'] = techfirst_name
				session['techlast_name'] = techlast_name
				session['techaddress'] = techaddress
				session['techcity'] = techcity
				session['techstate'] = techstate
				session['techzip'] = techzip
				session['techreg_date'] = 0
				session['techbio'] = techbio
				#change this when the server goes live to the proper folder
				session['techprof_pic'] = default_prof_pic
				return redirect(url_for('techaccount'))

		return render_template("techregister.html", form=form)


	except Exception as e:
		return(str(e))


## Sending Files ##

@app.route('/MinutetechLLC_tos/')
def return_file():
	#changing the directory does not effect the remote environement, the command doesnt even seem to go through
	#so I have this here so that when on a local environment, it changes to the proper place so it can pull this file
	#perhaps try and replace with this (https://stackoverflow.com/questions/17681762/unable-to-retrieve-files-from-send-from-directory-in-flask)
	os.chdir('C:\Users\Dougroot\Python27\Projects\minutetech-flask\static\legal\\')
	#return send_file('static\legal\MinutetechLLC_tos.pdf', attachment_filename='MinutetechLLC_tos.pdf')
	return send_file('MinutetechLLC_tos.pdf', attachment_filename='MinutetechLLC_tos.pdf')

    
############################################ END ACCOUNT SYSTEM #########################################################

if __name__ == "__main__":
    app.run(debug=True)