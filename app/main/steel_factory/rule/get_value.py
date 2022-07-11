#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/26 9:46
# @Author  : \pingyu
# @File    : get_value.py
# @Software: PyCharm
from typing import List

from app.main.steel_factory.entity.stock import Stock


def get_value_load_plan(pre_load_plan: List[Stock], priority_weights):
    """
    根据各优先级权重计算当前一份预装车清单的价值
    1. 货物优先级
    2. 装卸优先级
    3. 仓库优先级
    4. 重量优先级
    """
    # 默认货物优先级
    stock_priority = 10
    # 记录装卸情况
    load_warehouse = set()
    # 默认仓库优先级
    warehouse_priority = 10
    # 仓储库
    storage_warehouse = ["F1", "F2", "F10", "F20"]
    # 默认为生产+仓储一体库
    default_warehouse_priority = 1
    storage_warehouse_priority = 2
    # 记录货物总重量
    load_weight = 0

    for stock in pre_load_plan:
        # 若有拼货，该装车清单的优先级取最高优先级
        stock_priority = min(stock_priority, stock.priority)
        # 若有拼货，取优先级最高的仓库
        curr_warehouse_priority = storage_warehouse_priority if stock.deliware_house in storage_warehouse else default_warehouse_priority
        warehouse_priority = min(warehouse_priority, curr_warehouse_priority)
        load_warehouse.add(stock.deliware_house)
        load_weight += stock.piece_weight
    load_warehouse_priority = len(load_warehouse)
    load_weight_priority = load_weight // 1000
    curr_value = stock_priority * priority_weights[0] \
                 + warehouse_priority * priority_weights[1] \
                 + load_warehouse_priority * priority_weights[2] \
                 + load_weight_priority * priority_weights[3]

    return curr_value

