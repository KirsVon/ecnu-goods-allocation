# -*- coding: utf-8 -*-
# Description: 
# Created: jjunf 2021/3/18 10:28
from app.util.base.base_entity import BaseEntity


class RemainCheck(BaseEntity):
    """
    摘单时判断剩余车次数类
    """

    def __init__(self, check=None):
        # 司机id
        self.driver_id = None
        # 摘单号
        self.pickup_no = None
        # 分配总重量
        self.total_weight = None
        # 总车次
        self.total_truck_num = None
        # 剩余车次
        self.remain_truck_num = None
        # 城市
        self.city = None
        # 区县
        self.district = None
        # 品种
        self.big_commodity_name = None
        # 每车的件数
        self.plan_quantity = None
        # 摘单备注
        self.remark = None
        # 返回的结果，默认False
        self.result = False

        if check:
            self.set_attr(check)
