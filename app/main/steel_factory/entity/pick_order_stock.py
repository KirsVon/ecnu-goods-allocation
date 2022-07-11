# -*- coding: utf-8 -*-
# @Time    : 2021/05/10
# @Author  : luchengkai
from app.util.base.base_entity import BaseEntity
from model_config import ModelConfig


class PickOrderStock(BaseEntity):
    """委托单库存比较表"""

    def __init__(self, item=None):
        # 主键
        self.spec_desc = ''      # 规格
        self.spec_desc_name = ''    # 规格名称
        self.warehouse_out_no = ''  # 仓库no
        self.city_code = ''     # 城市id
        self.business_nature = ''   # 业务性质
        self.consignee_company_id = ''  # 客户id
        self.total_weight = 0.0     # 总重量

        self.bind_no = ''   # 捆绑单号
        self.order_no = ''  # 委托单号
        self.pick_no = ''    # 发货通知单号

        # 库存比较字段
        self.wait_compare_total_sheet = 0.0      # 待匹配委托子单的总根数
        self.current_stock_total_sheet = 0.0     # 当前库存总根数
        self.have_push_total_sheet = 0.0         # 已派单总根数
        self.ready_push_total_sheet = 0.0        # 就绪中、摘单中总根数
        if item:
            self.set_attr(item)
