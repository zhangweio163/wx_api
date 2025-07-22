import random


def get_org(session):
    """
    调用企业微信 getOrg 接口，获取企业组织信息。

    参数：
        session: 已登录的 requests.Session 对象，包含有效 Cookie 等。

    返回：
        response: requests.Response 对象，可根据 response.json() 获取返回内容。
    """
    url = "https://work.weixin.qq.com/wework_admin/contacts/party/cache"
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": random.random()  # 可以每次用 random.random() 动态生成
    }

    response = session.post(
        url,
        params=params,
    )
    return response.json()


def get_org_user(session):
    """
    调用企业微信 getOrgUser 接口，获取企业组织用户信息。

    参数：
        session: 已登录的 requests.Session 对象，包含有效 Cookie 等。

    返回：
        response: requests.Response 对象，可根据 response.json() 获取返回内容。
    """
    url = "https://work.weixin.qq.com/wework_admin/contacts/member/cache"
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": random.random()  # 可以每次用 random.random() 动态生成
    }

    response = session.post(
        url,
        params=params,
    )
    return response.json()
