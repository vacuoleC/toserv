from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, OperationLog
from app.forms import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            _log_operation(user.id, "login", "user", user.id, "用户登录")
            db.session.commit()

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("main.index"))
        else:
            flash("用户名或密码错误", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """退出登录"""
    _log_operation(current_user.id, "logout", "user", current_user.id, "用户退出")
    db.session.commit()
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("auth.login"))


def _log_operation(user_id, action, target_type, target_id, description):
    """记录操作日志"""
    log = OperationLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        description=description
    )
    db.session.add(log)