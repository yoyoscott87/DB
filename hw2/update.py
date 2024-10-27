from flask import Blueprint, request, redirect, url_for
import mysql.connector

update_bp = Blueprint('update_bp', __name__)

db_config = {
    'user': 'root',
    'password': 'yoyoscott123',
    'host': 'localhost',
    'database': 'game'
}

@update_bp.route('/update/<int:post_id>', methods=['POST'])
def update_post(post_id):
    # 確保從表單中取得正確的值
    new_content = request.form.get(f'game_rank_{post_id}')  # 使用 f-string 來根據 post_id 動態取得表單資料
    new_content2 = request.form.get(f'country_{post_id}')
    new_content3 = request.form.get(f'team_name_{post_id}')
    # 檢查是否有輸入資料，沒有的話返回錯誤
    #if not new_content:
      #  return "No content to update", 400  # 返回 400 錯誤，告知無內容
    # 連接到資料庫並更新內容
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if new_content:
        update_game_query = "UPDATE game SET game_rank = %s WHERE idgame = %s"
        cursor.execute(update_game_query, (new_content, post_id))

    # 更新 players 表
    if new_content2:
        update_players_query = "UPDATE players SET country = %s WHERE idPlayers = %s"
        cursor.execute(update_players_query, (new_content2, post_id))

    # 更新 team_name 表
    if new_content3:
        update_team_name_query = "UPDATE team_name SET team_name = %s WHERE idteam_name = %s"
        cursor.execute(update_team_name_query, (new_content3, post_id))


    conn.commit()  # 提交更改
    cursor.close()
    conn.close()
    
    # 更新完成後，重定向到主頁面
    return redirect(url_for('read_bp.index'))
