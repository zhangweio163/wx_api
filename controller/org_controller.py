from flask import jsonify, Blueprint

from base.app import with_session
from service import wx_person
from service.response_obj import ResetResponse
from flask import send_file, after_this_request
import os
org_bp = Blueprint("org", __name__, url_prefix="/org")

@org_bp.route("/get_wx_organization", methods=["GET"])
@with_session
def get_wx_organization(key_str, session):
    response = wx_person.get_org(session)
    if response:
        return jsonify(ResetResponse.ok(response).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取企业组织架构失败").to_dict()), 500

@org_bp.route("/get_wx_user", methods=["GET"])
@with_session
def get_wx_user(key_str, session):
    response = wx_person.get_org_user(session)
    if response:
        return jsonify(ResetResponse.ok(response).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取企业用户信息失败").to_dict()), 500

@org_bp.route("/out_put_user_excel", methods=["GET"])
@with_session
def out_put_user_excel(key_str, session):
    file_path = wx_person.export_excel_person(session)
    if not file_path or not os.path.exists(file_path):
        return jsonify(ResetResponse.fail("文件生成失败").to_dict()), 500

    @after_this_request
    def remove_file(response):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            # 可记录日志，但不影响下载响应
            pass
        return response

    # 以附件方式下载，文件名从路径提取
    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

