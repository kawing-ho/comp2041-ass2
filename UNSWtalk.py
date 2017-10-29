#!/usr/bin/python3

# written by z5087077@cse.unsw.edu.au October 2017
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/
# UNSWtalk social media website

#Private information such e-mail, password, lat, long and courses should not be displayed.
#The student's posts should be displayed in reverse chronological order. 

import os, re
from flask import Flask, render_template, session, url_for, redirect, request
from datetime import datetime as dt

students_dir = "static/dataset-medium"
static_dir = students_dir.replace("static/",'')
all_possible_details = ["home_longitude", "friends", "email",
                        "home_suburb", "birthday", "full_name", 
                        "home_latitude", "program", "courses"]

app = Flask(__name__)

#if session is not found redirect to login 
def checkLogin():
	if(len(session) == 0): return redirect(url_for('login'))
	if 'zid' not in session: return redirect(url_for('login'))

#get the zid of the logged in user
def whoAmI():
	checkLogin()
	if 'zid' not in session: return render_template('login.html')
	return session["zid"]

#replace all tags with name and links
def addTags(message):
	if(re.search("z\d+", message)): 
			
		for tagged in re.findall("z\d+", message):
			url = url_for('profile',zid=tagged)
			repl = "<a href=\""+url+"\"><mark>@"+getName(tagged)+"</mark></a>"
			message = message.replace(tagged,repl)
			
	return message

#gets the name of the person by zid
def getName(zid):
	
	filename = os.path.join(students_dir,zid,"student.txt")
	with open(filename) as f:
		n = re.search("name: ([\w\- ]+)", f.read())
	
	if(n is None): name = ""
	else: name = n.group(1)
	
	return name

#parse birthday into a more human friendly format
def parseBirthday(bday):
	if(bday == "-"): return bday
	
	(year, month, day) = bday.split("-")
	month = month.lstrip("0")
	month = {"1":"January","2":"February","3":"March","4":"April","5":"May","6":"June","7":"July",
	         "8":"August","9":"September","10":"October","11":"November","12":"December"}.get(month,"NEIN")
	
	return (day + " " + month + " " + year)
#-------------------------------------------------


@app.route('/#', methods=['POST'])
def post(message=None):
	me = whoAmI()
	
	message = request.form.get('message')
	time = dt.now().strftime("%Y-%m-%dT%H:%M:%S+0000")
	message = message.replace('\r','')
	message = message.replace('\n','\\n')
	
	message = "message: " + message
	sender = "from: " + me
	time = "time: " + time
	if(len(message) > 0):
		path = os.path.join(students_dir,me)
		recent = max([post for post in os.listdir(path) if re.search("^(\d)+.txt$",post)])
		num = int(recent.replace('.txt','')) + 1
		new = str(num)+".txt"
		check = os.path.join(path,new)
		if(os.path.exists(check) is False):
			with open(check,'w+') as f:
				data = message+"\n"+sender+"\n"+time+"\n"
				f.write(data)
		else: print("File already exists !!!!")	
	
	return redirect(url_for('profile',zid=me))

