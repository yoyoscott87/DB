from flask import Blueprint, render_template, request, redirect, url_for, session
from bson.objectid import ObjectId, InvalidId
from config import collection

# Create a Blueprint for the update functionality
update_bp = Blueprint('update', __name__)

@update_bp.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    try:
        # 確保使用者已登入
        if 'username' not in session:
            return "Unauthorized. Please log in.", 403

        # 驗證 ID 格式是否正確
        try:
            object_id = ObjectId(id)
        except InvalidId:
            return "Invalid document ID", 400

        # 查找文檔
        doc = collection.find_one({"_id": object_id})
        if not doc:
            return "Document not found", 404

        # 僅限創建者或管理員更新
        if doc.get('created_by') != session['username'] and session['username'] != 'admin':
            return "Unauthorized. You do not have permission to update this entry.", 403

        # 若為 POST，更新數據
        if request.method == 'POST':
            update_data = {
                key: value for key, value in request.form.items() if key != '_id'
            }
            collection.update_one(
                {"_id": object_id},
                {"$set": update_data, "$setOnInsert": {"updated_by": session['username']}}
            )
            return redirect(url_for('index'))

        # 若為 GET，預填表單數據
        doc['_id'] = str(doc['_id'])  # 將 _id 轉為字串供模板使用
        return render_template('update.html', entry=doc)

    except Exception as e:
        return str(e), 400
