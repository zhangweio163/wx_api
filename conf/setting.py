version = '1.0.0'
debug = False

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:140.0) Gecko/20100101 Firefox/140.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://work.weixin.qq.com',
    'Referer': 'https://work.weixin.qq.com/wework_admin/frame',
    'Connection': 'keep-alive',
}
constants = {
    "session_prefix" : 'wx_session:',
	"version" : version,
    "corpid":"1970326604993422",
}
cookies = {}
redis_params = {
    "host": "172.16.9.145",
    "port": 6379,
    "db": 4,
    "password": "xxzx2019&2901",
    "connect_timeout": 5,  # 连接超时
}


datacenter_connect_params = {
    "host": "172.16.9.145",
    "port": 3306,
    "user": "data_center",
    "password": "DataCenter2020&2901",
    "database": "datacenter_mind",
    "connect_timeout": 5,  # 连接超时
}


dev_cookies =  {
		"_qimei_fingerprint": "436cef11cc131522e26fa276d7b29a32",
		"_qimei_h38": "b8851de211a7e0af811c266903000000419208",
		"_qimei_q36": "",
		"omgid": "0_y3cB4Hbibxk0n",
		"pac_uid": "0_GGc6871YF7132",
		"ptcz": "8565ca6fc09f207978e510b8cbf9abfc5fb51dde89d20c92239d29f086d9c9b5",
		"RK": "FBV5amd7SO",
		"ww_lang": "cn,zh",
		"wwopen.open.sid": "wbjSeOBtt1_HoIiy1WRZarTnXoIlRzUAViyAwoi_qR77w467X7D_v5oluX12ZwHdnvy9fa-2owpKb8XdjxXroVg",
		"wwrtx.c_gdpr": "0",
		"wwrtx.cs_ind": "",
		"wwrtx.i18n_lan": "zh",
		"wwrtx.logined": "true",
		"wwrtx.ltype": "1",
		"wwrtx.ref": "direct",
		"wwrtx.refid": "39666303641092912",
		"wwrtx.sid": "wPExF_15q4sxo7H-U2fi8Uqt97BmKqQbCD8e-ngeC9hN7u3NnzphDCa6tLfi-ZP3cvmlinJ4-xG-4oj6hzKBKA",
		"wwrtx.vid": "1688851270958669",
		"wwrtx.vst": "wepS426Ic3ocswj6IVaAXTzKXROfQMQ7esLm_dH8lwthq7Bir_QE8W4sdB5VVWCTnx93BUq9tmK4Dpp7tIZxg-Mqnfx2YK6PvKVDww67BxrFOobwzQ1_yVK_BP5h4iyKLInr8hnPv3kMiXlZTww0o_Y_ncCX09fwnz9QfcgSGk4D430070sCSh7oLLFmD-cuIFyyJF7OTUytWSSoOBdPq3myjtE8qrm4Sqz8kNMTsKVSNrE1keqoZs28ULDMQoDQx35ekKs5GGegzJ7lYKmJXfC6azrX2LqFSgZccr-JvrY",
		"wwrtx.vst2": "AQAAtRD4-di4EXGqHqgBqopf0h3GG9jaaPfyreP5NObvS_a9aZwQ797Ef2RzPqzHnPyKvOwP-1331TZuLp0elMnfVnmXyeWWsrqVqtTOXJBegnDUmD3aW-iBLPvtBXEWe2hdjdrKbXmSAgHnLXWuLhmPJMOKq9qWK5t8cSMyc9d3vuj3Gguni3Tt9CrccxDkf7rf_ZP4Je1PCv9oizltXa2RtDc_c78xtkDbxVXWIkX4zroQVFsKvF7qUPSJ-9bHVqL20LQmZ0tgD0ddlCbT0o01Hg",
		"wxpay.corpid": "1970325082047884",
		"wxpay.vid": "1688851270958669"
	}


# python
from types import MappingProxyType
from typing import Optional


class AuditTemplateLevel:
    """
    模板 ID -> 等级 的只读常量映射。
    使用示例：
        level = AuditTemplateLevel.get_level(template_id)  # 返回 4/5 或 None
        level = AuditTemplateLevel.get_level(template_id, default=0)  # 未知 ID 返回 0
    """
    _LEVELS = {
        "C4NyGNa3sPo5kH8q7HJt6fYQAEe46UbP2dMzfkBma": "5",
        "C4RbxevTkYthYn648ypX8gbjeFboXepksMyxvafPD": "5",
        "3WK7zGKUJZ8NFEasotTvGrQxHxPkrhz9G9Rvhop7": "5",
        "C4NyGEaVhwkKdWHiVu8fuyS7UkLtHfPJ5nfuCxuTw": "5",
        "C4UCJJFisgdGLy2G5DCu4y7LzGV1AHcct5TFtBaod": "4",
        "3WLJ77G1gzHbsam1mtWXmZ2PFEzwy3z7sqFwtRHR": "4",
        "C4WroTtyLzNwUSRgrPGXp2P5Wm3PX2NeN8wNrbPov": "4",
        "3WLuFVDsp5vLaZWbFjdRp8qJ2nB3nXx8nR3PmoWg": "9",
        "C4c6SftbAA1aPaDcU9dDen4HQxGKQhMsKZbsMhsgM": "9",
        "C4c6SftbxHXrnR5Qki2HDMXCFZzWo3WN9KYJ5JrJt": "9",
        "C4c6SwYBzeDyfi8quVERv1r2dJSL1Ca2ErnZ3frRF": "9",
        "C4c6SwbjcY4rRC7cb251yy3N9xcCm6V8UKKkS1EZr": "9",
        "C4WqcwY4fjERRjkGJ4urDuJ3AxZV3GP2SMXHdofqE": "4",
        "C4WrD8rjTmPUEpZVvizReNXnJqipDErhC6RrkbfSG": "9",
        "C4WqcY9CZgETscsC7bPF3k4FKkoK5fqUu1aFhBFvg": "9",
        "3WLtynAFaZ7SmgzUTN1w6DKU7ZFEdBJ6aSmJSWJH": "9",
        "ZvmJ9ATu1nVvG8AM2DpoX1F9B5ozYaDsCWYwaR": "9",
        "C4WrDg6GHDhQGB81QcTioN61cMBL1NtZk9w3jxYyt": "9",
    }
    LEVELS = MappingProxyType(_LEVELS)

    @classmethod
    def get_level(cls, template_id: str, default: Optional[int] = None) -> Optional[str]:
        return cls.LEVELS.get(template_id, default)