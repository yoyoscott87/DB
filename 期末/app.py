from flask import Flask, render_template, request, redirect, url_for, session
from bson.objectid import ObjectId
from config import collection  # Import collection from config.py
from update import update_bp  # Import the update blueprint
from delete import delete_bp  # Import the delete blueprint
from reply import replies_bp
from auth import auth_bp
from config import collection, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
# 配置 Flask 的上傳文件夾


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(update_bp)
app.register_blueprint(delete_bp)
app.register_blueprint(replies_bp)
app.register_blueprint(auth_bp)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Display documents (Read)
@app.route('/')
def index():
    show_all = session.get('show_all', False)
    data = list(collection.find({})) if show_all else []
    for doc in data:
        doc['_id'] = str(doc['_id'])
    return render_template('index.html', data=data, results=None, show_all=show_all)

# Create a new document (Create)
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        new_doc = {'name': name, 'description': description}
        collection.insert_one(new_doc)
        return redirect(url_for('index'))
    return render_template('create.html')

# Search documents (Read with keyword)
@app.route('/search', methods=['POST'])
def search():
    query_text = str(request.form.get("query", ""))
    regex_query = {"$regex": query_text, "$options": "i"}
    query = {"$or": [{field: regex_query} for field in ["name", "description", "hostname", "startTime", "startTimeLocal", "pid"]]}

    results = list(collection.find(query))
    for result in results:
        result['_id'] = str(result['_id'])

    # 搜尋結果，不顯示全部資料
    return render_template('index.html', data=[], results=results, show_all=session.get('show_all', False))

# Toggle show_all feature
@app.route('/show_all', methods=['GET'])
def show_all():
    session['show_all'] = not session.get('show_all', False)
    return redirect(url_for('index'))

# Delete a document (Delete)
@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    try:
        collection.delete_one({"_id": ObjectId(id)})
        return redirect(url_for('index'))
    except Exception as e:
        return str(e), 400
@app.route('/reply/<id>', methods=['POST'])
def reply(id):
    try:
        # 查找文檔
        doc = collection.find_one({"_id": ObjectId(id)})
        if not doc:
            return "Document not found", 404

        # 獲取表單數據
        user = request.form.get('user', 'Anonymous').strip()
        message = request.form.get('message', '').strip()

        if not message:
            return "Message cannot be empty", 400

        # 初始化 replies 字段並添加新的留言
        collection.update_one(
            {"_id": ObjectId(id)},
            {"$push": {"replies": {"user": user, "message": message}}}
        )

        # 返回首頁
        return redirect(url_for('index'))
    except Exception as e:
        return str(e), 400
if __name__ == '__main__':
    app.run(debug=True)
