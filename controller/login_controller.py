# ======= 登录路由 =======
from flask import jsonify, Blueprint, request

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

@login_bp.route("/confirm_captcha", methods=["POST"])
@with_session
def confirm_captcha(key_str, session, data):
    captcha_code = data.get("captcha_code")
    tl_key = data.get("tl_key")
    if not captcha_code or not tl_key:
        return jsonify(ResetResponse.fail("参数不完整").to_dict()), 400
    response = get_wx_cookie.confirm_captcha(session, captcha_code, tl_key)
    if response:
        return jsonify(ResetResponse.ok("验证验证码成功", response).to_dict())
    else:
        return jsonify(ResetResponse.fail("验证验证码失败").to_dict()), 500

@login_bp.route("/login_by_captcha", methods=["POST"])
@with_session
def login_by_captcha(key_str, session, data):
    tl_key = data.get("tl_key")
    if not tl_key:
        return jsonify(ResetResponse.fail("参数不完整").to_dict()), 400
    response = get_wx_cookie.after_captcha_success(session, tl_key)
    if 'result' in response:
        result = response['result']
        if 'errCode' in result:
            return jsonify(ResetResponse.fail(response).to_dict())
    if response:
        return jsonify(ResetResponse.ok("登录成功", response).to_dict())
    else:
        return jsonify(ResetResponse.fail("登录失败").to_dict()), 500


@login_bp.route("/create_wx_session", methods=["POST"])
def create_wx_session():
    data = request.json
    cookies = data.get("cookies")
    if not cookies:
        return jsonify(ResetResponse.fail("参数不完整").to_dict()), 400
    key_str = get_wx_cookie.make_wx_session_by_cookie(cookies)
    if key_str:
        return jsonify(ResetResponse.ok("创建会话成功", {"key_str": key_str}).to_dict())
    else:
        return jsonify(ResetResponse.fail("创建会话失败,无效的cookies").to_dict()), 500