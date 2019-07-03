# coding=utf-8

from loguru import logger

from risk_models.drives.base import _used_drives


def build_redis_key(event_code, dimension, menu_type):
    """
    :param event_code: 名单code
    :param dimension:  名单维度
    :param menu_type:  名单类型 黑/白/灰
    :return:
    """
    fields = ['menu', event_code, dimension, menu_type]
    if all(fields):
        return ':'.join(fields)
    else:
        return ''


def hit_menu(req_body, op_name, event, dimension, menu_type):
    if dimension not in req_body:
        logger.error('req_body(%s) does not contain %s', req_body, dimension)
        return False

    logger.info("{},{},{},{},{}".format(op_name, event, dimension, menu_type,req_body))

    #自定义驱动
    if _used_drives.has_key(dimension):
        logger.info("used custom drive:{}".format(dimension))
        rv = _used_drives.get(dimension).Check(req_body, op_name, event, dimension, menu_type)
        if rv:
            return rv

    #默认驱动
    if _used_drives.has_key('*'):
        logger.info("used default drive:{}".format('*'))
        rv = _used_drives.get('*').Check(req_body, op_name, event, dimension, menu_type)
        return rv

    return False


