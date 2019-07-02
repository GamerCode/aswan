# coding=utf8
from base import register_drive, BaseDrive

@register_drive("ip")
class IPDrive(BaseDrive):
    """ IP名单驱动 """

    def Check(self, req_body, op_name, event, dimension, menu_type):
        pass