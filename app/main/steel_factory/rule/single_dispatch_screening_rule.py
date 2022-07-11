#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ecnu-goods-allocation 
@File    ：single_dispatch_screening_rule.py
@IDE     ：PyCharm 
@Author  ：fengchong
@Date    ：2021/8/11 3:50 下午 
'''
from typing import List

from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from model_config import ModelConfig

def check_tail_stock(stock_list:List[Stock], truck:Truck):
    tail_select_list = []
    if truck.big_commodity_name == ''
    if truck.load_weight >= 25:

    else:
        return tail_select_list
