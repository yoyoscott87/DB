from flask import Blueprint, redirect, url_for, session
from bson.objectid import ObjectId, InvalidId
from config import collection

# Create a Blueprint for delete functionality
delete_bp = Blueprint('delete', __name__)

@delete_bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    try:
        # 確保使用者已登入
        if 'username' not in session:
            return "Unauthorized. Please log in.", 403

        # 驗證 ID 格式是否正確
        try:
            obj_id = ObjectId(id)
        except InvalidId:
            return "Invalid document ID", 400

        # 查找文檔
        doc = collection.find_one({"_id": obj_id})
        if not doc:
            return "Document not found", 404

        # 僅限創建者或管理員刪除
        if doc.get('created_by') != session['username'] and session['username'] != 'admin':
            return "Unauthorized. You do not have permission to delete this entry.", 403

        # 執行刪除操作
        collection.delete_one({"_id": obj_id})
        return redirect(url_for('index'))
    except Exception as e:
        return str(e), 400
