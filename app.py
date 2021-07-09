'''

author - Hari Prasad

sources - 

https://stackoverflow.com/questions/13772884/css-problems-with-flask-web-app

'''

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_session import Session
from flask_pymongo import PyMongo
from decouple import config

import business

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

app.config["MONGO_URI" ] = config("MONGO_URI")

Session(app)

socketio = SocketIO(app, manage_session=False)

mongo  = PyMongo(app)
users  = mongo.db.cio_users

participants=[]

'''
http://127.0.0.1:5000/
'''

@app.route("/", methods = ['GET', 'POST'])
def home():

    if(request.method=='POST'):

        room_pin = request.form['room_pin']

        # print(room_pin)

    return render_template("home.html")

'''
http://127.0.0.1:5000/login
'''

@app.route("/login", methods = ['GET'])
def login_get():
    return render_template("login.html")

@app.route("/login", methods = ['POST'])
def login_post():

    if(request.method=='POST'):

        email    = request.form['email']
        password = request.form['password']

        result, error_message = business.login(email, password)

        if(result == True):
            
            return render_template("home.html")

        return render_template("login.html", error_message = error_message)

'''
http://127.0.0.1:5000/signup
'''

@app.route("/signup", methods = ['GET'])
def signup_get():
    return render_template("signup.html")

@app.route("/signup", methods = ['POST'])
def signup_post():

    if(request.method=='POST'):

        email    = request.form['email']
        username = request.form['username']
        password = request.form['password']

        business.signup(email, username, password)

    return render_template("home.html")

'''
http://127.0.0.1:5000/create/room
'''

@app.route("/create/room", methods = ['GET'])
def get_create_room():
    return render_template("create_room.html")

@app.route("/create/room", methods = ['POST'])
def post_create_room():

    if(request.method=='POST'):

        room_name = request.form['room_name']

        # print(room_name)

    return render_template("create_room.html")

'''
http://127.0.0.1:5000/room
'''

@app.route("/room", methods = ['GET', 'POST'])
def room():
    
    if(request.method=='POST'):

        username = request.form['username']
        room = request.form['room']
        
        session['username'] = username
        session['room'] = room

        participants.append(session)
        
        return render_template('room.html', session = session)
    
    else:
        
        if(session.get('username') is not None):
        
            return render_template('room.html', session = session)
        
        else:
        
            return redirect(url_for('index'))


@app.route("/get/participants", methods = ['GET'])
def get_participantss():
    print(participants)

# @app.route("/room/<room>", methods = ['GET', 'POST'])
# def room(room):
#     print(room)
#     return render_template("room.html")

@socketio.on('connect')
def connected():
    print('connect')

@socketio.on('join', namespace='/room')
def join(data):

    # print('join')

    room = session.get('room')

    join_room(room)

    emit('status', { 'message':  session.get('username') + ' has entered the room.' }, room=room )

@socketio.on('message', namespace='/room')
def message(data):

    # print(data)

    room = session.get('room')

    emit('message_response', { 'message': session.get('username') + ' : ' + data['message']}, room=room)

@socketio.on('leave', namespace='/room')
def leave(data):

    # print('leave')

    room = session.get('room')
    
    leave_room(room)

    session.clear()

    emit('status', { 'message':  session.get('username') + ' has left the room.' }, room=room )

if __name__ == '__main__':
    socketio.run(app, debug=True)
