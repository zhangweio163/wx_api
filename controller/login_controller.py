# ======= 登录路由 =======
from flask import jsonify, Blueprint

from base.app import with_session
from base.check_session import check_session
from service import get_wx_cookie
from service.response_obj import ResetResponse

login_bp = Blueprint("login", __name__, url_prefix="/login")  # 统一前缀 /login
@login_bp.route("/check_login_type",methods=["GET"])
@with_session
def check_login_type(key_str, session):
    """
    检查登录类型
    :param key_str: 企业微信登录的key
    :param session: 已登录状态的 requests.Session 对象
    :return: 登录类型
    """
    response = get_wx_cookie.check_login_type(session)
    if response:
        return jsonify(ResetResponse.ok("检查登录类型成功",response).to_dict())
    else:
        return jsonify(ResetResponse.fail("检查登录类型失败").to_dict()), 500

@login_bp.route("/get_login_key", methods=["GET"])
def get_login_key():
    key_str = get_wx_cookie.get_wx_cookieKey() # 获取企业微信登录的key
    if key_str:
        return jsonify(ResetResponse.ok("获取key成功", {"key_str": key_str}).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取key失败").to_dict()), 500
@login_bp.route("/get_qr_code", methods=["GET"])
@with_session
def get_qr_code(key_str, session):
    image_base64 = get_wx_cookie.get_qrcode_image_base64(key_str, session)
    if image_base64:
        return jsonify(ResetResponse.ok("获取二维码成功", {"image_base64": image_base64}).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取二维码失败").to_dict()), 500


@login_bp.route("/get_qr_status", methods=["GET"])
@with_session
def get_qr_status(key_str, session):
    report = get_wx_cookie.get_report(key_str, session)
    if report:
        return jsonify(ResetResponse.ok(report).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取二维码状态失败").to_dict()), 500


@login_bp.route("/get_wx_cookie", methods=["GET"])
@with_session
def get_wx_cookie_route(key_str, session):
    #先检查扫码状态
    report = get_wx_cookie.get_report(key_str, session)
    if not report:
        return jsonify(ResetResponse.fail("获取二维码状态失败").to_dict()), 500
    if  check_session(report):
        return jsonify(ResetResponse.fail("页面已过期，请重新扫码").to_dict()), 400
    if report["data"] and report["data"]["status"] != "QRCODE_SCAN_SUCC":
        return jsonify(ResetResponse.fail("二维码未扫码或扫码失败").to_dict()), 400
    cookies = get_wx_cookie.get_cookie(key_str, session)
    if 'result' in cookies:
        result = cookies['result']
        if 'errCode' in result:
            return jsonify(ResetResponse.fail(cookies).to_dict())
    if cookies:
        return jsonify(ResetResponse.ok("调用企业微信登录接口成功", cookies).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取企业微信cookie失败").to_dict()), 500