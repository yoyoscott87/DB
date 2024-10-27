from flask import Blueprint, request, redirect, url_for
import mysql.connector

create_bp = Blueprint('create_bp', __name__)

db_config = {
    'user': 'root',
    'password': 'yoyoscott123',
    'host': 'localhost',
    'database': 'game'
}

@create_bp.route('/submit', methods=['POST'])
def submit():
    uid = request.form['uid']
    name = request.form['name']
    game_name = request.form['game_name']
    game_rank = request.form['game_rank']
    birth = request.form['birth']
    country = request.form['country']
    team_name = request.form['team_name']
    # 建立資料庫連接
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 寫入資料到 MySQL，這裡是正確的 INSERT 語法
    insert_query = "INSERT INTO game (uid, name, game_name, game_rank) VALUES (%s, %s, %s, %s)"
    values_game = (uid, name, game_name, game_rank)
    cursor.execute(insert_query, values_game)

    insert_query2 = "INSERT INTO players (name,uid,birth, country) VALUES (%s, %s, %s, %s)"
    values_players = (name,uid,birth, country)
    cursor.execute(insert_query2, values_players)

    insert_query3 = "INSERT INTO team_name (uid,name,team_name) VALUES (%s, %s, %s)"
    values_team = (uid,name,team_name,)
    cursor.execute(insert_query3, values_team)

    conn.commit()

    # 關閉連接
    cursor.close()
    conn.close()

    return redirect(url_for('read_bp.index'))
