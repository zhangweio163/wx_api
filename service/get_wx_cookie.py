import base64
import json
import random
import re
import time
import uuid
from datetime import datetime

from base import wx_session
import requests
from base.redis_connector import redis_conn
from base.wx_session import LoginStatus
from conf import setting

# python
import re
import json

def parse_mobile_confirm_page(html: str):
    """
    解析页面中的 window.settings JSON，返回 tl_key、mobile 与 is_capcaptcha。
    """
    # 更稳健的正则：提取花括号内部 JSON，避免跨到 </script>
    m = re.search(r'window\.settings\s*=\s*(\{[^<]+?\})\s*;?', html, re.DOTALL)
    if not m:
        # 调试输出，便于定位问题
        # 可选：打印前后 200 字符的上下文
        return None

    settings_raw = m.group(1)
    try:
        settings = json.loads(settings_raw)
    except json.JSONDecodeError:
        return None

    tl_key = settings.get('tl_key')
    mobile = settings.get('mobile')
    if not tl_key:
        return None

    return {
        "tl_key": tl_key,
        "mobile": mobile,
        "is_capcaptcha": bool(mobile)
    }


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
        "wxpay.corpid": setting.constants["corpid"],
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
        html = res.text
        info = parse_mobile_confirm_page(html)
        if not info:
            return {"code": 500, "msg": "登录失败，二维码失效"}
        session_obj = wx_session.WXSession(key_str, session)
        session_obj.login_time = datetime.now()
        session_obj.is_login = True
        session_obj.login_status = LoginStatus.LOGGED_IN
        redis_conn.set(setting.constants["session_prefix"] + key_str, json.dumps(session_obj.to_dict()))
        return {"code": 200, "msg": "登录企业微信成功","capcaptcha":info}
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
            session_obj = wx_session.WXSession(key_str, session,LoginStatus.SCANNING_QR)
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


def generate_viewkey(local_counter=None, popstate_count=0):
    """
    模拟 JS 中的生成逻辑:
    o = "{Date.now() % 1e5}-{(1e5*Math.random())|0}-{localCounter%1000}"
    最终返回: o + "-" + i  (i = popstate/hash change 计数，通常为 0)
    local_counter:
      - 如果你能从浏览器 localStorage 里读到 "__viewkey__" 的数值，传入该数值（int）。
      - 否则传 None，函数会随机一个初始值（0..99999），效果通常能通过格式校验。
    popstate_count:
      - 通常为 0（你没有浏览器事件），但 JS 会在 hash/popstate 时自增。
    """
    # JS: a = +(localStorage.getItem("__viewkey__") || 0) + 1
    if local_counter is None:
        a = random.randint(0, 99999)  # 任意初始计数，JS 使用 localStorage 的累计计数
    else:
        try:
            a = int(local_counter) + 1
        except:
            a = int(local_counter or 0) + 1
    part1 = int((int(time.time() * 1000) % 100000))    # Date.now() % 1e5
    part2 = (int(100000 * random.random()) | 0)        # (1e5*Math.random())|0
    part3 = a % 1000                                  # a % 1e3
    o = f"{part1}-{part2}-{part3}"
    viewkey = f"{o}-{int(popstate_count)}"
    return viewkey

def confirm_captcha(session: requests.Session, captcha: str, tl_key: str,
                    local_counter=None, popstate_count=0):
    """
    session: 同 get_key 使用的 session（确保 cookie/headers 一致）
    captcha: 用户输入的验证码
    tl_key: 从 get_key 接口得到的 qrcode_key（仍然放在 json body）
    local_counter: 可选，从真实浏览器 localStorage "__viewkey__" 读到的数值（若可得）
    popstate_count: 可选事件计数（通常 0）
    """
    viewkey = generate_viewkey(local_counter=local_counter, popstate_count=popstate_count)

    url = "https://work.weixin.qq.com/wework_admin/mobile_confirm/confirm_captcha"
    params = {
        "ajax": "1",
        "f": "json",
        "d2st": "",
        "_viewkey": viewkey,  # <- 这里是关键：不要把 tl_key 当作 viewkey
        "_r": str(int(time.time() * 1000)) + "_57",
        "_cmtid": "0a01e867"
    }
    payload = {
        "captcha": captcha,
        "tl_key": tl_key
    }

    # 发请求前，建议打印/记录用于调试的内容：
    print("confirm_captcha -> viewkey:", viewkey, "tl_key:", tl_key)
    print("cookies:", session.cookies.get_dict())

    headers = session.headers
    headers.update({
        "Content-Type": "application/json",  # 必须
        "Referer": (
            "https://work.weixin.qq.com/wework_admin/mobile_confirm/"
            f"captcha_page?tl_key={tl_key}&redirect_url="
        ),
    })

    response = session.post(url, params=params, json=payload, headers=headers)
    print(response.text)
    print(response.request.__dict__)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"确认验证码失败，状态码: {response.status_code}")
        return None

def after_captcha_success(session,tl_key):
    """
    Referer: https://work.weixin.qq.com/wework_admin/mobile_confirm/captcha_page?tl_key=a5c35bc3514894c79fbeaf9452b0a253&redirect_url=https%3A%2F%2Fwork.weixin.qq.com%2Fwework_admin%2Flogin%2Fchoose_corp%3Ftl_key%3Da5c35bc3514894c79fbeaf9452b0a253
    GET /wework_admin/login/choose_corp?tl_key=a5c35bc3514894c79fbeaf9452b0a253
    :param tl_key:
    :param session:
    :return:
    """
    url = f"https://work.weixin.qq.com/wework_admin/login/choose_corp?tl_key={tl_key}"
    headers = setting.headers
    headers.update({
        "Referer": f"https://work.weixin.qq.com/wework_admin/mobile_confirm/captcha_page?tl_key={tl_key}&redirect_url=https%3A%2F%2Fwork.weixin.qq.com%2Fwework_admin%2Flogin%2Fchoose_corp%3Ftl_key%3D{tl_key}"
    })
    response = session.get(url, headers=setting.headers)
    if response.status_code == 200:
        '''
        /wework_admin/frame
        '''
        url = "https://work.weixin.qq.com/wework_admin/frame"
        headers.update({
            "Referer": f"https://work.weixin.qq.com/wework_admin/login/choose_corp?tl_key={tl_key}"
        })
        response = session.get(url, headers=setting.headers)
        response.raise_for_status()
        html = response.text
        return html
    else:
        print(f"选择企业失败，状态码: {response.status_code}")
        return None

def make_wx_session_by_cookie(cookie_dict):
    session = requests.Session()
    cookies = requests.cookies.cookiejar_from_dict(cookie_dict)
    session.cookies = cookies
    session.headers.update(setting.headers)
    key_str = uuid.uuid1().hex
    session_obj = wx_session.WXSession(key_str, session)
    #测试cookie是否有效
    if check_login_type(session):
        session_obj.is_login = True
        session_obj.login_time = datetime.now()
        session_obj.login_status = LoginStatus.LOGGED_IN
        redis_conn.set(setting.constants["session_prefix"] + key_str, json.dumps(session_obj.to_dict()))
        return key_str
    else:
        return None