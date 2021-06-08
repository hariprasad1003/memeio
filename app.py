'''

author - Hari Prasad

sources - 

https://stackoverflow.com/questions/13772884/css-problems-with-flask-web-app

'''

from flask import Flask , render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_session import Session

app = Flask(__name__)

socketio = SocketIO(app)

@app.route("/", methods = ['GET', 'POST'])
def index():
    return render_template("home.html")

@socketio.on('connect')
def connected():
    print('connect')

@socketio.on('join')
def on_join(data):

    username = data['username']
    room = data['room']
    
    session['username'] = username
    session['room'] = room

    join_room(room)

    print(username, room)

    emit('status', { 'message':  session.get('username') + ' has entered the room.' }, room=room )

# @socketio.on('message')
# def message(json):

#     room = session.get('room')

#     emit('message_response', { 'message': session.get('username') + ' : ' + message['msg']}, room=room)

@socketio.on('leave')
def on_leave(data):
    
    username = data['username']
    room = data['room']
    
    leave_room(room)

    session.clear()

    emit('status', { 'message':  session.get('username') + ' has left the room.' }, room=room )

if __name__ == '__main__':
    socketio.run(app, debug=True)
