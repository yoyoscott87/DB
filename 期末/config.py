# config.py
from pymongo import MongoClient
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
client = MongoClient('mongodb://localhost:27017/')
db = client['local']  # Replace with your database name
collection = db['startup_log']  # Replace with your collection name

db2 = client["local"]  # 指定 local 資料庫
users_collection = db["user"]  # 用戶集合