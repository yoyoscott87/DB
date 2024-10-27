from flask import Blueprint, request, redirect, url_for
import mysql.connector

delete_bp = Blueprint('delete_bp', __name__)

db_config = {
    'user': 'root',
    'password': 'yoyoscott123',
    'host': 'localhost',
    'database': 'game'
}

@delete_bp.route('/delete', methods=['POST'])
def delete_posts():
        selected_ids = request.form.getlist('idgames')  # Collect selected ids from the form
        selected_ids2 = request.form.getlist('idPlayerss')
        selected_ids3 = request.form.getlist('idteam_ids')

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Check and delete from game table
            if selected_ids:
                delete_game_query = "DELETE FROM game WHERE idgame IN (%s)" % ','.join(['%s'] * len(selected_ids))
                cursor.execute(delete_game_query, selected_ids)
            if selected_ids2:
                delete_game_query = "DELETE FROM players WHERE idPlayers IN (%s)" % ','.join(['%s'] * len(selected_ids2))
                cursor.execute(delete_game_query, selected_ids2)
            if selected_ids3:
                delete_game_query = "DELETE FROM team_name WHERE idteam_name IN (%s)" % ','.join(['%s'] * len(selected_ids3))
                cursor.execute(delete_game_query, selected_ids3)
            conn.commit()

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            # Optionally, handle error (e.g., log or return an error message)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Redirect to a view that lists the current records
        return redirect(url_for('read_bp.index'))
