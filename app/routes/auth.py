"""认证路由

职责：接收登录/登出请求，调用服务，返回响应
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.services import UserService, OperationLogService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    from app.forms import LoginForm
    form = LoginForm()

    if form.validate_on_submit():
        user = UserService.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user, remember=True)
            OperationLogService.log(user.id, "login", "user", "用户登录", user.id)
            db.session.commit()
            next_page = request.args.get("next")
            return redirect(next_page if next_page else url_for("main.index"))
        else:
            flash("用户名或密码错误", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """退出登录"""
    OperationLogService.log(current_user.id, "logout", "user", "用户退出", current_user.id)
    db.session.commit()
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("auth.login"))