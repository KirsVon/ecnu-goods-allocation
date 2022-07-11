# -*- coding: utf-8 -*-
# Description: 管厂需要分派的委托订单类
# Created: jjunf 2021/3/29 17:04
from app.util.base.base_entity import BaseEntity


class OrderWt(BaseEntity):
    """管厂需要分派的委托订单"""

    def __init__(self, order_wt=None):
        # 公司ID
        self.company_id = None
        # 业务板块ID
        self.business_module_id = None
        # 起点
        self.start_point = None
        # 委托单号
        self.order_no = None
        # 发货通知单号
        self.pick_no = None
        # 委托单位
        self.consignor_company_id = None
        # 运输单位
        self.carrier_company_id = None
        # 收货单位
        self.consumer = None
        # 收货单位名称
        self.consumer_name = None
        # 司机池id（将多个客户绑定为一个客户后，driver_pool_id相同）
        self.driver_pool_id = None
        # 司机池id（将多个客户绑定为一个客户后，driver_pool_id相同）
        self.driver_pool_name = None
        # 总重量
        self.total_weight = 0
        # 业务类型
        self.business_nature = None
        # 委托状态
        self.status = None
        # 备注
        self.remark = None
        # 推荐车辆
        self.r_vehicle = None
        # 推荐司机手机号
        self.recommend_mobile = None
        # 推荐司机姓名
        self.recommend_driver = None
        # 捆绑单号
        self.bind_no = None
        # 目的地编号
        self.end_point = None
        # 省份
        self.province = None
        # 城市
        self.city = None
        # 区县
        self.district = None
        # 乡
        self.town = None
        # 此条订单的最新更新时间
        self.update_date = None
        # 优先级：YXJ10最低（默认），YXJ20普通，YXJ30加急
        self.delegation_priority = 'YXJ20'
        # 子项
        self.items = []

        if order_wt:
            self.set_attr(order_wt)

        self.total_weight = float(self.total_weight)
        # town为空字符串、为None的情况统一为None
        if not self.town:
            self.town = None
