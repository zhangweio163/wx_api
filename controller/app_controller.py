import base64

from flask import jsonify, request, Blueprint

from base.app import with_session, app
from service import wx
from service.response_obj import ResetResponse
app_bp = Blueprint("app", __name__, url_prefix="/app")  # 统一前缀 /app


@app_bp.route("/get_corp_application", methods=["GET"])
@with_session
def get_corp_application(key_str,session):
    response = wx.get_corp_application(session)
    if response:
        return jsonify(ResetResponse.ok(response).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取企业应用失败").to_dict()), 500

@app_bp.route("/add_app", methods=["POST"])
@with_session
def add_app(key_str, session, data):
    response = wx.add_app(session, data)
    if response:
        return jsonify(ResetResponse.ok(response).to_dict())
    else:
        return jsonify(ResetResponse.fail("添加应用失败").to_dict()), 500



@app_bp.route("/upload_logo_image", methods=["POST"])
@with_session
def upload_logo_image(key_str, session, data):
    """
    上传企业微信应用 logo 图片（支持 form-data 中附带参数）
    """
    if 'image' not in request.files:
        return jsonify(ResetResponse.fail("Missing image file").to_dict()), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify(ResetResponse.fail("Empty filename").to_dict()), 400

    try:
        # 获取附带的裁剪参数等字段
        fields = {
            "file_path": request.form.get("file_path", ""),
            "target_vid": request.form.get("target_vid", ""),
            "crop_left": request.form.get("crop_left", "0"),
            "crop_top": request.form.get("crop_top", "0"),
            "crop_width": request.form.get("crop_width", "423"),
            "crop_height": request.form.get("crop_height", "423"),
            "degree": request.form.get("degree", "0"),
            "img_width": request.form.get("img_width", "750"),
            "img_height": request.form.get("img_height", "750"),
            "type": request.form.get("type", "IMG_ICO"),
            "_d2st": request.form.get("_d2st", "")
        }

        # 转 base64
        file_content = file.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')

        # 上传处理
        response = wx.upload_logo_image(session, image_base64, fields)

        if response:
            return jsonify(ResetResponse.ok(response).to_dict())
        else:
            return jsonify(ResetResponse.fail("上传logo图片失败").to_dict()), 500

    except Exception as e:
        return jsonify(ResetResponse.fail(f"处理图片出错: {str(e)}").to_dict()), 500

@app_bp.route("/get_app_by_app_id", methods=["GET"])
@with_session
def get_app_by_app_id(key_str, session):
    """
    根据应用ID获取应用信息
    :param key_str: 企业微信登录的key
    :param session: 已登录状态的 requests.Session 对象
    :param appid: 应用ID
    :return: 应用信息
    """
    appid = request.args.get("appid")
    response = wx.get_corp_app_info(session, appid)
    if response:
        return jsonify(ResetResponse.ok(response).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取应用信息失败").to_dict()), 500

@app_bp.route("/update_corp_app_setting", methods=["POST"])
@with_session
def update_corp_app_setting(key_str, session, data):
    """
    更新企业微信应用设置
    :param data:
    :param key_str: 企业微信登录的key
    :param session: 已登录状态的 requests.Session 对象
    :return: 更新结果
    """
    required_fields = ["app_id", "type_", "app_flag", "url", "mobile_home_url", "pc_home_url", "app_type"]
    if not all(field in data for field in required_fields):
        return jsonify(ResetResponse.fail("Missing required fields").to_dict()), 400

    response = wx.update_corp_app_setting(session, **data)
    if response:
        return jsonify(ResetResponse.ok(response).to_dict())
    else:
        return jsonify(ResetResponse.fail("更新应用设置失败").to_dict()), 500


@app_bp.route("/update_corp_app_info_setting", methods=["POST"])
@with_session
def update_corp_app_info_setting(key_str, session, data):
    """
    获取企业微信应用设置
    :param data:
    :param key_str: 企业微信登录的key
    :param session: 已登录状态的 requests.Session 对象
    :return: 应用设置
    """
    app_id = request.form.get("app_id")
    data = request.form.to_dict()  # 获取表单数据
    if not app_id:
        return jsonify(ResetResponse.fail("Missing app_id").to_dict()), 400
    response = wx.update_app_info_by_app_id(session, data)
    if response:
        return jsonify(ResetResponse.ok("修改成功",response).to_dict())
    else:
        return jsonify(ResetResponse.fail("获取应用设置失败").to_dict()), 500

@app_bp.route("/del_app_by_app_id", methods=["POST"])
@with_session
def del_app_by_app_id(key_str, session,data):
    """
    删除企业微信应用
    :param data:
    :param key_str: 企业微信登录的key
    :param session: 已登录状态的 requests.Session 对象
    :return: 删除结果
    """
    app_id = request.form.get("app_id")
    if not app_id:
        return jsonify(ResetResponse.fail("Missing app_id").to_dict()), 400
    response = wx.delete_app_by_app_id(session, request.form.to_dict())
    if response:
        return jsonify(ResetResponse.ok("删除成功", response).to_dict())
    else:
        return jsonify(ResetResponse.fail("删除应用失败").to_dict()), 500