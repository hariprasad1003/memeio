'''

author - Hari Prasad

sources - 

https://stackoverflow.com/questions/13772884/css-problems-with-flask-web-app
https://www.javatpoint.com/flask-session
https://stackoverflow.com/questions/26954122/how-can-i-pass-arguments-into-redirecturl-for-of-flask
https://stackoverflow.com/questions/19614027/jinja2-template-variable-if-none-object-set-a-default-value
https://stackoverflow.com/questions/63043491/convert-utc-timezone-to-ist-python

'''

from types import resolve_bases
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import html
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_session import Session
from flask_pymongo import PyMongo
from decouple import config
from datetime import datetime
import pytz
import business

app = Flask(__name__)

app.static_folder = 'static'

app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["MONGO_URI" ] = config("MONGO_URI")

Session(app)

socketio = SocketIO(app, manage_session=False)

mongo  = PyMongo(app)
users  = mongo.db.cio_users
rooms  = mongo.db.cio_rooms

# participants=[]

def get_time():

    tz = pytz.timezone('Asia/Kolkata')

    datetime_ny = datetime.now(tz)  

    time = datetime_ny.strftime("%H:%M:%S")

    return time

'''
http://127.0.0.1:5000/
'''

@app.route("/", methods = ['GET'])
def get_home():

    return render_template("home.html", error_message = None)

@app.route("/", methods = ['POST'])
def post_home():

    if(request.method=='POST'):

        name = request.form['username']
        room_pin = request.form['room_pin']

        # print(name, room_pin)

        result = business.enter_room(name, room_pin)

        # print(result)

        if(int(result["status_code"]) == 200):

            room_name = result["room_name"]
            acc_type  = result["acc_type"]

            # print(room_name, acc_type)

            session['user_session'] = name
            session['room'] = room_name
            session['acc_type'] = acc_type

            # print(session.get('user_session'), session.get('room'), session.get('acc_type'))

            return redirect(url_for('get_room'))

        return render_template("home.html", error_message = result['message'])


'''
http://127.0.0.1:5000/login
'''

@app.route("/login", methods = ['GET'])
def login_get():
    return render_template("login.html", error_message = None)

@app.route("/login", methods = ['POST'])
def login_post():

    if(request.method=='POST'):

        username    = request.form['username']
        password    = request.form['password']

        # print(username, password)

        result = business.login(username, password)

        # print(result)

        # print(int(result["status_code"]))

        if(int(result["status_code"]) == 200):
            
            session['user_session'] = username

            return redirect(url_for('get_create_room'))

        return render_template("login.html", error_message = result['message'])


'''
http://127.0.0.1:5000/logout
'''

@app.route("/logout")
def logout():

  if 'user_session' in session:  

        session.pop('user_session', None)  

        return redirect(url_for('get_home'));  

'''
http://127.0.0.1:5000/signup
'''

@app.route("/signup", methods = ['GET'])
def signup_get():
    return render_template("signup.html")

@app.route("/signup", methods = ['POST'])
def signup_post():

    if(request.method=='POST'):

        username = request.form['username']
        password = request.form['password']

        session['user_session'] = username

        business.signup(username, password)

    return redirect(url_for('get_create_room'))

'''
http://127.0.0.1:5000/create/room
'''

@app.route("/create/room", methods = ['GET'])
def get_create_room():

    # print("get_create_room")

    if 'user_session' in session:

        return render_template("create_room.html")
     
    else:

        result = {

            "message"     : "Login Required!",
            "status_code" : 401  
        }
        

        # return redirect(url_for('login_get', error_message = result['message'], **request.args))
    
        return render_template("login.html", error_message = result['message'])

@app.route("/create/room", methods = ['POST'])
def post_create_room():

    if(request.method=='POST'):

        room_name = request.form['room_name']

        username  = session['user_session']

        # print(room_name, username)
        
        result = business.create_room(room_name, username)

        # room_type = request.form['room_type']

        # print(room_name, room_type)

        # print(result)

        # print(int(result["status_code"]))

        if(int(result["status_code"]) == 200):

            # room_name = result["room_name"]

            return render_template("pin.html", result = result)

        return render_template("create_room.html", error_message = result['message'])

'''
http://127.0.0.1:5000/room
'''

@app.route("/room", methods = ['GET'])
def get_room():

    if 'room' in session:

        room = session.get('room')

        acc_type = session.get('acc_type')

        # print(room, acc_type)

        if acc_type=="admin":

            return render_template('admin.html')

        else:

            return render_template('user.html')

    else:

        result = {

            "message"     : "It seems like, you don't have access to this room",
            "status_code" : 401

        }

        return render_template("error.html", error_message = result['message'])


@app.route("/get/participants", methods = ['GET'])
def get_participantss():

    # print(participants)

    pass

@socketio.on('connect')
def connected():
    print('connect')

@socketio.on('join')
def join(data):

    # print('join')

    room = session.get('room')

    join_room(room)

    result_dict = {

        "username"  : session.get('user_session'),
        "room"      : room,
        "message"   : "has entered the room"
    
    }

    # print(result_dict)

    socketio.emit('status', result_dict)

@socketio.on('message')
def message(data):

    # print(data)

    room = session.get('room')

    result_dict = {

        "username"  : session.get('user_session'),
        "room"      : room,
        "message"   : data['message'],
        "time"      : get_time()
    
    }
    
    # print(result_dict)
    
    socketio.emit('message_response', result_dict)

@socketio.on('leave')
def leave(data):

    # print('leave')

    # username = session.get('user_session')

    room = session.get('room')
    
    leave_room(room)

    result_dict = {

        "username"  : session.get('user_session'),
        "room"      : room,
        "message"   : "had left the room"
    
    }

    session.clear()

    emit('status', result_dict )

if __name__ == '__main__':
    socketio.run(app, debug=True)
