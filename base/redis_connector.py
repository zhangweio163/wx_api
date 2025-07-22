import redis
import json

class RedisConnector:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password
        )
        self.redis = redis.Redis(connection_pool=self.pool)

    def set(self, key, value):
        try:
            # 自动将dict或list转为json字符串
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self.redis.set(key, value)
        except Exception as e:
            print(f"Set key error: {e}")

    def get(self, key):
        try:
            val = self.redis.get(key)
            if val is not None:
                try:
                    return json.loads(val)
                except:
                    return val.decode('utf-8')
            return None
        except Exception as e:
            print(f"Get key error: {e}")
            return None

    def delete(self, key):
        try:
            self.redis.delete(key)
        except Exception as e:
            print(f"Delete key error: {e}")

    def keys(self,pattern='*'):
        try:
            return self.redis.keys(pattern)
        except Exception as e:
            print(f"Keys error: {e}")
            return []

    def close(self):
        self.pool.disconnect()

# 单例使用
redis_conn = RedisConnector()