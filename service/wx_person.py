import os
import random
from base.person import Person
import requests
from flask import session
import pandas as pd
import uuid

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


def get_org_user(session,page = 0):
    """
    调用企业微信 getOrgUser 接口，获取企业组织用户信息。
    GET /wework_admin/contacts/getDepartmentMember?lang=zh_CN&f=json&ajax=1&timeZoneInfo%5Bzone_offset%5D=-8&random=0.7722565285168298&action=getpartycontacts&partyid=1688856978646799&page=0&limit=20&joinstatus=0&fetchchild=1&preFetch=true&use_corp_cache=0

    参数：
        session: 已登录的 requests.Session 对象，包含有效 Cookie 等。

    返回：
        response: requests.Response 对象，可根据 response.json() 获取返回内容。
    """
    url = "https://work.weixin.qq.com/wework_admin/contacts/getDepartmentMember"
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": random.random(),  # 可以每次用 random.random() 动态生成
        "page": page,
        "limit": "20",
        "fetchchild": "1",
        "preFetch": "true",
        "use_corp_cache": "0"
    }

    response = session.get(
        url,
        params=params,
    )
    return response.json()

def get_all_org_user(session):
    """
    获取所有企业微信用户信息，处理分页逻辑。
    page_count 是从第一次获取用户信息时返回的总页数 。{'data': {'member_count': 23, 'page_count': 2, 。。。
    :param session:
    :return:
    """
    page = 0
    all_users = []
    first_response = get_org_user(session, page)
    all_users.extend(first_response.get("data").get("contact_list").get("list"))
    page_count = first_response.get("data").get("page_count")
    for page in range(1, page_count):
        response = get_org_user(session, page)
        all_users.extend(response.get("data").get("contact_list").get("list"))
    return all_users

def export_excel_person(session):

    # 准备数据
    user_info = get_all_org_user(session)
    orgs = get_org(session).get("data", {}).get("party_list", {}).get("list", [])
    org_map = {org.get("partyid"): org for org in orgs if org}

    excel_data = []
    for person in user_info or []:
        depart_ids = person.get("depart_ids") or []
        department_name = ""
        if depart_ids:
            path = []
            cur = org_map.get(depart_ids[0])
            seen = set()
            while cur and cur.get("partyid") not in seen:
                seen.add(cur.get("partyid"))
                path.append(cur.get("name") or "")
                pid = cur.get("parentid")
                if not pid or pid == 0:
                    break
                cur = org_map.get(pid)
            department_name = "/".join(reversed([p for p in path if p])) or ""

        p = Person(
            person.get("name"),
            person.get("acctid"),
            alias=person.get("alias"),
            position=person.get("position") or "",
            department=department_name,
            gender=("男" if person.get("gender") == 1 else "女" if person.get("gender") == 2 else "男"),
            mobile=person.get("mobile"),
            telephone=person.get("ext_tel"),
            email=person.get("email"),
            address=person.get("address"),
            extid=person.get("extid"),
            videonum=person.get("videonum"),
            status=("已激活" if person.get("bind_stat") == 1 else "未激活"),
            disable=("已禁用" if person.get("disable_stat") == 1 else "未禁用"),
            wechat_plugin=("未关注" if (person.get("wechat") or "") == "" else "已关注"),
        )
        excel_data.append(p)
    return make_excel_for_persons(excel_data)


def make_excel_for_persons(excel_data):
    id = uuid.uuid4().hex
    df_data = {
        "姓名": [p.name for p in excel_data],
        "账号": [p.userid for p in excel_data],
        "别名": [p.alias for p in excel_data],
        "职务": [p.position for p in excel_data],
        "部门": [p.department for p in excel_data],
        "性别": [p.gender for p in excel_data],
        "手机": [p.mobile for p in excel_data],
        "座机": [p.telephone for p in excel_data],
        "邮箱": [p.email for p in excel_data],
        "地址": [p.address for p in excel_data],
        "企业邮箱": [p.extid for p in excel_data],
        "视频号": [p.videonum for p in excel_data],
        "激活状态": [p.status for p in excel_data],
        "禁用状态": [p.disable for p in excel_data],
        "微信插件": [p.wechat_plugin for p in excel_data],
    }
    df = pd.DataFrame(df_data)

    notices = [
        "填写须知：",
        "1、不能在该Excel表中对成员信息类别进行增加、删除或修改；",
        "2、红色字段为必填，黑色为选填（手机和邮箱需选其一），字段值里不要填入“，”字符；仅填邮箱或国际手机号+邮箱会发送邀请邮件；",
        "3、账号：成员唯一标识，由1-64个字母、数字、点(.)、减号(-)或下划线(_)组成；账号相同会覆盖导入；支持修改一次，示例：old_userid:new_userid；",
        "4、部门：上下级用‘/’隔开，从最上级开始；多部门用‘；’隔开，首个为主部门；部门≤32字符，英文名≤64字符；",
        "5、支持国内、国际手机号（国际需包含+国家码，示例：+85259****24）；",
        "6、网页类型：网页名称与地址用‘；’隔开，地址以http://或https://开头，示例：企业微信；http://work.weixin.qq.com；",
        "7、企业邮箱：邮箱名1-32个字母、数字、点(.)、减号(-)、下划线(_)；后缀必须为当前企业域名；",
        "8、视频号：填写视频号名字，且已绑定到企业微信；",
    ]

    with pd.ExcelWriter(f"企业微信人员信息表导出_{id}.xlsx", engine="xlsxwriter") as writer:
        sheet = "成员列表"
        # 表头在第10行（0基索引9），数据从第11行开始
        df.to_excel(writer, index=False, sheet_name=sheet, startrow=9)
        workbook = writer.book
        worksheet = writer.sheets[sheet]

        # 写入填写须知（第1-9行），整行合并
        notice_fmt = workbook.add_format({"valign": "vcenter", "align": "left", "text_wrap": True})
        total_cols = len(df.columns)
        for i, line in enumerate(notices):
            worksheet.merge_range(i, 0, i, total_cols - 1, line, notice_fmt)

        # 表头样式（第10行）
        header_fmt = workbook.add_format({
            "bold": True, "text_wrap": True, "valign": "center", "align": "center", "border": 1
        })
        for col_idx, col_name in enumerate(df.columns):
            worksheet.write(9, col_idx, col_name, header_fmt)

        # 自动列宽
        for col_idx, col_name in enumerate(df.columns):
            col_values = df[col_name].astype(str)
            max_len = max(col_values.map(len).max() if not df.empty else 0, len(col_name)) + 2
            worksheet.set_column(col_idx, col_idx, max_len)

        # 为“有数据的行”的整行加边框（不影响数据范围之外的空白）
        n_rows = len(df)
        n_cols = len(df.columns)
        if n_rows > 0 and n_cols > 0:
            data_border_fmt = workbook.add_format({"valign": "center", "align": "center", "border": 1})
            start_data_row = 10  # 第11行（人类计数）
            end_data_row = start_data_row + n_rows - 1
            # 使用固定真公式，覆盖数据矩形区域所有单元格（含空值）
            worksheet.conditional_format(
                start_data_row, 0, end_data_row, n_cols - 1,
                {"type": "formula", "criteria": "TRUE", "format": data_border_fmt}
            )
    #返回绝对路径
    file_path = os.path.abspath(f"企业微信人员信息表导出_{id}.xlsx")
    return file_path