#Function for handling the friend system, refreshes the page after finishing
@app.route('/#', methods=['POST'])
def friend(peer=None):
	me = whoAmI()
	peer = request.form.get('peer')
	
	myFile = os.path.join(students_dir,me,"student.txt")
	try:
			with open(myFile) as f:	myData = f.read()
	except Exception as e: print(e)
	myFriends = re.search("friends: (.*)",myData).group(1)
	
	
	peerFile = os.path.join(students_dir,peer,"student.txt")
	try:
			with open(peerFile) as f:	peerData = f.read()
	except Exception as e: print(e)
	peerFriends = re.search("friends: (.*)",peerData).group(1)
	
	
	if(request.form.get('request') or request.form.get('accept')):
		action="request"
		
		#TODO if(request.form.get('request')): SEND EMAIL TODO
		
		#add them to your friends list 
		#(then they either add you to their list or remove themselves from your list)
		if(peer not in myFriends):
			newFriends = myFriends.replace(')',", "+peer+")")	
			data = myData.replace(myFriends, newFriends)
		
			try:
				with open(myFile,'w') as f:	f.write(data)
			except Exception as e: print(e)
		else: print("They're already in the list !")
		
		
	elif(request.form.get('cancel')):
		action="cancel"
		
		#delete them from your friends list
		#(basically undo the action of sending the request)
		if(peer in myFriends):
			newFriends = myFriends.replace("("+peer+",",'(')
			newFriends = myFriends.replace(", "+peer,'')
			data = myData.replace(myFriends, newFriends)
			print("deleted",peer)
			try:
				with open(myFile,'w') as f: f.write(data)
			except Exception as e: print(e)
		else: print("They're not in the list ?")
		
		#acceptance is handled above as well
		#add them to your friends list 
		#(since they added you to theirs already)
		
	elif(request.form.get('reject')):
		action="reject"
		
		#delete yourself from their friend list
		#(then they will have to add you to the list again as a "request")
		if(me in peerFriends):
			newFriends = peerFriends.replace("("+me+",",'(')
			newFriends = peerFriends.replace(", "+me,'')
			data = peerData.replace(peerFriends, newFriends)
		try:
			with open(peerFile,'w') as f: f.write(data)
		except Exception as e: print(e)
		else: print("I'm not in their friend list ?")
		
	elif(request.form.get('unfriend')):
		action="unfriend"
		
		#delete them from your friends list
		if(peer in myFriends):

			newFriends = myFriends
			if(re.match(", "+peer,myFriends)): 
				print("matched the mid")
				newFriends = myFriends.replace(", "+peer,'')
			else: 
				print("matched the end")
				newFriends = myFriends.replace(peer+", ",'')

			data = myData.replace(myFriends, newFriends)
			print("deleting",peer)
			print(myFriends)
			print(newFriends)

			try:
				with open(myFile,'w') as f: f.write(data)
			except Exception as e: print(e)
		else: print("They're not in the list ?")
		
		#delete yourself from their friends list
		if(me in peerFriends):

			newFriends = peerFriends
			if(re.match(", "+me,peerFriends)): 
				print("matched the mid")
				newFriends = peerFriends.replace(", "+me,'')
			else: 
				print("matched the end")
				newFriends = peerFriends.replace(me+", ",'')

			data = peerData.replace(peerFriends, newFriends)
			print("deleting",me)
			print(peerFriends)
			print(newFriends)

			try:
				with open(peerFile,'w') as f: f.write(data)
			except Exception as e: print(e)
		else: print("I'm not in their friend list ?")
		
	else: action="UNDEFINED"
	
	
	print("Friend button pressed:", peer, action)
	return redirect(url_for('profile',zid=peer))

@app.route('/results', methods=['POST'])
def results():
	checkLogin()
	results = []
	students = {}
	search = request.form.get('search','')
	print("Searched :","\'"+search+"\'")
	search = search.lower()
	
	#get dictionary of all users -- student['name'] = zid
	for user in os.listdir(students_dir):
		students[getName(user).lower()] = user
	
	for key,value in students.items():
		if(re.search(search, key)): results.append(value)
	
	return render_template('results.html', me=whoAmI(), search=search, results=results)

@app.route('/settings', methods=['GET'])
def settings():
	checkLogin()
	return render_template('settings.html', me=whoAmI())

