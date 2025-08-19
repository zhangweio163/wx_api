import logging

import redis
import json
import sys
from conf.setting import redis_params
class RedisConnector:
    def __init__(self, host='localhost', port=6379, db=0, password=None, connect_timeout=5):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.connect_timeout = connect_timeout

        try:
            self.pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                socket_connect_timeout=self.connect_timeout,  # ⏱️ 连接超时
                socket_timeout=self.connect_timeout           # ⏱️ 操作超时（可选）
            )
            logging.warning(f"redis连接信息:{self.host}:{self.port}/{self.db}-连接超时:{self.connect_timeout}秒")
            logging.warning("开始连接 Redis...")
            self.redis = redis.Redis(connection_pool=self.pool)

            # 🚨 关键：初始化时主动测试连接
            self.redis.ping()

        except Exception as e:
            logging.error(f"Cannot connect to Redis at {self.host}:{self.port}/{self.db} - {e}")
            sys.exit(1)  # 直接退出程序

    def set(self, key, value):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.redis.set(key, value)

    def get(self, key):
        val = self.redis.get(key)
        if val is not None:
            try:
                return json.loads(val)
            except:
                return val.decode('utf-8')
        return None

    def delete(self, key):
        self.redis.delete(key)

    def keys(self, pattern='*'):
        return self.redis.keys(pattern)

    def close(self):
        self.pool.disconnect()


# 单例使用
redis_conn = RedisConnector(**redis_params)  # 3秒连不上就直接报错