#!/usr/bin/python3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os, re
from flask import Flask, render_template, session

students_dir = "dataset-medium";

app = Flask(__name__)

#Implement a login page later
#if session not detected then redirect to login page



#Show unformatted details for student "n".
# Increment  n and store it in the session cookie
@app.route('/', methods=['GET','POST'])
@app.route('/start', methods=['GET','POST'])
def start():
    details = {}
    n = session.get('n', 0)
    students = sorted(os.listdir(students_dir))
    student_to_show = students[n % len(students)]
    details_filename = os.path.join(students_dir, student_to_show, "student.txt")
    session['n'] = n + 1
    with open(details_filename) as f:
        #[details.append(line) for line in f]
    #return render_template('start.html', student_details=details)
        for line in f:
        		match = re.search("([^\:]+):(.*)",line)
        		key = match.group(1)
        		value = match.group(2)
        		details[key] = value		
    return render_template('start.html', student_details=details)

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=1337)
