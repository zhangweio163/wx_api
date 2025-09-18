import base64
import re
from typing import Optional, Dict
import demjson3
from requests_toolbelt.multipart.encoder import MultipartEncoder
from conf import setting
import time
import requests
from io import BytesIO


def random_str(length=16):
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_corp_application(session):
    """
    调用企业微信 getCorpApplication 接口，获取企业应用列表信息。

    参数：
        session: 已登录的 requests.Session 对象，包含有效 Cookie 等。

    返回：
        response: requests.Response 对象，可根据 response.json() 获取返回内容。
    """
    url = "https://work.weixin.qq.com/wework_admin/getCorpApplication"
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": "0.46411433146200576"  # 可以每次用 random.random() 动态生成
    }
    data = {
        "app_type": "0"
    }

    response = session.post(
        url,
        params=params,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://work.weixin.qq.com",
            "Referer": "https://work.weixin.qq.com/wework_admin/frame",
        }
    )
    #取出json里的data字段
    try:
        return response.json().get("data", {})
    except ValueError:
        print(f"获取企业应用列表失败，响应内容不是 JSON: {response.text}")
        return {}
def add_app(session,data):
    url = 'https://work.weixin.qq.com/wework_admin/apps/addOpenApiApp'
    params = {
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'timeZoneInfo[zone_offset]': '-8',
        'random': '0.5846023001064263'
    }

    response = session.post(url, headers=setting.headers, cookies=setting.cookies, params=params, data=data)
    print("状态码：", response.status_code)
    print("返回内容：", response.text)
    return response.json()

def upload_logo_image(
    session: requests.Session,
    image_base64_str: str,
    fields: Dict[str, str],
    filename: str = "logo.png",
    content_type: str = "image/png",
    boundary: str = "geckoformboundary7c630c345cbb4893fbc0ab644700eef7"
) -> Optional[str]:
    """
    上传企业微信应用 logo 图片（带裁剪参数）

    :param session: 已登录的 requests.Session 对象
    :param image_base64_str: 图片的 base64 编码字符串（不带 data:image/png;base64, 前缀）
    :param fields: 表单字段（除了文件外）
    :param filename: 上传文件名，默认 logo.png
    :param content_type: MIME 类型，默认 image/png
    :param boundary: multipart/form-data 的边界字符串
    :return: 成功时返回图片 URL，失败返回 None
    """
    timestamp = str(int(time.time() * 1000))
    callback = f"uploadLogoImageCallback{timestamp}"
    url = f"https://work.weixin.qq.com/wework_admin/uploadImage?callback={callback}"

    image_data = base64.b64decode(image_base64_str)
    image_file = BytesIO(image_data)

    # 添加文件字段
    fields = {
        **fields,
        "uploadImageFile": (filename, image_file, content_type)
    }

    m = MultipartEncoder(fields=fields, boundary=boundary)

    headers = {
        "Content-Type": m.content_type
    }

    try:
        resp = session.post(url, data=m, headers=headers, timeout=10)
        resp.raise_for_status()
        return parse_upload_response_from_html(resp.text)
    except requests.RequestException as e:
        print(f"上传失败：{e}")
        return None

def parse_upload_response_from_html(response_text: str, debug: bool = False) -> Optional[Dict]:
    """
    从 HTML 响应中提取 `var data = {...}` 并解析为 Python 字典。

    参数：
        response_text: HTML 文本内容
        debug: 是否打印调试信息

    返回：
        包含 src 等字段的字典，如果解析失败则返回 None。
    """
    # 提取 JS 中的 var data = {...};
    match = re.search(r"var\s+data\s*=\s*(\{.*?});", response_text, re.DOTALL)
    if not match:
        if debug:
            print("未找到 data 定义")
        return None

    data_str = match.group(1)

    try:
        data = demjson3.decode(data_str)
        if debug:
            print("解析成功，data =", data)

        return data
    except Exception as e:
        if debug:
            print(f"解析失败: {e}")
            print("原始 data_str:", data_str)
        return None

def get_corp_app_info(session, appid):
    """
    调用企业微信接口获取应用信息
    :param session: 已登录状态的 requests.Session 对象
    :param appid: 应用 ID（字符串）
    :return: 响应 JSON 数据（dict）或 None
    """
    base_url = "https://work.weixin.qq.com/wework_admin/apps/getCorpAppV2"

    # 构建查询参数
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": random.random(),  # 每次随机生成
        "app_id": appid
    }

    try:
        response = session.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        #返回 json的data
        return response.json().get("data", {})
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def update_corp_app_setting(session,
                            app_id: str,
                            type_: str,
                            app_flag: str,
                            url: str,
                            mobile_home_url: str,
                            pc_home_url: str,
                            app_type: str):
    """
    更新企业微信应用设置的通用函数
    :param session: 已登录状态的 requests.Session 对象
    :param app_id: 应用 ID
    :param type_: 类型（如 switch2web）
    :param app_flag: 应用标志位（如 18）
    :param url: 应用主入口 URL
    :param mobile_home_url: 移动端首页 URL
    :param pc_home_url: PC 端首页 URL
    :param app_type: 应用类型（如 APP_TYPE_MSG）
    :return: 返回请求的 JSON 结果，或 None
    """
    endpoint = "https://work.weixin.qq.com/wework_admin/apps/xcx/setting"
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": random.random()
    }

    data = {
        "app_id": app_id,
        "type": type_,
        "app_flag": app_flag,
        "url": url,
        "mobile_home_url": mobile_home_url,
        "pc_home_url": pc_home_url,
        "app_type": app_type
    }

    try:
        response = session.post(endpoint, params=params, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[update_corp_app_setting] 请求失败: {e}")
        return None


import random

def update_app_info_by_app_id(session: requests.Session, data: Dict) -> dict:
    """
    更新企业微信开放应用信息。

    :param session: 已登录状态的 requests.Session 对象，带有完整 Cookie 等信息
    :param data: 要提交的表单数据，字段包括 name, description, logoimage, app_id, visible_vid, visible_pid 等
    :return: 接口响应 JSON 字典
    """
    url = "https://work.weixin.qq.com/wework_admin/apps/saveOpenApiApp"
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": str(random.random())
    }

    # 提交 POST 请求
    response = session.post(url, params=params, data=data)
    try:
        return response.json()
    except Exception as e:
        return {"error": "响应非 JSON", "text": response.text, "exception": str(e)}

def delete_app_by_app_id(session: requests.Session,data : Dict) -> dict:
    """
    删除开放平台创建的企业微信应用。

    :param data:
    :param session: 已登录的 requests.Session 对象（包含完整的 Cookie）
    :return: 接口返回的 JSON 数据（或错误信息）
    """
    url = "https://work.weixin.qq.com/wework_admin/apps/delOpenApiApp"
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": str(random.random())
    }

    data = {
        "app_id": data.get("app_id"),
        "app_open_id": data.get("app_open_id"),
        "app_type": data.get("app_type", "APP_TYPE_MSG")
    }
    response = session.post(url, params=params, data=data)
    try:
        return response.json()
    except Exception as e:
        return {"error": "响应不是 JSON", "text": response.text, "exception": str(e)}