import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置"""

    # 密钥（生产环境请改掉）
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-prod"

    # 数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        f"sqlite:///{os.path.join(basedir, 'data', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # 文件上传
    UPLOAD_FOLDER = os.path.join(basedir, "data", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx", "xls", "xlsx"}