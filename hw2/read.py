from flask import Blueprint, render_template
import mysql.connector

read_bp = Blueprint('read_bp', __name__)

db_config = {
    'user': 'root',
    'password': 'yoyoscott123',
    'host': 'localhost',
    'database': 'game'
}

@read_bp.route('/')
def index():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
   # 正確的 SELECT 語句，選擇資料表中實際存在的欄位
    select_query = "SELECT * FROM game"
    cursor.execute(select_query)
    posts = cursor.fetchall()

    select_query_players = "SELECT * FROM players"
    cursor.execute(select_query_players)
    players = cursor.fetchall()

    select_query_players = "SELECT * FROM team_name"
    cursor.execute(select_query_players)
    teams = cursor.fetchall()
    
    cursor.close()
    conn.close()

    # 渲染模板並傳遞資料
    return render_template('index.html', posts=posts,players=players,teams=teams)
