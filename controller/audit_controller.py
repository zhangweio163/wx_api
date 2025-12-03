import base64

from flask import jsonify, request, Blueprint

from base.app import with_session, app
from service import wx_audit
from service.response_obj import ResetResponse
app_bp = Blueprint("audit", __name__, url_prefix="/audit")  # 统一前缀 /app


@app_bp.route("/get_audit_list", methods=["GET"])
@with_session
def get_audit_list(key_str,session):
    response = wx_audit.get_audit_list(session)
    if response:
        return jsonify(ResetResponse.ok(data=response).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取企业审批列表失败").to_dict()), 500

@app_bp.route("/async_all_audit_list", methods=["GET"])
@with_session
def async_all_audit_list(key_str, session):
    response = wx_audit.async_all_audit(session)
    if response:
        return jsonify(ResetResponse.ok(data=response).to_dict())
    else:
        return jsonify(ResetResponse.fail("添加应用失败").to_dict()), 500



@app_bp.route("/get_audit_info", methods=["POST"])
@with_session
def get_audit_info(key_str, session, data):
    response = wx_audit.get_audit_info(session = session, **data)
    if response:
        return jsonify(ResetResponse.ok(data=response).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取审批记录失败").to_dict()), 500