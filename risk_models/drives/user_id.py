# coding=utf8
from base import register_drive, BaseDrive
from loguru import logger

@register_drive("user_id")
class UseridDrive(BaseDrive):
    """ 用户ID名单驱动 """

    def Check(self, req_body, op_name, event, dimension, menu_type):
        return False