from flask import Blueprint, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os
from config import collection, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
import uuid
# 配置 Blueprint
replies_bp = Blueprint('replies', __name__)

# 確保上傳文件夾存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 文件類型檢查
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 添加回覆功能
@replies_bp.route('/replies/<id>', methods=['POST'])
def reply(id):
    try:
        # 查找文檔
        doc = collection.find_one({"_id": ObjectId(id)})
        if not doc:
            return "Document not found", 404

        # 使用 session 中的用戶名（如果已登入）
        user = session.get('username', 'Anonymous').strip()
        message = request.form.get('message', '').strip()

        # 確保內容或圖片至少有一個
        if not message and 'image' not in request.files:
            return "Message and image cannot both be empty", 400

        # 處理圖片上傳
        image_url = None
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)
                image_url = f"/static/uploads/{filename}"

        # 構造回覆數據
        reply = {
            "reply_id": str(uuid.uuid4()),
            "user": user,
            "message": message,
            "image_url": image_url
        }

        # 更新文檔，添加新的回覆
        collection.update_one(
            {"_id": ObjectId(id)},
            {"$push": {"replies": reply}}
        )

        flash("Reply added successfully!")
        return redirect(url_for('index'))
    except Exception as e:
        return str(e), 400
@replies_bp.route('/replies/delete/<post_id>/<int:reply_index>', methods=['POST'])
def delete_reply(post_id, reply_index):
    try:
        # 确保用户已登录
        if 'username' not in session:
            return "Unauthorized", 403

        # 检查帖子是否存在
        post = collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            return "Post not found", 404

        # 确保用户有权限删除回复（只有管理员或回复的创建者可删除）
        if session['username'] != 'admin' and post['replies'][reply_index]['user'] != session['username']:
            return "Unauthorized", 403

        # 删除指定回复
        post['replies'].pop(reply_index)
        collection.update_one({"_id": ObjectId(post_id)}, {"$set": {"replies": post['replies']}})

        return redirect(url_for('index'))
    except Exception as e:
        return str(e), 400
