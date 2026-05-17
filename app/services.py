"""业务逻辑服务层

职责：所有业务规则和数据库操作都放在这里
routes 只负责接收请求、调用服务、返回响应
"""
from datetime import datetime
from app import db
from app.models import User, Record, OperationLog


# ========== 用户服务 ==========

class UserService:
    """用户相关业务逻辑"""

    @staticmethod
    def authenticate(username, password):
        """验证用户登录，返回用户或 None"""
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def create_user(username, password):
        """创建新用户"""
        if User.query.filter_by(username=username).first():
            raise ValueError("用户名已存在")
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user


# ========== 记录服务 ==========

class RecordService:
    """记录相关业务逻辑"""

    @staticmethod
    def create(title, content, user_id):
        """新建记录"""
        record = Record(title=title, content=content, user_id=user_id)
        db.session.add(record)
        OperationLogService.log(user_id, "create", "record", f"新增记录: {title}")
        db.session.commit()
        return record

    @staticmethod
    def get_by_id(record_id, user_id):
        """获取单条记录（带权限校验）"""
        return Record.query.filter_by(id=record_id, user_id=user_id).first_or_404()

    @staticmethod
    def list_by_user(user_id, page=1, per_page=10):
        """分页获取用户的记录"""
        return Record.query.filter_by(user_id=user_id) \
            .order_by(Record.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def update(record, title, content):
        """更新记录"""
        record.title = title
        record.content = content
        OperationLogService.log(record.user_id, "update", "record",
                                f"编辑记录: {title}")
        db.session.commit()
        return record

    @staticmethod
    def delete(record):
        """删除记录"""
        OperationLogService.log(record.user_id, "delete", "record",
                                f"删除记录: {record.title}")
        db.session.delete(record)
        db.session.commit()

    @staticmethod
    def batch_delete(record_ids, user_id):
        """批量删除记录"""
        count = 0
        for record_id in record_ids:
            record = Record.query.filter_by(
                id=int(record_id), user_id=user_id
            ).first()
            if record:
                db.session.delete(record)
                count += 1
        OperationLogService.log(user_id, "delete", "record",
                               f"批量删除 {count} 条记录")
        db.session.commit()
        return count


# ========== 日志服务 ==========

class OperationLogService:
    """操作日志业务逻辑"""

    @staticmethod
    def log(user_id, action, target_type, description, target_id=None):
        """记录一条操作日志"""
        log = OperationLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
        )
        db.session.add(log)