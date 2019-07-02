# coding=utf8
from base import register_drive, BaseDrive

@register_drive("pay")
class PayDrive(BaseDrive):
    """ 支付账号名单驱动 """

    def Check(self, req_body, op_name, event, dimension, menu_type):
        return False