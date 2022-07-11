# -*- coding: utf-8 -*-
# Description: 摘单参数类
# Created: jjunf 2021/01/15
from app.util.base.base_entity import BaseEntity


class PickParam(BaseEntity):
    """
    摘单参数类
    """

    def __init__(self, param=None):
        # 品种名称
        self.commodity = None
        # 关联品种名称
        self.match_commodity = None
        # 卸点省份
        self.unload_province = None
        # 卸点城市
        self.unload_city = None
        # 卸点区县
        self.unload_district = None
        # 关联省份
        self.match_unload_province = None
        # 关联城市
        self.match_unload_city = None
        # 关联区县
        self.match_unload_district = None
        # 留货城市
        self.keep_goods_city = None
        # 留货区县
        self.keep_goods_district = None
        # 留货品种
        self.keep_goods_commodity = None
        # 留货客户
        self.keep_goods_customer = None
        # 载重配置城市
        self.weight_city = None
        # 载重配置品种
        self.weight_commodity = None
        # 载重下限
        self.weight_lower = None
        # 载重上限
        self.weight_upper = None
        # 配置类型：1品种搭配；2关联路线；3留货；4载重
        self.type_flag = None
        # 更新人id
        self.update_id = None
        # 更新时间
        self.update_time = None

        if param:
            self.set_attr(param)
