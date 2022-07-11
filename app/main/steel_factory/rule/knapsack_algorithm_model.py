#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/6 16:58
# @Author  : \pingyu
# @File    : knapsack_algorithm_model.py
# @Software: PyCharm
import time
from typing import List, Dict

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.get_value import get_value_load_plan
from app.main.steel_factory.rule.knapsack_algorithm_rule import knapsack_algorithm_rule
from app.util.enum_util import LoadTaskType
from model_config import ModelConfig

start = time.perf_counter()


def knapsack_algorithm_model(stock_list: List[Stock], truck: Truck) -> List[Stock]:
    """
    配载模型1：背包算法+价值函数计算
    :param stock_list: 库存数据
    :param truck: 车次信息
    :return: 当前车次的装车计划
    """

    # 1. 获得配载方案集合
    if not stock_list:
        return None
    load_plans = knapsack_algorithm_rule(stock_list, truck)
    # 2. 根据优化目标挑选价值最高的配载方案
    max_value_load_plan = get_value_load_plans(load_plans)

    return max_value_load_plan


def get_value_load_plans(load_plans: List[List[Stock]]) -> List[Stock]:
    """
    计算单个装车计划的价值，分别包括：货物状态优先级、仓库发运优先级、装货优先级、货物总重量
    其中只有货物重量的优先级与实际数值成正比，故修改重量的表示方式
    最终价值数值越小表示优先级越高
    :param load_plans:
    :return:
    """

    min_value_load_plan = []
    min_value = float('inf')

    # 各装车清单对应的价值
    value_of_load_plans = []

    # 各特征对应的权重值
    priority_weights = [10, 5, 7, -1]

    for plan in load_plans:
        curr_value = get_value_load_plan(plan, priority_weights)

        value_of_load_plans.append(curr_value)
        if min_value > curr_value:
            min_value = curr_value
            min_value_load_plan = plan

    return min_value_load_plan
