#!/usr/bin/python
# -*- coding: utf-8 -*-
# Description: 
# Created: lei.cheng 2021/8/27
# Modified: lei.cheng 2021/8/27
import copy
from typing import List
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.jc_single_dispatch_model.knapsack_algorithm_rule import knapsack

from app.util.enum_util import LoadTaskType


def knapsack_algorithm_model(stock_list: List[Stock], truck: Truck):
    """加权多目标 背包算法模型"""

    # 获取参数字典
    parameter = get_parameter(truck)

    # 获取拆分后的库存列表
    split_stock_list = stock_list_split(stock_list, parameter['max_weight'])

    # 模型生成结果
    pre_load_task_list = knapsack(parameter, split_stock_list)

    # 没有推荐结果，返回None
    if not pre_load_task_list:
        return None

    pre_load_plan = []
    if len(pre_load_task_list) == 1:
        pre_load_plan = pre_load_task_list
    else:
        pre_load_task_list = sorted(pre_load_task_list, key=lambda stock_item: stock_item.parent_stock_id)
        # 如果来源是同一份订单，需要合并
        for index, stock in enumerate(pre_load_task_list):
            if index != 0 and stock.parent_stock_id == pre_load_task_list[index-1].parent_stock_id:
                pre_load_plan[-1].actual_number += 1
                pre_load_plan[-1].actual_weight += stock.piece_weight
            else:
                pre_load_plan.append(stock)

    # 将装载计划转化为装车清单类型
    load_task = generate_load_task(pre_load_plan)
    return load_task


def generate_load_task(load_plan: List[Stock]):
    """
    将装载计划转化为装车清单类型
    """
    if not load_plan:
        return None

    warehouse_set = set()
    for stock_item in load_plan:
        warehouse_set.add(stock_item.deliware_house)
    if len(warehouse_set) == 1:
        load_task = create_load_task(load_plan, None, LoadTaskType.TYPE_1.value)
    else:
        load_task = create_load_task(load_plan, None, LoadTaskType.TYPE_2.value)
    return load_task


def get_weight_range(truck: Truck):
    """
    根据司机的品种和报道重量得到载重上下限
    1. 若司机未指定品种，则卷类标载[29, 35],非卷类标载[31, 35]
    2. 若司机指定载重，[w-2000, w+1000]
    :param truck:
    :return:
    """
    # 标载重量上下限
    min_weight, max_weight = 29000, 35000

    # 非标载重量上下限
    truck_weight = truck.load_weight
    if truck_weight < min_weight or truck_weight > max_weight:
        min_weight = truck_weight - 2000
        max_weight = truck_weight + 1000

    return min_weight, max_weight


def stock_list_split(stock_list, max_weight):
    """
    库存需拆分为单件, 取该货物最多可放入的件数
    :param stock_list: 原库存列表
    :param max_weight: 最大装载重量
    :return: split_stock_list: 拆分后的库存列表
    """
    # 已拆分的库存列表
    split_stock_list = []

    for stock in stock_list:
        actual_number = stock.actual_number
        max_used_number = max_weight // stock.piece_weight
        number = min(actual_number, max_used_number)
        temp_stock = copy.deepcopy(stock)
        temp_stock.actual_number = 1
        temp_stock.actual_weight = stock.piece_weight
        for num in range(number):
            split_stock_list.append(copy.deepcopy(temp_stock))
    return split_stock_list


def get_parameter(truck):
    """获取模型参数字典"""
    """参数声明"""
    w1 = 1      # 总重量权重
    w2 = 50     # 装点权重
    w3 = 50     # 卸点权重
    w4 = 50     # 货物优先级权重
    w5 = 50     # 仓库优先级权重

    # 精度缩小倍数
    multiple_num = 100

    # 权重元组
    weight_tuple = (w1, w2, w3, w4, w5)

    # 装点数量上限
    max_load_point_num = 2
    # 卸点数量上限
    max_unload_point_num = 1

    # 根据品种和载重获取当前车次的载重上限和下限
    min_weight, max_weight = get_weight_range(truck)

    # 参数字典
    parameter = {
        'multiple_num': multiple_num,
        'weight_tuple': weight_tuple,
        'min_weight': min_weight,
        'max_weight': max_weight,
        'max_load_point_num': max_load_point_num,
        'max_unload_point_num': max_unload_point_num
    }
    return parameter
