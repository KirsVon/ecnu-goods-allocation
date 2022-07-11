# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:32
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13

from app.util.base.base_entity import BaseEntity


class Order(BaseEntity):
    """订单类"""

    def __init__(self, order=None):
        # 主键（发货通知单号、订单号、出库仓库）
        self.key = None
        # 车次号
        self.schedule_no = None
        # (开单)方式
        self.style = None
        # 发货通知单号
        self.notice_num = None
        # 订单号
        self.oritem_num = None
        # 出库仓库
        self.outstock_code = None
        # 创建时间
        self.create_date = None

        if order:
            self.set_attr(order)
