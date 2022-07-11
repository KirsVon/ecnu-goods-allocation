# -*- coding: utf-8 -*-
# Description: 摘单记录类
# Created: jjunf 2021/3/29 18:23
from app.util.base.base_entity import BaseEntity


class PickTask(BaseEntity):
    """
    摘单类
    """

    def __init__(self, pick_task=None):
        # 摘单记录号
        self.pick_id = None
        # 公司ID
        self.company_id = None
        # 池id（将多个客户绑定为一个客户后，driver_pool_id相同）
        self.driver_pool_id = None
        # 司机池名称，非司机池为默认值None
        self.driver_pool_name = None
        # 业务板块ID
        self.business_module_id = None
        # 起点
        self.start_point = None
        # 委托单号，用;拼接
        self.order_no = None
        # 重量
        self.total_weight = 0
        # 总车次数
        self.truck_num = 0
        # 推荐车辆
        self.r_vehicle = None
        # 推荐手机号
        self.recommend_mobile = None
        # 推荐司机姓名
        self.recommend_driver = None
        # 省
        self.province = None
        # 城市
        self.city = None
        # 区县
        self.district = None
        # 乡
        self.town = None
        # 收货用户
        self.consumer = set()
        # 收货单位名称
        self.consumer_name = None
        # 注释
        self.remark = None
        # 摘单子类
        self.items = []

        if pick_task:
            self.set_attr(pick_task)
