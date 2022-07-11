#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/16 20:42
# @Author  : \pingyu
# @File    : gene_algorithm_model.py
# @Software: PyCharm
from typing import List

from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule.genetic_stock_filter import carpooling_or_not
from app.main.steel_factory.service.single_gene_algorithm_service import GA
from model_config import ModelConfig


def gene_algorithm_model(stock_list: List[Stock], truck: Truck, load_plans: List[Stock]):

    if not stock_list:
        return None

    # 参数分别表示：交叉概率、变异概率、繁衍次数、种群数
    CXPB, MUTPB, NGEN, popsize = 0.8, 0.8, 300, 50

    # 根据品种和载重获取当前车次的载重上限和下限
    min_weight, max_weight = get_weight_range(truck)

    # 库存需拆分为单件,取该货物最多可放入的件数
    for stock in stock_list:
        if stock.actual_number == 1:
            continue
        actual_number = stock.actual_number
        max_used_number = max_weight // stock.piece_weight
        number = min(actual_number, max_used_number)
        stock.actual_number = 1
        for num in range(number-1):
            stock_list.append(stock)

    parameter = [CXPB, MUTPB, NGEN, popsize, min_weight, max_weight, stock_list]
    run = GA(parameter, truck)
    cargo_truck_state, max_profit = run.GA_main()
    # print(cargo_truck_state, max_profit)

    pre_load_task_list: List[Stock] = []
    for index, state in enumerate(cargo_truck_state):
        if state == 1:
            pre_load_task_list.append(stock_list[index])
            pre_load_task_list[-1].actual_weight = pre_load_task_list[-1].piece_weight

    # 生成的装车清单不符合规则
    if not carpooling_or_not(pre_load_task_list, truck):
        return None

    if len(pre_load_task_list) == 1:
        return pre_load_task_list

    pre_load_task_list = sorted(pre_load_task_list, key=lambda stock_item: stock_item.parent_stock_id)
    # 如果来源是同一份订单，需要合并
    pre_load_plan = []
    for index, stock in enumerate(pre_load_task_list):
        if index != 0 and stock.parent_stock_id == pre_load_task_list[index-1].parent_stock_id:
            pre_load_plan[-1].actual_number += 1
            pre_load_plan[-1].actual_weight += stock.piece_weight
        else:
            pre_load_plan.append(stock)

    return pre_load_plan


def get_weight_range(truck: Truck):
    """
    根据司机的品种和报道重量得到载重上下限
    1. 若司机未指定品种，则卷类标载[29, 35],非卷类标载[31, 35]
    2. 若司机指定载重，[w-2000, w+1000]
    :param truck:
    :return:
    """

    min_weight, max_weight = 29000, 35000
    truck_commodity = truck.big_commodity_name
    truck_weight = truck.load_weight

    if truck_weight < min_weight or truck_weight > max_weight:
        min_weight -= 2000
        max_weight += 1000

    return min_weight, max_weight
