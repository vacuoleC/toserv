import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name="config.Config"):
    """Flask 应用工厂"""
    app = Flask(
        __name__,
        template_folder=os.path.join(basedir, "..", "templates"),
        static_folder=os.path.join(basedir, "..", "static"),
    )
    app.config.from_object(config_name)

    # 确保上传目录存在
    os.makedirs(app.config.get(
        "UPLOAD_FOLDER",
        os.path.join(basedir, "..", "data", "uploads")
    ), exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录"
    login_manager.login_message_category = "warning"

    # 注册 user_loader（必须在 init_app 之后）
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        with app.app_context():
            return User.query.get(int(user_id))

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app