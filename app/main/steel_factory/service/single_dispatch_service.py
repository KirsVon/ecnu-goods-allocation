# -*- coding: utf-8 -*-
# Description: 单车配载服务
# Created: shaoluyu 2020/06/16
from typing import List

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.gene_algorithm_model import gene_algorithm_model
from app.main.steel_factory.rule.knapsack_algorithm_model import knapsack_algorithm_model

from app.util.enum_util import LoadTaskType
from app.util.result import Result
from model_config import ModelConfig
import json

def dispatch(stock_list: List[Stock], stock_dict, truck: Truck):
    """
    进行单车配载
    """
    # start = time.perf_counter()
    # 1. 筛选库存：根据司机提供的品种、城市进行库存筛选
    curr_stock_list = stock_filter(stock_list, truck)

    # 2. 配载模型
    # 模型1：背包算法+价值计算
    knapsack_load_plan = knapsack_algorithm_model(curr_stock_list, truck)

    # 模型2：遗传算法求解
    gene_load_plan = gene_algorithm_model(curr_stock_list, truck, knapsack_load_plan)

    # 3. 将配载方案转化为load_task，默认使用遗传算法
    knapsack_load_task = generate_load_task(knapsack_load_plan, flag="knapsack")
    gene_load_task = generate_load_task(gene_load_plan, flag="gene")
    load_task = gene_load_task

    if not load_task:
        return Result.error('无推荐结果！')
    else:
        load_task.schedule_no = truck.schedule_no
        load_task.car_mark = truck.car_mark
        # set_load_task_count(load_task)
    load_task_dict = load_task.as_dict()
    # end = time.perf_counter()
    # print("single_knapsack_model", end - start)
    return Result.success(data=load_task_dict)


def stock_filter(stock_list: List[Stock], truck: Truck) -> List[Stock]:
    """
    根据车次信息中的品种、区县、载重对原库存列表进行筛选，得到子库存列表并返回
    :param stock_list:
    :param truck:
    :return:
    """
    if not stock_list:
        return None

    sub_stock_list = []
    truck_commodity = truck.big_commodity_name
    truck_district = truck.actual_end_point
    truck_weight = truck.load_weight

    for stock_item in stock_list:
        if truck_commodity and truck_commodity != "全部" and stock_item.big_commodity_name not in \
                ModelConfig.RG_QD_COMMODITY_GROUP[truck_commodity]:
            continue

        if stock_item.actual_end_point not in truck_district:
            continue
        if stock_item.piece_weight > truck_weight + ModelConfig.RG_SINGLE_UP_WEIGHT:
            continue

        sub_stock_list.append(stock_item)

    return sub_stock_list


def generate_load_task(load_plan: List[Stock], flag) -> LoadTask:
    """
    将装载计划转化为装车清单类型，
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
    # if flag == "knapsack":
    #     print("背包算法模型开单结果")
    # if flag == "gene":
    #     print("遗传算法模型开单结果")
    #print(load_task.__dict__)
    return load_task

if __name__ == '__main__':
    with open("/Users/lalala/Desktop/test.json",'r',encoding='UTF-8') as f:
        load_dict = json.load(f)
    stock_list_str = load_dict['stock_list']
    stock_dict = load_dict['stock_dic']
    truck_str = load_dict['truck']
    stock_list = []
    for i in stock_list_str:
        stock = Stock()
        stock.set_attr(i)
        stock_list.append(stock)
    truck = Truck()
    truck.set_attr(truck_str)
    dispatch(stock_list,stock_dict,truck)
