from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import users_collection  # MongoDB 集合
from datetime import datetime

# 定義 Blueprint
auth_bp = Blueprint('auth', __name__)

# 註冊路由
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # 檢查用戶是否已存在
        if users_collection.find_one({"email": email}):
            flash('Email already registered. Please login.')
            return redirect(url_for('auth.login'))

        # 插入新用戶
        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": password,
            "created_at": datetime.utcnow()
        })
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

# 登錄路由
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # 查找用戶
        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            flash('Login successful!')
            return redirect(url_for('index'))
        flash('Invalid email or password.')
    return render_template('login.html')

# 登出路由
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
