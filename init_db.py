"""初始化数据库和默认管理员"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def init_db():
    app = create_app()
    with app.app_context():
        # 检查是否已有用户
        if User.query.first() is None:
            admin = User(username="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("✓ 默认管理员已创建: admin / admin123")
        else:
            print("用户已存在，跳过初始化")

if __name__ == "__main__":
    init_db()
    print("✓ 数据库初始化完成")