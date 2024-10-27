from flask import Blueprint, render_template
import mysql.connector

join_bp = Blueprint('join_bp', __name__)

db_config = {
    'user': 'root',
    'password': 'yoyoscott123',
    'host': 'localhost',
    'database': 'game'
}

@join_bp.route('/join_data')
def index():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 更新后的 JOIN 查询
    select_query = """
    SELECT 
        p.name AS player_name,
        g.game_name,
        g.game_rank,
        p.country,
        t.team_name
    FROM 
        game g
    JOIN 
        players p ON g.uid = p.uid  -- 连接 game 表和 players 表
    JOIN 
        team_name t ON p.name = t.name  -- 连接 players 表和 team_name 表
    LIMIT 0, 1000
    """
    
    cursor.execute(select_query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    # 渲染模板并传递数据
    return render_template('join.html', results=results)
