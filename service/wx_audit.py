import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List

import requests
from base.datacenter_mind_mysql_connector import DataCenterMindMySQLConnector
from base.ODS_ZXSWSBLJ import ODS_ZXSWSBLJ
from conf import setting
from utils.hash_utils import make_32_hash


def get_audit_list(session):
    """
    调用企业微信审批应用列表接口，获取审批应用列表信息。
    https://work.weixin.qq.com/oamng/approval_v2/getApplist?lang=zh_CN&f=json&ajax=1&timeZoneInfo%5Bzone_offset%5D=-8&random=0.24308943858924215&need_template_range=1
    :param session:
    :return :
    """
    url = "https://work.weixin.qq.com/oamng/approval_v2/getApplist"
    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": random.random(),  # 可以每次用 random.random() 动态生成
        "need_template_range": "1",
    }

    response = session.get(
        url,
        params=params,
    )
    response.raise_for_status()
    return response.json()

TZ_CHINA = timezone(timedelta(hours=8))

def _parse_date_to_ts(date_str: str, end_of_day: bool = False) -> int:
    """
    将 yyyy-mm-dd 转换为 Unix 秒（东八区），end_of_day=True 时取当天 23:59:59。
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("日期格式需为 yyyy-mm-dd")
    if end_of_day:
        dt = dt.replace(hour=23, minute=59, second=59)
    return int(dt.replace(tzinfo=TZ_CHINA).timestamp())

def get_audit_info(
    session: requests.Session,
    template_id: str,
    start_time: Optional[str] = "",
    end_time: Optional[str] = "",
    page: int = 1,
    limit: int = 20,
    sp_status: int = 0,
    sp_number: int = 0,
    creator_vid: int = 0,
    order_name: str = "apply_time",
    order_direction: int = 1,
    finish_time_begin: int = 0,
    finish_time_end: int = 0,
):
    """
    获取指定审批模板明细，时间需为 yyyy-mm-dd，默认本月第一天至今天。
    """
    url = "https://work.weixin.qq.com/oamng/approval_v2/commQueryData"

    # 时间范围（默认本月第一天 00:00:00 至今天 23:59:59）
    if start_time:
        start_ts = _parse_date_to_ts(start_time)
    else:
        today = datetime.now(TZ_CHINA).date()
        first = today.replace(day=1)
        start_ts = int(datetime(first.year, first.month, first.day, tzinfo=TZ_CHINA).timestamp())

    if end_time:
        end_ts = _parse_date_to_ts(end_time, end_of_day=True)
    else:
        now = datetime.now(TZ_CHINA).replace(hour=23, minute=59, second=59, microsecond=0)
        end_ts = int(now.timestamp())

    if start_ts > end_ts:
        raise ValueError("开始日期不能晚于结束日期")

    # 分页与查询参数
    offset = max(0, (page - 1) * limit)

    params = {
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "timeZoneInfo[zone_offset]": "-8",
        "random": random.random(),
        "template_id": template_id,
        "startTime": str(start_ts),
        "endTime": str(end_ts),
        "finish_time_begin": str(finish_time_begin),
        "finish_time_end": str(finish_time_end),
        "start": str(offset),
        "limit": str(limit),
        "sp_status": str(sp_status),
        "sp_number": str(sp_number),
        "creator_vid": str(creator_vid),
        "order_name": order_name,
        "order_direction": str(order_direction),
        "curPage": str(page),
    }

    resp = session.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_all_audit_info(
    session: requests.Session,
    template_id: str,
    start_time: Optional[str] = "",
    end_time: Optional[str] = "",
    limit: int = 20,
    **kwargs,
):
    page = 1
    all_records = []
    total = None
    while True:
        data = get_audit_info(
            session=session,
            template_id=template_id,
            start_time=start_time,

            end_time=end_time,
            page=page,
            limit=limit,
            **kwargs,
        )
        mng = data["data"].get("mngdata", [])
        if total is None:
            total = int(data["data"].get("totalcnt", 0))
        if not mng:
            break
        all_records.extend(mng)
        if len(all_records) >= total:
            break
        page += 1
    return {
        "data": {
            "totalcnt": total if total is not None else len(all_records),
            "mngdata": all_records,
        }
    }

def _now_fmt() -> str:
    return datetime.now(tz=TZ_CHINA).strftime("%Y%m%d %H%M%S")

def fetch_audit_common(
    s: requests.Session,
    template_id: str,
    biz_name: str,
    biz_code_020102: str,
    biz_code_020103: str,
    apply_time_fmt: str = "%Y%m%d %H%M%S",
    fetch_all: bool = True,
) -> List[ODS_ZXSWSBLJ]:
    if fetch_all:
        d = get_all_audit_info(s, template_id=template_id)
    else:
        d = get_audit_info(s, template_id=template_id)
    result = []
    for rec in d["data"]["mngdata"]:
        event = rec["event"]
        apply_time = datetime.fromtimestamp(event["apply_time"], tz=TZ_CHINA).strftime(apply_time_fmt)
        if "finish_time" in event:
            finish_time = datetime.fromtimestamp(int(event["finish_time"]), tz=TZ_CHINA).strftime(apply_time_fmt)
        else:
            #否则就默认2小时候完成
            finish_time = (datetime.fromtimestamp(event["apply_time"], tz=TZ_CHINA) + timedelta(hours=2)).strftime(apply_time_fmt)
        pk = make_32_hash(rec["req_name"] + apply_time + rec.get("req_org", "") + str(event.get("event_type", ""))).upper()
        obj = ODS_ZXSWSBLJ(
            ZYGCXX010101=pk,
            JCXX010101="4142012981",
            ZYGFW020101=biz_name,
            ZYGFW020102=biz_code_020102,
            ZYGFW020103=biz_code_020103,
            ZYGFW020104=apply_time,
            ZYGFW020105=rec["req_name"],
            GZFW040208=finish_time,
            ZYGCXX01018=_now_fmt(),
        )
        result.append(obj)
    result.sort(key=lambda x: x.ZYGFW020104)
    return result


def async_all_audit(s : requests.Session):
    try:
        data = get_audit_list(s)
        db_connector = DataCenterMindMySQLConnector()
        db_connector.connect()
        for l in data["data"]["list"]:
            if l["template_status"] == 0:
                continue
            os = fetch_audit_common(
                s, template_id=l["template_id"], biz_name=l["template_name"],
                biz_code_020102=setting.AuditTemplateLevel.get_level(l["template_id"]),
                biz_code_020103="1", fetch_all=True)
            for o in os:
                o.insert(db_connector)
        db_connector.close()
        return f"已成功同步审批数据，共计 {len(data['data']['list'])} 个审批模板。"
    except Exception as e:
        print(f"Fetch audit info failed: {e}")
        return None