#feeds are specific to each user logged in ! 
@app.route('/feed', methods=['GET','POST'])
def feed():
	
	checkLogin()
	me = whoAmI()
	
	postList = []
	commentList = []
	replyList = []
	
	#Section for recent posts
	recentPostList = []
	recentCommentList = []
	recentReplyList = []
	
	#only grab posts that are recent enough
	content_path = os.path.join(students_dir, me)
	myPosts = [ content for content in os.listdir(content_path) if re.search("^\d+.txt$",content) ]
	
	for post in myPosts:
		filename = os.path.join(content_path, post)
		try:
			with open(filename) as f: data = f.read()
		except Exception as e: print("checking posts file",e)
		
		self = re.sub('\D','',post)
		
		time = re.search("time: (.*)",data).group(1)
		t = dt.strptime(time, "%Y-%m-%dT%H:%M:%S+0000")
		lastMonth = "01/10/2017"
		t2 = dt.strptime(lastMonth, "%d/%m/%Y")
		
		if(t > t2): 
			parent = None
			sender = re.search("from: (.*)",data).group(1)
			m = re.search("message: (.*)",data)
			message = "" if m is None else m.group(1)
			message = message.replace("\\n","<br \>")
			message = addTags(message)
					
			recentPostList.append((time, parent, self, sender, message))
	
	#only grab comments that are from recent posts
	myComments = [ content for content in os.listdir(content_path) if re.search("^\d+-\d+\.txt",content) ]
	parents = [tup[2] for tup in recentPostList]
	
	if(parents):
		for comment in myComments:
			p = re.search('^(\d+)-(\d+)\.txt$',comment)
			parent = p.group(1)
			self = p.group(2)
			if(parent not in parents): continue
			
			filename = os.path.join(content_path, comment)
			try:
				with open(filename) as f: data = f.read()
			except Exception as e: print("checking comments file",e)
			
			sender = re.search("from: (.*)",data).group(1)
			time = re.search("time: (.*)",data).group(1)
			m = re.search("message: (.*)",data)
			message = "" if m is None else m.group(1)
			message = message.replace("\\n","<br \>")
			message = addTags(message)
			
			recentCommentList.append((time, parent,self, sender, message))
	
	#only grab replies that are from comments that are from recent posts
	myReplies = [ content for content in os.listdir(content_path) if re.search("^\d+-\d+-\d+\.txt$", content) ]
	parents = [tup[2] for tup in recentCommentList]
	
	if(parents):
		for reply in myReplies:
			r = re.search('^\d+-(\d+)-(\d+)\.txt$'.reply)
			parent = r.group(1)
			self = r.group(2)
			if(parent not in parents): continue
			
			filename = os.path.join(content_path, reply)
			try:
				with open(filename) as f: data = f.read()
			except Exception as e: print("checking comments file",e)
			
			sender = re.search("from: (.*)",data).group(1)
			time = re.search("time: (.*)",data).group(1)
			m = re.search("message: (.*)",data)
			message = "" if m is None else m.group(1)
			message = message.replace("\\n","<br \>")
			message = addTags(message)
			
			recentReplyList.append((time, parent,self, sender, message))
			
	recentPostList.sort(reverse=True)
	recentCommentList.sort(reverse=True)
	recentReplyList.sort(reverse=True)
	
		
	#Section for friend's posts
	friendsPostList = []
	friendsCommentList = []
	friendsReplyList = []
	
	#get list of friends
	filename = os.path.join(students_dir,me,"student.txt")
	try:
		with open(filename) as f: data = f.read()
	except Exception as e: print("Getting friends list", e)
	friendStr = re.search("friends: (.*)",data).group(1)
	friendStr = friendStr.replace("(",'').replace(")",'').replace(",",'')
	friends = friendStr.split(" ")
	
	#for every single friend 
	for friend in friends:
		content_path = os.path.join(students_dir, friend)
		friendPosts = [ content for content in os.listdir(content_path) if re.search("^\d+.txt$",content) ]
	
		for post in friendPosts:
			filename = os.path.join(content_path, post)
			try:
				with open(filename) as f: data = f.read()
			except Exception as e: print("checking posts file",e)
		
		
			self = re.sub('\D','',post)
			self = self + "//" + friend  #unique identifier for post per friend
			time = re.search("time: (.*)",data).group(1)
			parent = None
			sender = re.search("from: (.*)",data).group(1)
			m = re.search("message: (.*)",data)
			message = "" if m is None else m.group(1)
			message = message.replace("\\n","<br \>")
			message = addTags(message)
			
			friendsPostList.append((time, parent, self, sender, message))
	
		#only grab comments that are from parents
		friendComments = [ content for content in os.listdir(content_path) if re.search("^\d+-\d+\.txt",content) ]
		parents = [tup[2] for tup in friendsPostList]
	
		if(parents):
			for comment in friendComments:
				p = re.search('^(\d+)-(\d+)\.txt$',comment)
				parent = p.group(1) + "//" + friend
				self = p.group(2) + "//" + friend
				if(parent not in parents): continue
			
				filename = os.path.join(content_path, comment)
				try:
					with open(filename) as f: data = f.read()
				except Exception as e: print("checking comments file",e)
			
				sender = re.search("from: (.*)",data).group(1)
				time = re.search("time: (.*)",data).group(1)
				m = re.search("message: (.*)",data)
				message = "" if m is None else m.group(1)
				message = message.replace("\\n","<br \>")
				message = addTags(message)
			
				friendsCommentList.append((time, parent, self, sender, message))
	
		#only grab replies that are from comments that are from friends posts
		friendReplies = [ content for content in os.listdir(content_path) if re.search("^\d+-\d+-\d+\.txt$", content) ]
		parents = [tup[2] for tup in friendsCommentList]
	
		if(parents):
			for reply in friendReplies:
				r = re.search('^(\d)+-(\d+)-(\d+)\.txt$',reply)
				root = r.group(1) + "//" + friend
				parent = r.group(2) + "//" + friend
				self = r.group(3) + "//" + friend
				if(parent not in parents): continue
				
				filename = os.path.join(content_path, reply)
				try:
					with open(filename) as f: data = f.read()
				except Exception as e: print("checking comments file",e)
				
				sender = re.search("from: (.*)",data).group(1)
				time = re.search("time: (.*)",data).group(1)
				m = re.search("message: (.*)",data)
				message = "" if m is None else m.group(1)
				message = message.replace("\\n","<br \>")
				message = addTags(message)
			
				friendsReplyList.append((time, parent, self, sender, message, root))
	#end of friend loop
	
	friendsPostList.sort(reverse=True)
	friendsCommentList.sort(reverse=True)
	friendsReplyList.sort(reverse=True)
	print(friendsReplyList)
	
	
	#Section for mentions
	return render_template('feed.html', 
						   recent=recentPostList, 
                           recentComment=recentCommentList,
                           recentReply=recentReplyList,
                           friends=friendsPostList,
                           friendsComment=friendsCommentList,
                           friendsReply=friendsReplyList,
                           )
	
	'''
	return render_template('feed.html',
                           recent=recentPostList, 
                           recentComment=recentCommentList,
                           recentReply=recentReplyList,
                           
                           friends=friendsPostList,
                           friendsComment=friendsCommentList,
                           friendsReply=friendsReplyList,
                           
                           mention=mentionPostList,
                           mentionComment=mentionCommentList,
                           mentionReply=mentionReplyList
                           )
    '''

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
		
		
	#Retrieve and order the posts 
	# ... need to extend to include comments and replies as well
	
	postList = []
	commentList = []
	replyList = []
	
	content_path = os.path.join(students_dir, zid)
	for content in os.listdir(content_path):
		if(content == "student.txt" or content == "img.jpg"): continue
		filename = os.path.join(content_path, content)
		try:
			with open(filename) as f:
				data = f.read()
		except Exception as e:
			print("Content file",e)
				
		sender = re.search("from: (\w+)",data).group(1)			#get zid
		time = re.search("time: ([\w:\+\-]+)",data).group(1)	#get Date
		m = re.search("message: (.*)",data)
		message = "" if(m is None) else m.group(1)				#get message
		message = message.replace("\\n","<br \>")
		parent = None
		root = None
		self = re.search("-?(\d+)\.txt$",content).group(1)
		type = "post"
		

		if(re.search("z\d+", message)): 
			#print(getName(sender), message)
			for tagged in re.findall("z\d+", message):
				#tagged is still a zid here
				#print(tagged,"-",getName(tagged))
				
				#need to replace tagged with repl
				url = url_for('profile',zid=tagged)
				repl = "<a href=\""+url+"\"><mark>@"+getName(tagged)+"</mark></a>"
				message = message.replace(tagged,repl)
				
			#print("--------")
		
		#if its a comment then the parent number is left of slash
		comment = re.compile('^\d+\-\d+\.txt$')
		if comment.match(content):
			type = "comment"
			parent = re.search("^(\d+)\-\d+\.txt$",content).group(1)
				
		#if its a reply then the parent number is between two slashes
		reply = re.compile('^\d+\-\d+\-\d+.txt$')
		if reply.match(content):
			type = "reply"
			m = re.search("(^\d+)\-(\d+)\-\d+.txt$",content)
			root = m.group(1)
			parent = m.group(2)
				
		element = (time, parent, self, sender, message, root)
				
		if(type == "post"): postList.append(element)
		elif(type == "comment"): commentList.append(element)
		elif(type == "reply"): replyList.append(element)
		else: print("ERROR IN CONTENT")
	
	#sort chronologically means most recent first
	postList.sort(reverse=True)
	commentList.sort(reverse=True)
	replyList.sort(reverse=True)
		
	return render_template('profile.html', zid=zid, student_details=details, image=image,
                                           postList=postList, commentList=commentList,
                                           replyList=replyList)

@app.context_processor
def my_utility_processor():
	
	#returns dictionary of info for friends list / posts / comments / replies
	def getInfo(zid):
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
		checkLogin()
		return session["zid"]

	#returns a more user-friendly version of time string
	#expand this later !    (2016-09-29T11:05:03+0000)
	def fixTime(time):
		
		t = dt.strptime(time, "%Y-%m-%dT%H:%M:%S+0000")
		time = t.strftime('%I:%M %p / %d %b %Y').lstrip('0')
		return time
		
	#check the friendship status of two individuals
	#results:[none, request, requested, friends]
	def checkFriendship(me, peer):
		me_details = getInfo(me)
		peer_details = getInfo(peer)
		
		myFriends = me_details['friends']
		peerFriends = peer_details['friends']
		
		if(peer not in myFriends and me not in peerFriends): result = "none"
		elif(peer not in myFriends and me in peerFriends): result = "requested"
		elif(peer in myFriends and me not in peerFriends): result = "request"
		elif(peer in myFriends and me in peerFriends): result = "friends"
		
		return result
	
	
	return dict(getInfo=getInfo, whoAmI=whoAmI, fixTime=fixTime, friendship=checkFriendship)
	


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=65535)
