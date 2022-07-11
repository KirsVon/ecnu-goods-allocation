# -*- coding: utf-8 -*-
# Description:  各城市车辆历史载重
# Created: jjunf 2021/5/10 11:06
from app.util.base.base_entity import BaseEntity


class CityTruckLoadWeight(BaseEntity):
    """
    各城市车辆历史载重类
    """

    def __init__(self, city_truck_load_weight=None):
        # 公司id
        self.company_id = None
        # 业务模块
        self.business_module_id = None
        # 报道号
        self.schedule_no = None
        # 车牌
        self.truck_no = None
        # 运单总重量
        self.total_weight = None
        # 省
        self.province = None
        # 市
        self.city = None
        # 实际开单重量
        self.open_weight = None

        # 统计时间段内的历史最低开单重量
        self.min_weight = None
        # 统计时间段内的历史最高开单重量
        self.max_weight = None
        # 推荐参考载重
        self.reference_weight = None

        if city_truck_load_weight:
            self.set_attr(city_truck_load_weight)
