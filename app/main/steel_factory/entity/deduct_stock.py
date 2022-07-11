# -*- coding: utf-8 -*-
# Description: 需要扣除的库存类
# Created: jjunf 2021/02/03


from app.util.base.base_entity import BaseEntity


class DeductStock(BaseEntity):
    """
    需要扣除的扣除类：摘单未开单调度单类、已开单数据库未扣减的库存
    """

    def __init__(self, deduct_stock=None):
        # 车次号
        self.trains_no = None
        # 发货通知单
        self.notice_num = None
        # 订单号(注：查出来的原始订单号中间没有‘-’，后续需要处理)
        self.oritem_num = None
        # 出库仓库name(注：这里查询到的名称为简写)
        self.deliware_house_name = None
        # 出库仓库code
        self.deliware_house = None
        # 品名
        self.big_commodity_name = None
        # 件数
        self.actual_number: int = 0
        # 重量
        self.actual_weight: int = 0
        # 城市
        self.city = None
        # 区县
        self.district = None
        # 开单时间
        self.open_order_time = None
        # 调度状态
        self.plan_status = None
        # 调度件数
        self.plan_quantity = None

        if deduct_stock:
            self.set_attr(deduct_stock)

        if self.actual_number:
            self.actual_number = int(self.actual_number)
        if self.actual_weight:
            self.actual_weight = int(float(self.actual_weight) * 1000)
