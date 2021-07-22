'''

author - Hari Prasad

sources - 

https://stackoverflow.com/questions/13772884/css-problems-with-flask-web-app
https://www.javatpoint.com/flask-session
https://stackoverflow.com/questions/26954122/how-can-i-pass-arguments-into-redirecturl-for-of-flask
https://stackoverflow.com/questions/19614027/jinja2-template-variable-if-none-object-set-a-default-value

'''

from types import resolve_bases
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import html
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
rooms  = mongo.db.cio_rooms

participants=[]

'''
http://127.0.0.1:5000/
'''

@app.route("/", methods = ['GET'])
def get_home():

    return render_template("home.html")

@app.route("/", methods = ['POST'])
def post_home():

    if(request.method=='POST'):

        name = request.form['username']
        room_pin = request.form['room_pin']

        # print(room_pin)

        result = business.enter_room(name, room_pin)

        print(result)

        if(result["status_code"] == 200):

            room_name = result["room_name"]

            session['user_session'] = name
            session['room'] = room_name
            

            return redirect(url_for('get_room'))

        return jsonify(result)


'''
http://127.0.0.1:5000/login
'''

@app.route("/login", methods = ['GET'])
def login_get():
    return render_template("login.html", error_message = request.args.get('error_message'))

@app.route("/login", methods = ['POST'])
def login_post():

    if(request.method=='POST'):

        username    = request.form['username']
        password = request.form['password']

        result = business.login(username, password)

        if(result["status_code"] == 200):
            
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

    if 'user_session' in session:

        return render_template("create_room.html")
     
    else:

        result = {

            "message"     : "Login Required!",
            "status_code" : 401  
        }
        

        return redirect(url_for('login_get', error_message = result['message'], **request.args))
    

@app.route("/create/room", methods = ['POST'])
def post_create_room():

    if(request.method=='POST'):

        room_name = request.form['room_name']

        username  = session['user_session']
        
        result = business.create_room(room_name, username)

        # room_type = request.form['room_type']

        # print(room_name, room_type)

        # print(result)

        if(result["status_code"] == 200):

            # room_name = result["room_name"]

            render_template("pin.html", result = result)

        return render_template("create_room.html", error_message = result['message'])

'''
http://127.0.0.1:5000/room
'''

@app.route("/room", methods = ['GET'])
def get_room():

    if 'room' in session:

        return render_template('room.html')

    result = {

        "message"     : "It seems like, you don't have access to this room",
        "status_code" : 401
    
    }

    return render_template("error.html", error_message = result['message'])

# @app.route("/room", methods = ['POST'])
# def post_room():
    
#     if(request.method=='POST'):

#         username = request.form['username']
#         room = request.form['room']
        
#         session['username'] = username
#         session['room'] = room

#         participants.append(session)
        
#         return render_template('room.html', session = session)
    
#     else:
        
#         if(session.get('username') is not None):
        
#             return render_template('room.html', session = session)
        
#         else:
        
#             return redirect(url_for('index'))


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

    emit('status', { 'message':  session.get('user_session') + ' has entered the room.' }, room=room )

@socketio.on('message', namespace='/room')
def message(data):

    # print(data)

    room = session.get('room')

    emit('message_response', { 'message': session.get('user_session') + ' : ' + data['message']}, room=room)

@socketio.on('leave', namespace='/room')
def leave(data):

    # print('leave')

    room = session.get('room')
    
    leave_room(room)

    session.clear()

    emit('status', { 'message':  session.get('user_session') + ' has left the room.' }, room=room )

if __name__ == '__main__':
    socketio.run(app, debug=True)
