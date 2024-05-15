from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store connected clients and their nicknames
clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    session['sid'] = request.sid
    emit('update_users', list(clients.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    nickname = clients.pop(session['sid'], None)
    if nickname:
        emit('update_users', list(clients.values()), broadcast=True)

@socketio.on('set_nickname')
def set_nickname(nickname):
    clients[session['sid']] = nickname
    emit('update_users', list(clients.values()), broadcast=True)

@socketio.on('message')
def handle_message(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sender = clients.get(session['sid'], 'Unknown')
    if data['recipient'] == 'all':
        emit('message', {'sender': sender, 'message': data['message'], 'timestamp': timestamp}, broadcast=True)
    else:
        recipient_sid = next((sid for sid, name in clients.items() if name == data['recipient']), None)
        if recipient_sid:
            emit('message', {'sender': sender, 'message': data['message'], 'timestamp': timestamp}, room=recipient_sid)
        else:
            emit('error', 'Recipient not found')

if __name__ == '__main__':
    socketio.run(app)
