from flask import Flask, request, jsonify, session, render_template, redirect, url_for, send_from_directory
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'yourSecretKey'

# MongoDB connection
app.config['MONGO_URI'] = 'mongodb://localhost:27017/fianl'
mongo = PyMongo(app)

# Folder for image uploads
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('threads.html', username=session.get('username'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if mongo.db.user.find_one({'username': username}):
            return 'Username already exists', 400

        hashed_password = generate_password_hash(password)
        mongo.db.user.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = mongo.db.user.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = username
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/create.html')
def create_thread():
    return render_template('create.html')

@app.route('/threads', methods=['GET', 'POST'])
def threads():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image = request.files.get('image')

        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
        else:
            image_path = None

        thread = {
            'title': title,
            'description': description,
            'image': image.filename if image else None,
            'messages': [],
            'created_by': session['username'],
            'closed': False
        }
        mongo.db.threads.insert_one(thread)
        return redirect(url_for('threads'))

    threads = list(mongo.db.threads.find())
    return render_template('threads.html', threads=threads)

@app.route('/threads/<thread_id>', methods=['GET', 'POST'])
def thread_detail(thread_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    thread = mongo.db.threads.find_one({'_id': ObjectId(thread_id)})

    if not thread:
        return 'Thread not found', 404

    if thread.get('closed'):
        return render_template('thread_closed.html', thread=thread)

    if request.method == 'POST':
        text = request.form.get('text')
        message = {
            '_id': ObjectId(),
            'user': session.get('username'),
            'text': text,
            'createdAt': datetime.utcnow()
        }
        mongo.db.threads.update_one(
            {'_id': ObjectId(thread_id)},
            {'$push': {'messages': message}}
        )
        return redirect(url_for('thread_detail', thread_id=thread_id))

    return render_template('thread_detail.html', thread=thread)

@app.route('/threads/<thread_id>/close', methods=['POST'])
def close_thread(thread_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    thread = mongo.db.threads.find_one({'_id': ObjectId(thread_id)})

    if not thread:
        return 'Thread not found', 404

    if thread['created_by'] != session['username']:
        return 'You are not authorized to close this thread', 403

    mongo.db.threads.update_one(
        {'_id': ObjectId(thread_id)},
        {'$set': {'closed': True}}
    )
    return redirect(url_for('threads'))

@app.route('/threads/<thread_id>/delete', methods=['POST'])
def delete_thread(thread_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    thread = mongo.db.threads.find_one({'_id': ObjectId(thread_id)})

    if not thread:
        return 'Thread not found', 404

    if thread['created_by'] != session['username']:
        return 'You are not authorized to delete this thread', 403

    mongo.db.threads.delete_one({'_id': ObjectId(thread_id)})
    return redirect(url_for('threads'))

@app.route('/threads/<thread_id>/messages/<message_id>', methods=['POST'])
def delete_message(thread_id, message_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    thread = mongo.db.threads.find_one({'_id': ObjectId(thread_id)})

    if not thread:
        return 'Thread not found', 404

    updated_messages = [
        message for message in thread['messages']
        if str(message['_id']) != message_id or message['user'] != session['username']
    ]

    if len(updated_messages) == len(thread['messages']):
        return 'You can only delete your own messages', 403

    mongo.db.threads.update_one(
        {'_id': ObjectId(thread_id)},
        {'$set': {'messages': updated_messages}}
    )
    return redirect(url_for('thread_detail', thread_id=thread_id))

@app.route('/threads/<thread_id>/update', methods=['GET', 'POST'])
def update_thread(thread_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    thread = mongo.db.threads.find_one({'_id': ObjectId(thread_id)})
    if not thread:
        return 'Thread not found', 404

    if thread['created_by'] != session['username']:
        return 'You are not authorized to edit this thread', 403

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        mongo.db.threads.update_one(
            {'_id': ObjectId(thread_id)},
            {'$set': {'title': title, 'description': description}}
        )
        return redirect(url_for('thread_detail', thread_id=thread_id))

    return render_template('update_thread.html', thread=thread)

if __name__ == '__main__':
    app.run(debug=True)
