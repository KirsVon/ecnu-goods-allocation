# -*- coding: utf-8 -*-
# Description: 摘单记录子类
# Created: jjunf 2021/3/30 9:19
from app.util.base.base_entity import BaseEntity


class PickTaskItem(BaseEntity):
    """
    摘单子类
    """

    def __init__(self, pick_task_item=None):
        # 摘单记录号
        self.pick_id = None
        # 公司ID
        self.company_id = None
        # 池id（将多个客户绑定为一个客户后，driver_pool_id相同）
        self.driver_pool_id = None
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
        # 注释
        self.remark = None
        # 委托订单类
        self.items = []

        if pick_task_item:
            self.set_attr(pick_task_item)
