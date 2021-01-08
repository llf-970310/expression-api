#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 20-3-08

import datetime
import logging
import math
import time
import uuid
from functools import wraps

from app_config import redis_client


def mutex_with_redis(lock_time):
    def inner_deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = 'aps_lock:%s:%s' % (func.__module__, func.__name__)
            val = str(datetime.datetime.utcnow())
            if redis_client.set(key, val, ex=lock_time, nx=True):
                func(*args, **kwargs)
            else:
                logging.warning("redis lock. func: " + func.__name__)

        return wrapper

    return inner_deco


def acquire_lock(lock_name: str, acquire_timeout: int = 3, expire_time: int = 2):
    """
    基于 Redis 实现的分布式锁

    :param lock_name: 锁的名称
    :param acquire_timeout: 获取锁的超时时间，超过这个时间则放弃获取锁，默认3秒
    :param expire_time: 锁的过期时间，默认2秒
    :return: 锁的标识，解锁时使用
    """

    # 生成 uuid 作为 redis value，保证唯一性
    lock_value = str(uuid.uuid1())
    # redis key
    key = "distributed_lock:" + lock_name
    # 过期时间处理，防止异常数据
    expire_time = int(math.ceil(expire_time))
    # 循环获取锁，超时时间为 acquire_timeout
    end = time.time() + acquire_timeout
    while time.time() < end:
        # 如果锁不存在，则加锁并设置过期时间
        # setnx ex 原子性加锁
        if redis_client.set(key, lock_value, ex=expire_time, nx=True):
            return lock_value
        time.sleep(0.1)
    # 超时，获取失败
    return None


def release_lock(lock_name: str, lock_value: str):
    """
    释放锁

    :param lock_name: 锁的名称
    :param lock_value: 锁的标识
    :return: 是否解锁成功 (bool)
    """

    lua_script = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end
    """
    # redis key
    key = "distributed_lock:" + lock_name
    # lua 脚本，原子性解锁
    unlock = redis_client.register_script(lua_script)
    result = unlock(keys=[key], args=[lock_value])
    if result:
        return True
    else:
        return False


if __name__ == "__main__":
    lock_value = acquire_lock("test", expire_time=300)
    if lock_value:
        print("lock successful!")
        result = release_lock("test", lock_value)
        if result:
            print("unlock successful")
        else:
            print("unlock failed!")
    else:
        print("lock failed!")
