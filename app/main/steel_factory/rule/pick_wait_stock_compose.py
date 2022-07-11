# -*- coding: utf-8 -*-
# Description: 将尾货中同客户等货的库存进行配货
# Created: jjunf 2021/03/11
from typing import List

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule.pick_goods_dispatch_filter import stock_compose_one_consumer
from model_config import ModelConfig


def pick_wait_stock_compose(tail_list: List[Stock]):
    """
    将尾货中同客户等货的库存进行配货
    :param tail_list:
    :return:
    """
    # 车次列表
    load_task_list: List[LoadTask] = []
    # 等货的库存
    wait_list = []
    for stock in tail_list:
        if stock.deliware_house.find('3') != -1:
            stock.deliware_house = stock.deliware_house.split('-')[0]
            stock.stock_id = stock.parent_stock_id
            wait_list.append(stock)
    # tail_list中等货库存以外的库存
    tail_list = [i for i in tail_list if i not in wait_list]
    # 将等货库存按厂区分组
    wait_dict = {'宝华': [], '厂内': [], '岚北港': [], '未知厂区': []}
    if wait_list:
        for wait_stock in wait_list:
            if wait_stock.deliware_house in ModelConfig.RG_WAREHOUSE_GROUP[0]:
                wait_dict['宝华'].append(wait_stock)
            elif wait_stock.deliware_house in ModelConfig.RG_WAREHOUSE_GROUP[1]:
                wait_dict['厂内'].append(wait_stock)
            elif wait_stock.deliware_house in ModelConfig.RG_WAREHOUSE_GROUP[2]:
                wait_dict['岚北港'].append(wait_stock)
            else:
                wait_dict['未知厂区'].append(wait_stock)
    # wait_list中最后剩余的
    surplus_wait_list = []
    # 同厂区组合
    for value in wait_dict.values():
        if value:
            # 将tail_list中标载等货的货物同客户之间进行组合（一装一卸、两装一卸(同区)）
            temp_load_task_list = []
            value = stock_compose_one_consumer(value, temp_load_task_list)
            load_task_list.extend(temp_load_task_list)
            surplus_wait_list.extend(value)
    if surplus_wait_list:
        for wait_stock in surplus_wait_list:
            wait_stock.deliware_house += '-3'
        tail_list.extend(surplus_wait_list)
    return load_task_list, tail_list
