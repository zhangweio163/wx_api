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
}
cookies = {}
redis_params = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": None,
    "connect_timeout": 5,  # 连接超时
}


