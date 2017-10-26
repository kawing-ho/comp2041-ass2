#!/usr/bin/python3

# written by z5087077@cse.unsw.edu.au October 2017
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/
# UNSWtalk social media website

#Private information such e-mail, password, lat, long and courses should not be displayed.
#The student's posts should be displayed in reverse chronological order. 

import os, re
from flask import Flask, render_template, session, url_for, redirect, request

students_dir = "static/dataset-medium"
all_possible_details = ["home_longitude", "friends", "email",
                        "home_suburb", "birthday", "full_name", 
                        "home_latitude", "program", "courses"]

app = Flask(__name__)

#parse birthday into a more human friendly format
def parseBirthday(bday):
	if(bday == "-"): return bday
	
	(year, month, day) = bday.split("-")
	month = month.lstrip("0")
	month = {"1":"January","2":"February","3":"March","4":"April","5":"May","6":"June","7":"July",
	         "8":"August","9":"September","10":"October","11":"November","12":"December"}.get(month,"NEIN")
	
	return (day + " " + month + " " + year)
	

#feeds are specific to each user logged in ! 
@app.route('/feed', methods=['GET','POST'])
def feed():
	currentUser = whoAmI()
	return render_template('feed.html')

#function which logs out the user
@app.route('/logout',methods=['POST'])
def logout():
	#clear out the session
	session.clear()
	
	#return them to the login page (via profile page)
	return redirect(url_for('profile'))
	

#function for login post request
@app.route('/login', methods=['POST'])
def login():
	#if session is active then redirect 
	if 'zid' in session:
		return redirect(url_for('profile'))
	
	#--- AUTO-LOGIN for easy debugging ---#
	session['zid'] = "z5196487"
	return redirect(url_for('profile'))
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
	

#Show unformatted details for student "n".
# Increment  n and store it in the session cookie
@app.route('/', methods=['GET','POST'])
@app.route('/user/<zid>')
def profile(zid=None):
	
	#if session is not found redirect to login 
	if 'zid' not in session: return render_template('login.html')
	if zid is None: zid = whoAmI()
	details = {}
	details_filename = os.path.join(students_dir, zid, "student.txt")
	 
	#Get text details from file
	with open(details_filename) as f:
	
	    for line in f:
	 	    match = re.search("([^\:]+): (.*)",line)
	 	    key = match.group(1)
	 	    value = match.group(2)
	 	    details[key] = value
	 		
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
	image_filename = os.path.join(students_dir, zid, "img.jpg")
	if(os.path.exists(image_filename) is False): #use default avatar if none found
		image_filename = "static/avatar.jpg"
		
	return render_template('start.html', student_details=details,
                           image=image_filename,)

@app.context_processor
def my_utility_processor():
	
	#returns dictionary of info for friends list / posts / comments / replies
	def getInfo(zid):
	
		details_filename = os.path.join(students_dir, zid, "student.txt")
		details = {}
		#Get text details from file
		with open(details_filename) as f:
	
			for line in f:
				match = re.search("([^\:]+): (.*)",line)
				key = match.group(1)
				value = match.group(2)
				details[key] = value
				
		#set default values
		for field in all_possible_details:
			if field not in details.keys():
				details[field] = "-"
	 	    	
	 	#get image as well
		image = os.path.join(students_dir, zid, "img.jpg")
		if(os.path.exists(image) is False): #use default avatar if none found
			image = "static/avatar.jpg"
			
		details["image"] = image
		return details
	#-------------------------------------------------
	
	def whoAmI():
		return session["zid"]
	
	
	return dict(getInfo=getInfo,whoAmI=whoAmI)
	


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=7331)
