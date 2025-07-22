import base64
import json
import random
import time
from datetime import datetime

from base import wx_session
import requests
from base.redis_connector import redis_conn
from conf import setting


def get_cookie(key_str,session):

    auth_data = get_report(key_str,session)
    if not auth_data or 'data' not in auth_data:
        return auth_data
    auth_data = auth_data['data']
    #获取会话地址
    setting.headers.update({
        "Referer": "https://work.weixin.qq.com/wework_admin/wwqrlogin/mng/login_qrcode?login_type=login_admin&callback=wwqrloginCallback_1752806305697&redirect_uri=https%3A%2F%2Fwork.weixin.qq.com%2Fwework_admin%2Floginpage_wx%3F_r%3D105%26url_hash%3D&crossorigin=1"
    })
    cookies = {
        "wwrtx.i18n_lan": "zh",
        "ww_lang": "cn,zh",
        "wwrtx.c_gdpr": "0",
        "wwrtx.ref": "direct",
        "wwrtx.refid": "39162987162324445",
        "wwrtx.ltype": "1",
        "wwrtx.vid": "1688855053723800",
        "wxpay.corpid": "1970326604993422",
        "wxpay.vid": "1688855053723800",
    }
    url = (
        f"https://work.weixin.qq.com/wework_admin/loginpage_wx"
        f"?_r={random.randint(0, 999)}"
        f"&url_hash="
        f"&code={auth_data['auth_code']}"
        f"&auth_redirect_time={int(time.time() * 1000)}"
        f"&getauth_time={auth_data['getauth_time']}"
        f"&wwqrlogin=1"
        f"&qrcode_key={key_str}"
        f"&auth_source=SOURCE_FROM_WEWORK"
        f"&confirm_type=0"
    )
    res = session.get(url=url, headers=setting.headers, cookies=cookies)
    if res.status_code == 200:
        session_obj = wx_session.WXSession(key_str, session)
        session_obj.login_time = datetime.now()
        session_obj.is_login = True
        redis_conn.set(setting.constants["session_prefix"] + key_str, json.dumps(session_obj.to_dict()))
        return {"code": 200, "msg": "登录企业微信成功"}
    return None


def get_wx_cookieKey():
    url = f"https://work.weixin.qq.com/wework_admin/wwqrlogin/mng/get_key?r={str(random.random())}&login_type=login_admin&callback=wwqrloginCallback_1752733765199&redirect_uri=https%3A%2F%2Fwork.weixin.qq.com%2Fwework_admin%2Floginpage_wx%3F_r%3D845%26url_hash%3D&crossorigin=1"
    session = requests.session()
    session.headers.update(setting.headers)
    response = session.get(url, headers=setting.headers)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            key_str = data['data']['qrcode_key']
            print(f"获取到的key: {key_str}")
            session_obj = wx_session.WXSession(key_str, session)
            session_obj.is_login = False
            session_obj.login_time = datetime.now()
            redis_conn.set(setting.constants["session_prefix"] + key_str, json.dumps(session_obj.to_dict()))
            return key_str
        return None
    else:
        print(f"获取key失败，状态码: {response.status_code}")
        return None

def get_report(key_str,session):
    #random 对应 Math.random()
    random_value = random.random()
    url = f"https://work.weixin.qq.com/wework_admin/wwqrlogin/mng/check?qrcode_key={key_str}&status=QRCODE_SCAN_NEVER&r=" + str(random_value)
    response = session.get(url, headers=setting.headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取报告失败，状态码: {response.status_code}")
        return None

def get_qrcode_image_base64(key_str,session):
    url =  "https://work.weixin.qq.com/wework_admin/loginpage_wx"
    session.get(url, headers=setting.headers)
    url = f"https://work.weixin.qq.com/wework_admin/wwqrlogin/mng/qrcode?qrcode_key={key_str}&login_type=login_admin"
    response = session.get(url, headers=setting.headers)
    #响应的是png所以需要转
    if response.status_code == 200:
        #png转base64
        base64_str = base64.b64encode(response.content).decode('utf-8')
        return base64_str
    else:
        print(f"获取二维码图片失败，状态码: {response.status_code}")
        return None


def check_login_type(session: requests.Session) -> bool:
    """
    检查当前微信会话是否仍然有效。

    :param session: requests.Session 对象（含登录 cookie 和 headers）
    :return: True 表示会话有效；False 表示已失效（如超时、被踢下线）
    """
    try:
        url = (
            "https://work.weixin.qq.com/wework_admin/third/hasServiceCorp"
            f"?lang=zh_CN&ajax=1&f=json&random={random.randint(0, 999999)}"
        )
        response = session.get(url, timeout=5)

        if response.status_code != 200:
            print(f"[check_login_type] 请求失败：状态码 {response.status_code}")
            return False

        data = response.json()
        result = data.get("result", {})
        err_code = result.get("errCode")

        if err_code == -3:
            # 会话超时 / 异地登录（常见字段 etype: "otherLogin"）
            print(f"[check_login_type] 会话失效：errCode=-3，etype={result.get('etype')}")
            return False

        # 其他非 -3 错误码可视情况处理
        if err_code is not None and err_code != 0:
            print(f"[check_login_type] 非正常 errCode：{err_code}")
            return False

        # 正常情况
        return True

    except requests.exceptions.RequestException as e:
        # 网络异常等情况
        print(f"[check_login_type] 请求异常：{e}")
        return False

    except ValueError as e:
        # JSON解析错误
        print(f"[check_login_type] JSON 解析失败：{e}")
        return False

    except Exception as e:
        # 兜底
        print(f"[check_login_type] 未知异常：{e}")
        return False

