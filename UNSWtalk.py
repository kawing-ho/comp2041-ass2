#!/usr/bin/python3

# written by z5087077@cse.unsw.edu.au October 2017
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/
# UNSWtalk social media website

#Private information such e-mail, password, lat, long and courses should not be displayed.
#The student's posts should be displayed in reverse chronological order. 

import os, re
from flask import Flask, render_template, session, url_for, redirect, request

students_dir = "static/dataset-medium"
static_dir = students_dir.replace("static/",'')
all_possible_details = ["home_longitude", "friends", "email",
                        "home_suburb", "birthday", "full_name", 
                        "home_latitude", "program", "courses"]

app = Flask(__name__)

#if session is not found redirect to login 
def checkLogin():
	if 'zid' not in session: return render_template('login.html')

#get the zid of the logged in user
def whoAmI():
	return session["zid"]

#parse birthday into a more human friendly format
def parseBirthday(bday):
	if(bday == "-"): return bday
	
	(year, month, day) = bday.split("-")
	month = month.lstrip("0")
	month = {"1":"January","2":"February","3":"March","4":"April","5":"May","6":"June","7":"July",
	         "8":"August","9":"September","10":"October","11":"November","12":"December"}.get(month,"NEIN")
	
	return (day + " " + month + " " + year)
	
@app.route('/results', methods=['POST'])
def results():
	checkLogin()
	return render_template('results.html', me=whoAmI())

@app.route('/settings', methods=['GET'])
def settings():
	checkLogin()
	return render_template('settings.html', me=whoAmI())

#feeds are specific to each user logged in ! 
@app.route('/feed', methods=['GET','POST'])
def feed():
	
	checkLogin()
	return render_template('feed.html', me=whoAmI())

#function which logs out the user
@app.route('/logout',methods=['GET','POST'])
def logout():
	#clear out the session
	session.clear()
	
	#return them to the login page
	return render_template('login.html', success="You have logged out")
	

#function for login post request
@app.route('/login', methods=['POST'])
def login():
	#if session is active then redirect 
	if 'zid' in session:
		print("REDIRECTING")
		return redirect(url_for('profile'), zid= whoAmI())
	
	#--- AUTO-LOGIN for easy debugging ---#
	session['zid'] = "z5196487"
	#return redirect(url_for('profile', zid=whoAmI()))
	return redirect(url_for('feed'))
	#-------------------------------------#
	
	#sanitize input
	zid = request.form.get('zid', '')
	attempt = request.form.get('password', '')
	zid = re.sub(r'\W', '', zid)
	
	#check if login doesn't match then return to page
	
	# - non existant id
	if zid not in os.listdir(students_dir):
		return render_template('login.html', error="Incorrect username or password")
	
	# - wrong password
	students_file = os.path.join(students_dir, zid, "student.txt")
	with open(students_file) as f:
		password = re.search("password\s*:\s*(.*)",f.read()).group(1)
	
	if password != attempt:
		return render_template('login.html', error="Incorrect username or password")
	
	#if login matches
	# - set session
	session['zid'] = zid
	
	# - redirect to home page / profile page
	return redirect(url_for('feed'))
	
#future functionality for registering
#runs when the user fills out details and clicks on "Register"
@app.route('/login', methods=['POST'])
def register():
	return render_template('login.html')


#Displays the profile of a specified user
#@app.route('/', methods=['GET','POST'])
@app.route('/', methods=['GET'])
@app.route('/user/<zid>', methods=['GET'])
def profile(zid=None):
	
	#if session is not found redirect to login 
	if 'zid' not in session: return render_template('login.html')
	
	if zid is None: zid = whoAmI()
	details = {}
	print("From Profile: getting info of " + zid)
	details_filename = os.path.join(students_dir, zid, "student.txt")
	 
	#Get text details from file
	try:
		with open(details_filename) as f:
	
			for line in f:
		 	    match = re.search("([^\:]+): (.*)",line)
		 	    key = match.group(1)
		 	    value = match.group(2)
		 	    details[key] = value
	except Exception as e:
		print("In Profile "+e)
	 		
    #if details not found then put default string
	#"The user has chosen not so supply data for this field"
	for field in all_possible_details:
		if field not in details.keys():
			details[field] = "-"
			
	#parse birthday
	details["birthday"] = parseBirthday(details["birthday"])
	
	#convert friends string into a proper list
	friendStr = details["friends"].replace("(",'').replace(")",'').replace(",",'')
	friends = friendStr.split(" ")
	details["friends"] = friends
       		
	#Get image file
	image = os.path.join(static_dir, zid, "img.jpg")
	checkImage = os.path.join(students_dir, zid, "img.jpg")
	if(os.path.exists(checkImage) is False): #use default avatar if none found
		image = "avatar.jpg"
		
	return render_template('profile.html', zid=zid, student_details=details, image=image)

@app.context_processor
def my_utility_processor():
	
	#returns dictionary of info for friends list / posts / comments / replies
	def getInfo(zid):
		print("From JINJA: getting info of " + zid)
		details_filename = os.path.join(students_dir, zid, "student.txt")
		details = {}
		#Get text details from file
		try:
			with open(details_filename) as f:
	
				for line in f:
					match = re.search("([^\:]+): (.*)",line)
					key = match.group(1)
					value = match.group(2)
					details[key] = value
		except Exception as e:
			print("In JINJA: "+e)
				
		#set default values
		for field in all_possible_details:
			if field not in details.keys():
				details[field] = "-"
	 	    	
	 	#get image as well
		image = os.path.join(static_dir, zid, "img.jpg")
		checkImage = os.path.join(students_dir, zid, "img.jpg")
		if(os.path.exists(checkImage) is False): #use default avatar if none found
			image = "avatar.jpg"
			
		details["image"] = image
		return details
	#-------------------------------------------------
	
	def whoAmI():
		return session["zid"]
	
	
	return dict(getInfo=getInfo,whoAmI=whoAmI)
	


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=7331)
