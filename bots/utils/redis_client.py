import redis
from botpy import logging

_log = logging.get_logger()
class RedisClient:
    #连 redis db1
    def __init__(self, host, port=6379, db=1, password=None, decode_responses=True):
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses
        )
        self.client = redis.Redis(connection_pool=self.pool)
        _log.info("redis已连接")

    def set(self, key, value, ex=None):
        """
        设置键值，ex为过期时间，单位秒，默认不 expire
        """
        return self.client.set(key, value, ex=ex)

    def get(self, key):
        """
        获取键值，找不到返回 None
        """
        return self.client.get(key)

    def delete(self, key):
        """
        删除指定 key，返回删除的数量
        """
        return self.client.delete(key)

    def exists(self, key):
        """
        判断 key 是否存在，返回 True/False
        """
        return self.client.exists(key) == 1


if __name__ == '__main__':
    redis_client = RedisClient(host="8.137.55.61", port=6379, db=0, password='difyai123456')
    redis_client.set("mykey", "myvalue", ex=600)
    value = redis_client.get("mykey")
    print(value)
