#!/usr/bin/python3

# written by z5087077@cse.unsw.edu.au October 2017
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/
# UNSWtalk social media website

import os, re
from flask import Flask, render_template, session, url_for, redirect, request

students_dir = "static/dataset-medium"
all_possible_details = ["home_longitude", "friends", "email",
                        "home_suburb", "birthday", "full_name", 
                        "home_latitude", "program", "courses"]

app = Flask(__name__)

@app.route('/feed', methods=['GET','POST'])
def feed():
    return render_template('base.html')

#function which logs out the user
@app.route('/logout',methods=['POST'])
def logout():
	#clear out the session
	session.clear()
	
	#return them to the login page
	return redirect(url_for('start'))
	

#function for login post request
@app.route('/login', methods=['POST'])
def login():
	#if session is active then redirect 
	if 'zid' in session:
		return redirect(url_for('/start'))
	
	#--- AUTO-LOGIN for easy debugging ---#
	session['zid'] = 1
	return redirect(url_for('start'))
	#-------------------------------------#
	
	#sanitize input
	zid = request.form.get('zid', '')
	attempt = request.form.get('password', '')
	zid = re.sub(r'\W', '', zid)
	
	#check if login doesn't match then return to page
	
	# - not existant id
	#print(zid)
	if zid not in os.listdir(students_dir):
		return render_template('login.html', error="Incorrect username or password")
	
	# - wrong password
	students_file = os.path.join(students_dir, zid, "student.txt")
	with open(students_file) as f:
		password = re.search("password\s*:\s*(.*)",f.read()).group(1)
	
	#print(password)
	if password != attempt:
		return render_template('login.html', error="Incorrect username or password")
	
	#if login matches
	# - set session
	session['zid'] = zid
	
	# - redirect to home page / profile page
	return redirect(url_for('start'))
	

#Show unformatted details for student "n".
# Increment  n and store it in the session cookie
@app.route('/', methods=['GET','POST'])
#@app.route('/start', methods=['GET','POST'])
def start():
	
	#if session is not found redirect to login 
	if 'zid' not in session: return render_template('login.html')
	 
	details = {}
	n = session.get('n', 0)
	students = sorted(os.listdir(students_dir))
	student_to_show = students[n % len(students)]
	details_filename = os.path.join(students_dir, student_to_show, "student.txt")
	session['n'] = n + 1
	 
	#Get text details from file
	with open(details_filename) as f:
	
	    for line in f:
	 	    match = re.search("([^\:]+): (.*)",line)
	 	    key = match.group(1)
	 	    value = match.group(2)
	 	    details[key] = value
	 		
    #if details not found then put default string
	default= "The user has chosen not so supply data for this field"
	for field in all_possible_details:
		if field not in details.keys():
			details[field] = default
        		
	#Get image file
	image_filename = os.path.join(students_dir, student_to_show, "img.jpg")
	if(os.path.exists(image_filename) is False): #use default avatar if none found
		image_filename = "static/avatar.jpg"
		
	return render_template('start.html', student_details=details, image=image_filename)

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=7331)
