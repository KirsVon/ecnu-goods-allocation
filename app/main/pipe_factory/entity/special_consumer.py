# -*- coding: utf-8 -*-
# Description: 指定司机的客户
# Created: jjunf 2021/4/29 11:10
from app.util.base.base_entity import BaseEntity


class SpecialConsumer(BaseEntity):

    def __init__(self, special_consumer=None):
        """
        指定司机的客户类
        :param special_consumer:
        """
        # 司机池id
        self.driver_pool_id = None
        # 司机池名称
        self.driver_pool_name = None
        # 客户id
        self.consumer_id = None
        # 公司id
        self.company_id = None
        # 司机id
        self.driver_id = None
        # 司机姓名
        self.driver_name = None
        # 司机电话
        self.driver_mobile = None
        # 司机车牌
        self.vehicle_no = None
        # 司机参考运量
        self.reference_load = None

        if special_consumer:
            self.set_attr(special_consumer)
