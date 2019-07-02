# coding=utf8
from base import register_drive, BaseDrive

@register_drive("phone")
class PhoneDrive(BaseDrive):
    """ 手机号名单驱动 """

    def Check(self, req_body, op_name, event, dimension, menu_type):
        pass