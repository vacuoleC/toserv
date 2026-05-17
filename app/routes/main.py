from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Record, OperationLog
from app.forms import RecordForm

main_bp = Blueprint("main", __name__, url_prefix="/")


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


@main_bp.route("/")
@login_required
def index():
    """主页 - 记录列表"""
    page = request.args.get("page", 1, type=int)
    per_page = 10
    pagination = Record.query.filter_by(user_id=current_user.id) \
        .order_by(Record.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    _log_operation(current_user.id, "view", "record", None, "查看主页")
    db.session.commit()

    return render_template("main/index.html", pagination=pagination)


@main_bp.route("/record/new", methods=["GET", "POST"])
@login_required
def new_record():
    """新增记录"""
    form = RecordForm()
    if form.validate_on_submit():
        record = Record(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        db.session.add(record)
        _log_operation(current_user.id, "create", "record", None, f"新增记录: {form.title.data}")
        db.session.commit()
        flash("记录已保存", "success")
        return redirect(url_for("main.index"))

    return render_template("main/form.html", form=form, action="新增")


@main_bp.route("/record/<int:record_id>", methods=["GET"])
@login_required
def view_record(record_id):
    """查看单条记录"""
    record = Record.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
    _log_operation(current_user.id, "view", "record", record_id, f"查看记录: {record.title}")
    db.session.commit()
    return render_template("main/view.html", record=record)


@main_bp.route("/record/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
def edit_record(record_id):
    """编辑记录"""
    record = Record.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
    form = RecordForm(obj=record)

    if form.validate_on_submit():
        record.title = form.title.data
        record.content = form.content.data
        _log_operation(current_user.id, "update", "record", record_id, f"编辑记录: {form.title.data}")
        db.session.commit()
        flash("记录已更新", "success")
        return redirect(url_for("main.index"))

    return render_template("main/form.html", form=form, action="编辑", record=record)


@main_bp.route("/record/<int:record_id>/delete", methods=["POST"])
@login_required
def delete_record(record_id):
    """删除记录"""
    record = Record.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
    title = record.title
    db.session.delete(record)
    _log_operation(current_user.id, "delete", "record", record_id, f"删除记录: {title}")
    db.session.commit()
    flash("记录已删除", "warning")
    return redirect(url_for("main.index"))


@main_bp.route("/record/batch-delete", methods=["POST"])
@login_required
def batch_delete_records():
    """批量删除记录"""
    ids = request.form.getlist("record_ids")
    if not ids:
        flash("请选择要删除的记录", "warning")
        return redirect(url_for("main.index"))

    count = 0
    for record_id in ids:
        record = Record.query.filter_by(id=int(record_id), user_id=current_user.id).first()
        if record:
            db.session.delete(record)
            count += 1

    _log_operation(current_user.id, "delete", "record", None, f"批量删除 {count} 条记录")
    db.session.commit()
    flash(f"已删除 {count} 条记录", "warning")
    return redirect(url_for("main.index"))