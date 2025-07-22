import datetime
import requests

class WXSession:
    def __init__(self, session_id, session=None):
        self.session_id = session_id
        self.is_login = False
        self.login_time = None
        self.last_check_time = None  # 新增：上次检查时间

        # 如果传入了 requests.Session，则取出 cookies 和 headers
        if session:
            self.cookies = session.cookies.get_dict()
            self.headers = dict(session.headers)
        else:
            self.cookies = {}
            self.headers = {}

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "is_login": self.is_login,
            "login_time": self.login_time.isoformat() if self.login_time else None,
            # 新增last_check_time序列化，使用iso格式
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "cookies": self.cookies,
            "headers": self.headers
        }

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(session_id=data["session_id"])
        obj.is_login = data.get("is_login", False)

        login_time_str = data.get("login_time")
        if login_time_str:
            obj.login_time = datetime.datetime.fromisoformat(login_time_str)

        last_check_str = data.get("last_check_time")
        if last_check_str:
            obj.last_check_time = datetime.datetime.fromisoformat(last_check_str)

        obj.cookies = data.get("cookies", {})
        obj.headers = data.get("headers", {})
        return obj

    def create_session(self):
        """从保存的 cookies 和 headers 创建一个新的 requests.Session"""
        s = requests.Session()
        s.headers.update(self.headers)
        s.cookies.update(self.cookies)
        return s