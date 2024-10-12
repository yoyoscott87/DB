from flask import Blueprint, request, redirect, url_for
import mysql.connector

delete_bp = Blueprint('delete_bp', __name__)

db_config = {
    'user': 'root',
    'password': 'yoyoscott123',
    'host': 'localhost',
    'database': 'hw1'
}

@delete_bp.route('/delete', methods=['POST'])
def delete_posts():
    selected_ids = request.form.getlist('ids')  # Collect selected ids from the form

    if selected_ids:
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Create a DELETE query with parameterized placeholders
            delete_query = "DELETE FROM information WHERE id IN (%s)" % ','.join(['%s'] * len(selected_ids))
            cursor.execute(delete_query, selected_ids)

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
