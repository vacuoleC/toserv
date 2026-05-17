"""业务路由

职责：接收增删改查请求，调用服务，返回响应
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.services import RecordService, OperationLogService
from app.forms import RecordForm

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    """主页 - 记录列表"""
    page = request.args.get("page", 1, type=int)
    pagination = RecordService.list_by_user(current_user.id, page=page)
    OperationLogService.log(current_user.id, "view", "record", "查看主页")
    db.session.commit()
    return render_template("main/index.html", pagination=pagination)


@main_bp.route("/record/new", methods=["GET", "POST"])
@login_required
def new_record():
    """新增记录"""
    form = RecordForm()
    if form.validate_on_submit():
        RecordService.create(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
        )
        flash("记录已保存", "success")
        return redirect(url_for("main.index"))
    return render_template("main/form.html", form=form, action="新增")


@main_bp.route("/record/<int:record_id>", methods=["GET"])
@login_required
def view_record(record_id):
    """查看单条记录"""
    record = RecordService.get_by_id(record_id, current_user.id)
    OperationLogService.log(
        current_user.id, "view", "record",
        f"查看记录: {record.title}", record_id
    )
    db.session.commit()
    return render_template("main/view.html", record=record)


@main_bp.route("/record/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
def edit_record(record_id):
    """编辑记录"""
    record = RecordService.get_by_id(record_id, current_user.id)
    from app.forms import RecordForm
    form = RecordForm(obj=record)
    if form.validate_on_submit():
        RecordService.update(record, form.title.data, form.content.data)
        flash("记录已更新", "success")
        return redirect(url_for("main.index"))
    return render_template("main/form.html", form=form, action="编辑", record=record)


@main_bp.route("/record/<int:record_id>/delete", methods=["POST"])
@login_required
def delete_record(record_id):
    """删除记录"""
    record = RecordService.get_by_id(record_id, current_user.id)
    RecordService.delete(record)
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
    count = RecordService.batch_delete(ids, current_user.id)
    flash(f"已删除 {count} 条记录", "warning")
    return redirect(url_for("main.index"))