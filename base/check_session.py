#{'statusCode': 200, 'method': 'GET', 'result': {'errCode': -31024, 'humanMessage': '页面已过期'}}
#如果页面已经过期就返回true
import json


def check_session(data):
    """
    检查返回数据中是否包含页面已过期的标志（errCode == -31024）。
    :param data: dict 或 JSON 字符串
    :return: bool，若页面过期则返回 True，否则返回 False
    """
    if not data:
        return False

    # 如果是字符串，尝试转为字典
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return False

    # 判断页面是否过期
    try:
        err_code = data.get('result', {}).get('errCode')
        return err_code == -31024
    except Exception:
        return False
