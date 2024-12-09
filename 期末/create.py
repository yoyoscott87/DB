from flask import Flask, request, redirect, url_for, session
from datetime import datetime
from config import collection  # 使用 config.py 中的 MongoDB 集合配置

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于 Flask 的 session

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # 确保用户已登录
        if 'username' not in session:
            return "Unauthorized: You must log in to create a post", 403

        # 获取表单数据和用户信息
        name = request.form.get('name').strip()
        description = request.form.get('description').strip()
        author = session['username']

        # 检查表单是否填写完整
        if not name or not description:
            return "Name and Description cannot be empty", 400

        # 插入新文档并附加用户信息
        new_doc = {
            'name': name,
            'description': description,
            'created_by': author,  # 保存作者名称
        }
        collection.insert_one(new_doc)

        # 重定向回首页
        return redirect(url_for('index'))

    # 如果是 GET 请求，返回创建表单
    return '''
        <form method="POST">
            Name: <input type="text" name="name"><br>
            Description: <input type="text" name="description"><br>
            <input type="submit" value="Create">
        </form>
    '''

@app.route('/')
def index():
    # 展示所有文档的简易页面
    data = list(collection.find({}))
    content = '<h1>Startup Log</h1>'
    content += '<a href="/create">Create New Entry</a><br><br>'
    for doc in data:
        content += f'<div><strong>{doc["name"]}</strong>: {doc["description"]} {doc["created_by"]}</div>'
    return content

if __name__ == '__main__':
    app.run(debug=True)
