#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：ecnu-goods-allocation
@File    ：genetic_stock_filter.py
@IDE     ：PyCharm
@Author  ：Feng Chong
@Date    ：2021/8/18 10:34 上午
"""
from typing import List
from app.main.steel_factory.entity.stock import Stock
from copy import copy
from app.main.steel_factory.entity.truck import Truck
from model_config import ModelConfig


def carpooling_or_not(stock_list: List[Stock], truck: Truck):

    self_carpooling_group = ['老区-型钢', '老区-线材', '老区-螺纹', '老区-开平板', '老区卷板', '新产品-冷板']
    carpooling_lbg = ['F10', 'F20']
    big_commodity_name_dict = {}
    deliware_house_dict = {}
    for i in stock_list:
        if i.big_commodity_name not in big_commodity_name_dict.keys():
            big_commodity_name_dict[i.big_commodity_name] = []
            big_commodity_name_dict[i.big_commodity_name].append(copy(i))
        else:
            big_commodity_name_dict[i.big_commodity_name].append(copy(i))

        if i.deliware_house not in deliware_house_dict.keys():
            deliware_house_dict[i.deliware_house] = []
            big_commodity_name_dict[i.big_commodity_name].append(copy(i))
        else:
            big_commodity_name_dict[i.big_commodity_name].append(copy(i))

    big_commodity_name_list = list(big_commodity_name_dict.keys())
    deliware_house_list = list(deliware_house_dict.keys())

    # 确保司机要的货在Stock_list中
    if truck.big_commodity_name not in big_commodity_name_list:
        return False

    # 单品种拼货判断
    for i in big_commodity_name_list:
        if i in self_carpooling_group and len(big_commodity_name_list) > 1:
            return False
        # 老区-型钢规格数量判断
        if i == '老区-型钢':
            specs_list = []
            for j in big_commodity_name_dict[i]:
                if j.specs not in specs_list:
                    specs_list.append(j.specs)
            if len(specs_list) > 2:
                return False

    # 拼货仓库判断
    if len(deliware_house_list) > 2:
        return False

    # 岚北港单独拼货判断
    if 'F10' in deliware_house_list or 'F20' in deliware_house_list:
        for i in deliware_house_list:
            if i not in carpooling_lbg:
                return False

    # 载重判断
    MAX_LOAD_WEIGHT = 0
    MIN_LOAD_WEIGHT = 0
    if 35000 >= truck.load_weight >= 29000 and truck.big_commodity_name in ModelConfig.RG_J_GROUP:  # 如果是卷类，且在卷类标载范围内 车辆载重区间
        MAX_LOAD_WEIGHT = truck.load_weight + 1000
        MIN_LOAD_WEIGHT = 29000
    elif 35000 >= truck.load_weight >= 31000 and truck.big_commodity_name not in ModelConfig.RG_J_GROUP and truck.big_commodity_name != '全部': # 如果是非卷类，且在非卷类的载重区间内
        MAX_LOAD_WEIGHT = truck.load_weight + 1000
        MIN_LOAD_WEIGHT = 31000
    else: # 如果大品名是全部，或者是卷类、非卷不在其标载范围内的
        MAX_LOAD_WEIGHT = truck.load_weight + 1000
        MIN_LOAD_WEIGHT = truck.load_weight - 2000
    load_task_weight = 0
    for stock in stock_list:
        load_task_weight += stock.piece_weight

    #两卸判断
    standard_address_list = []
    for i in stock_list:
        if i.standard_address not in standard_address_list:
            standard_address_list.append(i.standard_address)
    if len(standard_address_list) > 1:
        return False

    # 大重量卷类1件，可以直接运走
    if load_task_weight < MIN_LOAD_WEIGHT or load_task_weight > MAX_LOAD_WEIGHT:
        if load_task_weight < MIN_LOAD_WEIGHT and len(stock_list) == 1 and \
                stock_list[0].big_commodity_name in ModelConfig.RG_J_GROUP and \
                stock_list[0].piece_weight >= 26000 and \
                stock_list[0].actual_number == 1:
            pass
        else:
            return False

    return True
