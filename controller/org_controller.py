from flask import jsonify, Blueprint

from base.app import with_session
from service import wx_person
from service.response_obj import ResetResponse

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
