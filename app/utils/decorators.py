from functools import wraps
from flask import request, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """管理员权限装饰器（预留）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function