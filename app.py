'''

author - Hari Prasad

sources - 

https://stackoverflow.com/questions/13772884/css-problems-with-flask-web-app

'''

from flask import Flask , render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_session import Session

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

socketio = SocketIO(app, manage_session=False)

participants=[]

@app.route("/", methods = ['GET', 'POST'])
def index():
    return render_template("home.html")

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
