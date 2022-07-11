#!/usr/bin/python
# -*- coding: utf-8 -*-
# Description: 
# Created: lei.cheng 2021/9/8
# Modified: lei.cheng 2021/9/8
from typing import List
import json

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.gene_algorithm_model import gene_algorithm_model
from app.main.steel_factory.rule.jc_single_dispatch_model.knapsack_algorithm_filter import knapsack_algorithm_model

from app.util.enum_util import LoadTaskType
from app.util.result import Result
from model_config import ModelConfig


def dispatch(stock_list: List[Stock], truck: Truck):
    """
    京创多目标分货模型
    :param stock_list: 库存列表
    :param truck: 装载车辆
    :return: Result: json Response
    """
    # 由多目标背包模型生成装载清单
    load_task = knapsack_algorithm_model(stock_list, truck)
    if not load_task:
        return Result.error('无推荐结果！')
    load_task_dict = generate_load_task_dict(load_task, truck)
    return Result.success(data=load_task_dict)


def generate_load_task_dict(load_task: LoadTask, truck: Truck):
    """
    生成 返回的load_task json字典
    :param load_task: load_task结果
    :param truck: 装载车辆
    :return: load_task_dict: load_task 字典
    """
    if not load_task:
        return None
    load_task.schedule_no = truck.schedule_no
    load_task.car_mark = truck.car_mark
    load_task_dict = load_task.as_dict()
    return load_task_dict
