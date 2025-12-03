import datetime
import json
from functools import wraps
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from base.redis_connector import redis_conn
from conf import setting
from service import get_wx_cookie
from service.response_obj import ResetResponse
from base.wx_session import WXSession, LoginStatus

app = Flask(__name__)

# 配置
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)

MAX_SESSION_LIFETIME = 2 * 3600       # 最大存活时间 2 小时
SESSION_CHECK_INTERVAL = 3600         # 登录时间超过 1 小时才检查
SESSION_CHECK_RATE_LIMIT = 2 * 60    # 每个会话至少间隔2分钟检查一次
MAX_SCANNER_LIFETIME = 10 * 60               # 扫码中状态最大存活时间 10 分钟
@scheduler.task('interval', id='job1', seconds=10)
def job1():
    keys = redis_conn.keys(setting.constants["session_prefix"] + "*")
    if not keys:
        return

    now = datetime.datetime.now()

    for key in keys:
        session_data = redis_conn.get(key)
        if not session_data:
            continue

        # 转成 WXSession 对象
        session = WXSession.from_dict(session_data)

        login_time = session.login_time
        last_check = session.last_check_time or datetime.datetime.min
        #如果是扫码中的状态就跳过并且 时间已经 超过了
        if session.login_status == LoginStatus.SCANNING_QR and not  (now - login_time).total_seconds() > MAX_SCANNER_LIFETIME:
            continue
        # 无登录时间，直接清理
        if not login_time:
            print(f"会话 {session.session_id} 无登录时间，删除")
            redis_conn.delete(key)
            continue

        time_since_last_check = (now - last_check).total_seconds()

        # 限频：每个会话至少间隔 SESSION_CHECK_RATE_LIMIT 秒才检查一次
        if time_since_last_check <= SESSION_CHECK_RATE_LIMIT:
            continue

        # 执行心跳检查
        is_valid = get_wx_cookie.check_login_type(session.create_session())
        session.last_check_time = now

        if not is_valid:
            print(f"会话 {session.session_id} 已失效，删除")
            redis_conn.delete(key)
            continue

        # 保持活性：检查通过则刷新 login_time（模拟活跃）
        session.login_time = now
        redis_conn.set(key, json.dumps(session.to_dict()))
        print(f"会话 {session.session_id} 心跳成功，已保活")



scheduler.start()


def with_session(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        key_str = request.args.get("key_str") or request.form.get("key_str")
        if not key_str:
            return jsonify(ResetResponse.fail("Missing key_str parameter").to_dict()), 400

        json_data = redis_conn.get(setting.constants["session_prefix"] + key_str)
        if not json_data:
            return jsonify(ResetResponse.fail("Session not found").to_dict()), 404

        try:
            wx_obj = WXSession.from_dict(json_data)
            session = wx_obj.create_session()
            #如果是调用接口地址前缀包含/login就不检查登录状态
            if request.endpoint and request.endpoint.startswith("login"):
                is_valid = True
            else:
                is_valid = get_wx_cookie.check_login_type(session)
            if not is_valid:
                #清除无效的会话
                redis_conn.delete(setting.constants["session_prefix"] + key_str)
                return jsonify(ResetResponse.fail("Session is invalid or expired").to_dict()), 403
        except Exception:
            return jsonify(ResetResponse.fail("Session parse error").to_dict()), 500

        # 根据 content-type 判断是否要解析 JSON
        content_type = request.content_type or ""

        if request.method in ["POST", "PUT", "PATCH"]:
            if "application/json" in content_type:
                try:
                    data = request.get_json(force=True)
                except Exception:
                    return jsonify(ResetResponse.fail("Invalid JSON body").to_dict()), 400
                return view_func(key_str, session, data, *args, **kwargs)

            else:
                # 非 JSON 请求，如 form-data、x-www-form-urlencoded 或 multipart
                return view_func(key_str, session, None, *args, **kwargs)
        else:
            return view_func(key_str, session, *args, **kwargs)

    return wrapper

@app.route("/", methods=["GET", "POST"])
def index():
    return f"企业微信代理API,当前版本: {setting.constants['version']}。"