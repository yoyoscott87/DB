from flask import Blueprint, request, redirect, url_for
import mysql.connector

create_bp = Blueprint('create_bp', __name__)

db_config = {
    'user': 'root',
    'password': 'yoyoscott123',
    'host': 'localhost',
    'database': 'hw1'
}

@create_bp.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    birth = request.form['birth']
    gender = request.form['gender']
    email = request.form['email']

    # 建立資料庫連接
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 寫入資料到 MySQL，這裡是正確的 INSERT 語法
    insert_query = "INSERT INTO information (name, birth, gender, email) VALUES (%s, %s, %s, %s)"
    values = (name, birth, gender, email)
    cursor.execute(insert_query, values)
    conn.commit()

    # 關閉連接
    cursor.close()
    conn.close()

    return redirect(url_for('read_bp.index'))
