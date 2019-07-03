# coding=utf8
import os
import random
from collections import defaultdict
import gevent
from clients.redis_client import get_config_redis_client
from loguru import logger

_used_drives = dict()

def register_drive(dimension):
    def wrapper(cls):
        _used_drives[dimension] = cls(dimension)
        return _used_drives.get(dimension)
    return wrapper


class BaseDrive(object):
    """ 驱动基类 """

    def __init__(self, dimension):
        self.dimension = dimension

    def Check(self, req_body, op_name, event, dimension, menu_type):
        return False


class Cache(object):
    def __init__(self, scan_key, refresh_interval=300):
        self.scan_key = scan_key
        self.refresh_interval = refresh_interval

        self.__client = get_config_redis_client()
        self.__menu_maps = defaultdict(set)
        self.__in_django = "DJANGO_SETTINGS_MODULE" in os.environ
        menu_maps = self.__build_menu_maps()
        for k in menu_maps:
            self.__menu_maps[k] = menu_maps[k]
        if not self.__in_django:
            gevent.spawn(self.__refresh_menu_maps)

    def __build_menu_maps(self):
        tmp_maps = defaultdict(set)
        for key in self.__client.scan_iter(match=self.scan_key):
            key_set = self.__get_key_from_redis(key)
            if key_set:
                tmp_maps[key] = key_set
        return tmp_maps

    def __get_key_from_redis(self, key):
        key_set = set()
        for item in self.__client.sscan_iter(key):
            key_set.add(item)
        return key_set

    def __getitem__(self, item):
        if self.__in_django:
            return self.__get_key_from_redis(item)
        else:
            return self.__menu_maps.get(item, set())

    def __refresh_menu_maps(self):
        while True:
            gevent.sleep(self.refresh_interval + random.randint(1, 60))
            logger.info('start refresh {} cache', self.scan_key)
            try:
                tmp_maps = self.__build_menu_maps()
                if tmp_maps:
                    self.__menu_maps = tmp_maps
            except Exception as e:
                logger.error('refresh {} cache failed', self.scan_key,
                             exc_info=e)
            else:
                logger.info('refresh {} cache success', self.scan_key)


@register_drive("*")
class DefaultDrive(BaseDrive):
    """ 默认驱动 """

    menu_cache = Cache(scan_key="menu:*")

    @staticmethod
    def build_redis_key(self, event, menu_type, dimension):
        fields = ['menu', event, menu_type, dimension]
        if all(fields):
            return ':'.join(fields)
        else:
            return ''

    def Check(self, req_body, op_name, event, dimension, menu_type):

        redis_key = self.build_redis_key(event, menu_type, dimension)
        logger.info("default drive key:{}".format(redis_key))

        if not redis_key:
            return False

        rv = req_body[dimension] in self.menu_cache[redis_key]
        if op_name == 'is_not':
            rv = not rv

        return rv

