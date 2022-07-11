#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/6 15:57
# @Author  : \pingyu
# @File    : knapsack_algorithm_rule.py
# @Software: PyCharm
import json
import time
from typing import List, Dict
from app.main.steel_factory.entity.stock import Stock
# from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.entity.load_task import LoadTask
from model_config import ModelConfig
import math
import numpy as np
from copy import copy
from model_config import ModelConfig
import pandas as pd

start = time.perf_counter()
def knapsack_algorithm_rule(stock_list: List, truck: Truck):
    """
    1. 大件订单最小甩货拆分
    2. 不足标载订单按规则拼货
    """
    order_dict = dict()
    for c in stock_list:
        order_dict.setdefault(c.oritem_num + "," + c.deliware_house, []).append(c)
    load_plan_list = list()
    tail_stock_list = list()
    MIN_LOAD_CAPACITY = math.ceil((truck.load_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT) / 1000)
    MAX_LOAD_CAPACITY = ((truck.load_weight + ModelConfig.RG_SINGLE_UP_WEIGHT) / 1000)
    if truck.big_commodity_name in ModelConfig.RG_J_GROUP:
        if 29000 <= truck.load_weight and 35000 >= truck.load_weight:
            MAX_LOAD_CAPACITY = ((truck.load_weight + ModelConfig.RG_SINGLE_UP_WEIGHT) / 1000)
            MIN_LOAD_CAPACITY = 29
    else:
        if 31000 <= truck.load_weight and 35000 >= truck.load_weight:
            MAX_LOAD_CAPACITY = ((truck.load_weight + ModelConfig.RG_SINGLE_UP_WEIGHT) / 1000)
            MIN_LOAD_CAPACITY = 31
    def dp(cargos):
        result_load_plan_list = list()  # :List[LoadTask]
        tail_list = []  # :List[Stock]
        shipping_dict = {}
        sum_weight = 0.0
        sum_count = 0
        # -----------------------疑问：每个订单号对应一个规格货物吗？-------------------------
        unit_weight = cargos[0].piece_weight
        if unit_weight == 0.0:
            return result_load_plan_list, tail_list

        for c in cargos:
            shipping_dict.setdefault(c.notice_num, []).append(c)  # 验证是否同个订单下有多个发货通知单，是否有区别
            sum_weight += c.actual_weight
            sum_count += c.actual_number
        sum_weight /= 1000
        unit_weight /= 1000

        # 动态规划划分订单
        # 1:找到达到装载限制的list
        load_type = []

        if sum_weight < MIN_LOAD_CAPACITY or unit_weight > MAX_LOAD_CAPACITY:
            tail_list.extend(cargos)
            return result_load_plan_list, tail_list

        max_count = min_count = math.floor(MIN_LOAD_CAPACITY / unit_weight)
        tmp_weight = math.floor(MIN_LOAD_CAPACITY / unit_weight) * unit_weight
        while tmp_weight < MAX_LOAD_CAPACITY:
            tmp_weight += unit_weight
            max_count += 1
        # 判断最小数量的合理性：总重量大于最小值
        min_weight = min_count * unit_weight
        if min_weight < MIN_LOAD_CAPACITY:
            min_count += 1
            min_weight += unit_weight
        # 判断最大数量的合理性：总重量小于最大值
        max_weight = max_count * unit_weight
        if max_weight > MAX_LOAD_CAPACITY:
            max_count -= 1
            max_weight -= unit_weight
        if min_count > max_count:
            tail_list.extend(cargos)
            return result_load_plan_list, tail_list
        # 通过最小件数和最大件数获取打包类型
        for i in range(min_count, max_count + 1):
            load_type.append(i)

        # 2:dp
        # i=装一车的方案; j=总重量拆分
        #   1.不使用当前方案arr[i]-->dp[i-1][j]
        #   2.用n个当前方案arr[i]-->max{sum-dp[i-1][j-n*arr[i]]-n*arr[i],0}
        # dp[i][j]=min{dp[i-1][j],max{sum-dp[i-1][j-n*arr[i]]-n*arr[i],0}}
        arr_j = [x * unit_weight for x in load_type]

        arr_i = []
        for index in range(MIN_LOAD_CAPACITY, math.ceil(sum_weight) + 1):
            arr_i.append(index)

        dp_matrix = np.arange(len(arr_i) * len(arr_j)).reshape(len(arr_i), len(arr_j))
        result = np.arange(len(arr_i) * len(arr_j)).reshape(len(arr_i), len(arr_j))
        for index_j in range(len(arr_j)):
            # 初始化第一行
            if arr_j[index_j] < arr_i[0]:
                dp_matrix[0][index_j] = arr_i[0] - arr_j[index_j]
                result[0][index_j] = 1
            else:
                dp_matrix[0][index_j] = arr_i[0]
                result[0][index_j] = 0
        for index_i in range(len(arr_i)):
            if arr_i[index_i] >= arr_j[0]:
                dp_matrix[index_i][0] = arr_i[index_i] - math.floor(arr_i[index_i] / arr_j[0]) * arr_j[0]
                result[index_i][0] = math.floor(arr_i[index_i] / arr_j[0])
            else:
                dp_matrix[index_i][0] = arr_i[index_i]
                result[index_i][0] = 0
        i = 1
        j = 1
        while i < len(arr_i):
            j = 1
            while j < len(arr_j):
                dp_1 = dp_matrix[i][j - 1]
                min_n = 1
                n = 1
                # next_i 下一个重量的index，arr_i[i] - min_n * arr_j[j]为下一个重量值，- curr_config_class.MIN_LOAD_CAPACITY做下标对其
                next_i = max(math.floor(arr_i[i] - min_n * arr_j[j] - MIN_LOAD_CAPACITY), 0)
                while i - n * arr_j[j] > 0:
                    n += 1
                    tmp_i = math.floor(arr_i[i] - min_n * arr_j[j] - MIN_LOAD_CAPACITY)
                    if tmp_i < 0:
                        break
                    if dp_matrix[next_i][j - 1] > dp_matrix[tmp_i][j - 1]:
                        min_n = n
                        next_i = tmp_i
                n = min_n
                # next_i = max(math.floor(i - min_n * arr_j[j] - curr_config_class.MIN_LOAD_CAPACITY), 0)
                dp_2 = dp_matrix[next_i][j - 1]
                if dp_2 < 0:
                    dp_2 = arr_i[i]
                    n = 0
                if dp_1 < dp_2:
                    dp_matrix[i][j] = dp_1
                    result[i][j] = 0
                else:
                    dp_matrix[i][j] = dp_2
                    result[i][j] = n
                j += 1
            i += 1
        i -= 1
        j -= 1

        while i >= 0 and j >= 0:
            if result[i][j] == 0:
                i -= max(math.floor(result[i][j] * arr_j[j]), 1)
                continue
            tmp_cargo = Stock()
            tmp_cargo.set_attr(cargos[0].as_dict())
            #tmp_cargo.set_weight(arr_j[j], load_type[j])
            tmp_cargo.actual_weight = arr_j[j] * 1000
            if load_type[j] != 0:
                tmp_cargo.actual_number = load_type[j]
                tmp_cargo.piece_weight = tmp_cargo.actual_weight / tmp_cargo.actual_number
            sum_weight -= arr_j[j]
            sum_count -= load_type[j]
            virtual_load_plan = get_load_plan_by_virtual_car([tmp_cargo])
            set_load_task_by_items(virtual_load_plan)
            result_load_plan_list.append(virtual_load_plan)
            for index in range(1, result[i][j]):
                # virtual_load_plan = get_load_plan_by_virtual_car([tmp_cargo])
                result_load_plan_list.append(copy(virtual_load_plan))
                sum_weight -= arr_j[j]
                sum_count -= load_type[j]

            i -= max(math.floor(result[i][j] * arr_j[j]), 1)
            j -= 1
        if sum_weight > 0 and sum_count > 0:
            tail = Stock()
            tail.set_attr(cargos[0].as_dict())
            tail.actual_weight = sum_weight
            tail.actual_number = sum_count
            tail_list.append(tail)

        return result_load_plan_list, tail_list
    for key, value in order_dict.items():
        tmp_load_plan_list, tmp_tail_list = dp(value)
        load_plan_list.extend(tmp_load_plan_list)
        tail_stock_list.extend(tmp_tail_list)

    def can_collocate(stock, load_task:LoadTask):
        if len(load_task.items) == 0:
            return True
        #仓库拼货限制
        # F10、F20可互相拼货，但不可与其他仓库拼货，其余仓库可自由拼货
        deliware_house_list = []
        for i in load_task.items:
            if i.deliware_house not in deliware_house_list:
                deliware_house_list.append(i.deliware_house)
        if stock.deliware_house == "F10" or stock.deliware_house == "F20":
            for i in deliware_house_list:
                if i != "F10" or i != "F20":
                    return  False
        if "F10" in deliware_house_list or "F20" in deliware_house_list:
            if stock.deliware_house not in ["F10","F20"]:
                return  False
        # 最多两个仓库拼货
        if len(deliware_house_list) == 2 and stock.deliware_house not in deliware_house_list:
            return False

        # 品种限制
        # 单品种拼货
        single_delivery_carpool = ["老区-型钢","老区-线材","老区-螺纹","老区-卷板","老区-开平板","新产品-冷板"]
        big_commodity_name_list = []
        for i in load_task.items:
            if i.big_commodity_name not in big_commodity_name_list:
                big_commodity_name_list.append(i.big_commodity_name)
        if stock.big_commodity_name in single_delivery_carpool:
            if len(big_commodity_name_list) > 1:
                return False
            elif len(big_commodity_name_list) == 1 and stock.big_commodity_name != big_commodity_name_list[0]:
                if big_commodity_name_list[0] == "新产品-白卷" and stock.big_commodity_name == "老区-卷板":
                    pass
                else:
                    return False
        # 老区-卷板规格限制
        if stock.big_commodity_name == "老区-型钢":
            specs = []
            for i in load_task.items:
                if i.specs not in specs:
                    specs.append(i.specs)
                if i.big_commodity_name != "老区-型钢":
                    return False
            if len(specs) > 2 or (len(specs) == 2 and stock.specs not in specs):
                return False
        return True
    def sort(cargo_list):
        """ 货物列表排序 """
        # 按优先级排序
        cargo_list = sorted(cargo_list, key=lambda cargo: cargo.actual_weight, reverse=True)
        return cargo_list

    def sort_by_piece_weight(cargo_list):
        """ 货物列表排序 """
        # 按优先级排序
        cargo_list = sorted(cargo_list, key=lambda cargo: cargo.piece_weight, reverse=True)
        return cargo_list
    tmp_tail_stock_list = copy(sort(tail_stock_list))
    remaining_cargo_list = []
    #单间拆拼
    for i in tmp_tail_stock_list:
        for j in range(0, i.actual_number):
            tmp = Stock()
            tmp.set_attr(i.__dict__)
            tmp.actual_weight = i.piece_weight
            tmp.actual_number = 1
            remaining_cargo_list.append(tmp)
    list_index = 0
    for i in range(len(remaining_cargo_list)):
        if remaining_cargo_list[i].actual_weight > 100:
            list_index = i
        else:
            break
    remaining_cargo_list = remaining_cargo_list[0:list_index + 1]
    remaining_cargo_list = sort_by_piece_weight((remaining_cargo_list))



    def find_combination(main_cargo:Stock, remaining_cargo_list:List[Stock]):
        # 寻找可组合货物
        load_plan = get_load_plan_by_virtual_car([main_cargo])
        set_load_task_by_items(load_plan)
        index = 0
        while index < len(remaining_cargo_list):
            # 判断、执行<添加-删除>
            if can_collocate(remaining_cargo_list[index], load_plan):
                # split order
                sum_weight = remaining_cargo_list[index].actual_weight
                sum_count = remaining_cargo_list[index].actual_number
                add_type = load_plan_add_stock(load_plan, remaining_cargo_list[index])
                if add_type == 1:
                    tmp = Stock()
                    tmp.set_attr(remaining_cargo_list[index].as_dict())
                    tmp.actual_weight = tmp.piece_weight = remaining_cargo_list[index].piece_weight
                    tmp.actual_number = 1
                    load_plan.items.append(tmp)
                    load_plan.total_weight += tmp.piece_weight
                    remaining_cargo_list[index].actual_weight -= remaining_cargo_list[index].piece_weight
                    remaining_cargo_list[index].actual_number -= 1
                elif add_type == 0:
                    load_task_weight = load_plan.total_weight
                    unit_weight = remaining_cargo_list[index].piece_weight
                    lower_bound = int((MIN_LOAD_CAPACITY*1000-load_task_weight)/unit_weight)
                    upper_bound = int((MAX_LOAD_CAPACITY*1000-load_task_weight)/unit_weight)
                    tmp = Stock()
                    tmp.set_attr(remaining_cargo_list[index].as_dict())
                    tmp.actual_weight = tmp.piece_weight = remaining_cargo_list[index].piece_weight
                    tmp.actual_number = 1
                    if lower_bound == upper_bound and lower_bound <= remaining_cargo_list[index].actual_number:
                        for i in range(0, lower_bound):
                            load_plan.items.append(copy(tmp))
                        set_load_task_by_items(load_plan)
                        remaining_cargo_list[index].actual_number = 0
                        remaining_cargo_list[index].actual_weight = 0
                    elif lower_bound == upper_bound and lower_bound> remaining_cargo_list[index].actual_number:
                        for i in range(0,remaining_cargo_list[index].actual_number):
                            load_plan.items.append(copy(tmp))
                        set_load_task_by_items(load_plan)
                        remaining_cargo_list[index].actual_number = 0
                        remaining_cargo_list[index].actual_weight = 0
                    elif lower_bound < upper_bound and remaining_cargo_list[index].actual_number >= upper_bound:
                        for i in range(0, upper_bound):
                            load_plan.items.append(copy(tmp))
                        set_load_task_by_items(load_plan)
                        remaining_cargo_list[index].actual_number -=upper_bound
                        remaining_cargo_list[index].actual_weight -= upper_bound *remaining_cargo_list[index].piece_weight
                    elif lower_bound < upper_bound and remaining_cargo_list[index].actual_number < upper_bound:
                        for i in range(0, remaining_cargo_list[index].actual_number):
                            load_plan.items.append(copy(tmp))
                        set_load_task_by_items(load_plan)
                        remaining_cargo_list[index].actual_number = 0
                        remaining_cargo_list[index].actual_weight = 0
                elif add_type == -1:
                    index += 1
                    continue
                sum_weight = remaining_cargo_list[index].actual_weight
                sum_count = remaining_cargo_list[index].actual_number
                if sum_weight <= 0:
                    del remaining_cargo_list[index]
                else:
                    index += 1
            else:
                index += 1
        return load_plan, remaining_cargo_list

    def load_plan_add_stock(load_task:LoadTask,stock:Stock):
        return_type = 0
        if MIN_LOAD_CAPACITY  > (load_task.total_weight + stock.piece_weight)/1000:
            return_type = 0
        elif MAX_LOAD_CAPACITY >= (load_task.total_weight + stock.piece_weight)/1000 >=  MIN_LOAD_CAPACITY:
            return_type = 1
        else:
            return_type = -1
        return return_type

    remaining_load_plan_list = []
    remaining_sum_weight = 0.0
    for i in remaining_cargo_list:
        remaining_sum_weight += i.actual_weight

    one_load_uncompleted_list = []
    beginning_queue = copy(remaining_cargo_list)
    while len(remaining_cargo_list) > 0:
        main_cargo = beginning_queue[0]
        beginning_queue.pop(0)
        remaining_cargo_list = copy(beginning_queue)
        # 循环取件
        while main_cargo.actual_number >= 1:
            # 取一件
            #print("当前拼货对象：",main_cargo.piece_weight, main_cargo.actual_weight)
            tmp = Stock()
            tmp.set_attr(main_cargo.as_dict())
            tmp.actual_weight = tmp.piece_weight = main_cargo.piece_weight
            tmp.actual_number = 1
            main_cargo.actual_weight = main_cargo.actual_weight - main_cargo.piece_weight
            main_cargo.actual_number = main_cargo.actual_number - 1
            # 拼车过程
            can_carpooling_stock = []
            cant_carpooling_stock = []
            for i in range(len(remaining_cargo_list)):
                if remaining_cargo_list[i].standard_address == main_cargo.standard_address:
                    can_carpooling_stock.append(copy(remaining_cargo_list[i]))
                else:
                    cant_carpooling_stock.append(copy(remaining_cargo_list[i]))
            remaining_cargo_list = cant_carpooling_stock
            tmp_mark = str(tmp.deliware_house) + ";" +tmp.oritem_num + ";" +tmp.notice_num
            # 一装货物
            if tmp_mark not in one_load_uncompleted_list:
                one_load_stock = []
                two_load_stock = []
                for i in can_carpooling_stock:
                    if i.deliware_house == tmp.deliware_house:
                        one_load_stock.append(copy(i))
                    else:
                        two_load_stock.append(copy(i))
            #print(carpooling_zero_one_knapsack(one_load_stock, math.floor(MAX_LOAD_CAPACITY-tmp.actual_weight/1000)))
                tmp_load_plan, one_load_stock = find_combination(tmp, one_load_stock)
                remaining_cargo_list.extend(two_load_stock)
                if tmp_load_plan.total_weight >= MIN_LOAD_CAPACITY * 1000 and tmp_load_plan.total_weight <= MAX_LOAD_CAPACITY*1000:
                    remaining_load_plan_list.append(tmp_load_plan)
                    after_queue= []
                    for i in range(1, len(tmp_load_plan.items)):
                        for j in range(len(beginning_queue)):
                            if beginning_queue[j].deliware_house == tmp_load_plan.items[i].deliware_house and beginning_queue[j].oritem_num == tmp_load_plan.items[i].oritem_num and tmp_load_plan.items[i].notice_num == beginning_queue[j].notice_num and tmp_load_plan.items[i].actual_weight == beginning_queue[j].actual_weight:
                                after_queue.append(beginning_queue[j])
                                break
                    for i in after_queue:
                        for j in beginning_queue:
                            if j.deliware_house == i.deliware_house  and j.oritem_num == i.oritem_num and i.notice_num == j.notice_num and i.actual_weight == j.actual_weight:
                                beginning_queue.remove(j)
                                break
                else:
                    beginning_queue.append(tmp)
                    one_load_uncompleted_list.append(tmp_mark)
            else:
                tmp_load_plan, can_carpooling_stock = find_combination(tmp, can_carpooling_stock)
                if (tmp_load_plan.total_weight >= MIN_LOAD_CAPACITY * 1000 and tmp_load_plan.total_weight <= MAX_LOAD_CAPACITY * 1000) or \
                        (len(tmp_load_plan.items) == 1 and tmp_load_plan.items[0].big_commodity_name in ModelConfig.RG_J_GROUP and tmp_load_plan.total_weight >= 26000):
                    remaining_load_plan_list.append(tmp_load_plan)
                    after_queue = []
                    for i in range(1, len(tmp_load_plan.items)):
                        for j in range(len(beginning_queue)):
                            if beginning_queue[j].deliware_house == tmp_load_plan.items[i].deliware_house and \
                                    beginning_queue[j].oritem_num == tmp_load_plan.items[i].oritem_num and \
                                    tmp_load_plan.items[i].notice_num == beginning_queue[j].notice_num and \
                                    tmp_load_plan.items[i].actual_weight == beginning_queue[j].actual_weight:
                                after_queue.append(beginning_queue[j])
                                break
                    for i in after_queue:
                        for j in beginning_queue:
                            if j.deliware_house == i.deliware_house and j.oritem_num == i.oritem_num and i.notice_num == j.notice_num and i.actual_weight == j.actual_weight:
                                beginning_queue.remove(j)
                                break
                else:
                    after_queue = []
                    for i in range(len(can_carpooling_stock)):
                        for j in range(len(beginning_queue)):
                            if beginning_queue[j].deliware_house == can_carpooling_stock[i].deliware_house and \
                                    beginning_queue[j].oritem_num == can_carpooling_stock[i].oritem_num and \
                                    can_carpooling_stock[i].notice_num == beginning_queue[j].notice_num and \
                                    beginning_queue[j].actual_weight == can_carpooling_stock[i].actual_weight:
                                after_queue.append(beginning_queue[j])
                                break
                    for i in after_queue:
                        for j in beginning_queue:
                            if j.deliware_house == i.deliware_house and j.oritem_num == i.oritem_num and i.notice_num == j.notice_num and i.actual_weight == j.actual_weight:
                                beginning_queue.remove(j)
                                break
    def load_task_screening_deduplication(load_task_list:List[LoadTask]):
        #screening
        def sort_by_load_task_load_weight(load_plan_list):
            """ 货物列表排序 """
            # 按优先级排序
            cargo_list = sorted(load_plan_list, key=lambda load_plan: load_plan.total_weight, reverse=True)
            return cargo_list
        def sort_by_item_parent_id(item_list):
            """货物父母id排序后拼接"""
            item_list = sorted(item_list,key=lambda  item:item.parent_stock_id, reverse=True)
            return item_list
        load_task_list = sort_by_load_task_load_weight(load_task_list)
        index = 0
        for i in range(len(load_task_list)):
            if (load_task_list[i].total_weight >= MIN_LOAD_CAPACITY * 1000) or \
                    (load_task_list[i].total_weight >= 26000 and len(load_task_list[i].items) == 1 and load_task_list[i].items[0].big_commodity_name in ModelConfig.RG_J_GROUP):
                index+=1
            else:
                break
        load_task_list = load_task_list[0:index]
        #deduplication
        de_dict = {}
        for i in range(len(load_task_list)):
            item_list = load_task_list[i].items
            item_list = sort_by_item_parent_id(item_list)
            items_stock_str = ""
            for j in item_list:
                items_stock_str += str(j.parent_stock_id)
                items_stock_str += ";"
                items_stock_str += str(int(j.actual_weight))
                items_stock_str += ";"
                items_stock_str += str(int(j.actual_number))
                items_stock_str += ";"
            if items_stock_str not in de_dict.keys():
                de_dict[items_stock_str] = [i]
            else:
                tmp_list = de_dict[items_stock_str]
                tmp_list.append(i)
                de_dict[items_stock_str] = tmp_list
        deduplicated_load_last_list = []
        for key in de_dict.keys():
            stock_list = de_dict.get(key)
            deduplicated_load_last_list.append(load_task_list[stock_list[0]])

        return deduplicated_load_last_list

    load_plan_list.extend(remaining_load_plan_list)
    load_plan_list = load_task_screening_deduplication(load_plan_list)
    #多拼类型判别
    final_load_plan_list = []
    for i in load_plan_list:
        big_commodity_list = []
        for j in i.items:
            big_commodity_list.append(j.big_commodity_name)
        if truck.big_commodity_name in big_commodity_list:
            final_load_plan_list.append(i)
    #单卷判别

    stock_matrix = []
    # final_str = ""
    for i in final_load_plan_list:
        stock_item_list = []
        stock_item_dict = {}
        for j in i.items:
            stock_str  = j.deliware_house + ';' + j.oritem_num + ';' + j.oritem_num
            if stock_str not in stock_item_dict.keys():
                stock_item_dict[stock_str] = []
                stock_item_dict[stock_str].append(j)
            else:
                stock_item_dict[stock_str].append(j)
        for key in stock_item_dict.keys():
            tmp = Stock()
            tmp.set_attr(stock_item_dict[key][0].__dict__)
            if len(stock_item_dict[key]) > 1:
                for j in range(1, len(stock_item_dict[key])):
                    tmp.actual_weight += stock_item_dict[key][j].actual_weight
                    tmp.actual_number += stock_item_dict[key][j].actual_number
            stock_item_list.append(tmp)
        stock_matrix.append(stock_item_list)
    #     s = json.dumps(i, default=lambda i:i.__dict__,ensure_ascii=False)
    #     final_str += s
    # fh = open('/Users/lalala/Desktop/test.txt', 'w',encoding='utf-8')
    # fh.write(final_str)
    # fh.close()
    return stock_matrix


def set_load_task_by_items(load_task:LoadTask):
    load_task.count = 0
    load_task.total_weight = 0
    load_task.city = load_task.items[0].city
    load_task.province = load_task.items[0].province
    load_task.end_point = []
    load_task.consumer = []
    for i in load_task.items:
        load_task.count += i.actual_number
        load_task.total_weight += i.actual_weight
        if i.actual_end_point not in load_task.end_point:
            load_task.end_point.append(i.actual_end_point)
        if i.consumer not in load_task.consumer:
            load_task.consumer.append(i.consumer)


def get_load_plan_by_virtual_car(cargo_list: List[Stock]) -> LoadTask:
    """
    1.  使用货物列表补充装车清单
    """
    load_task = LoadTask()
    if len(cargo_list) >= 1:
        # 补充装车清单
        for cargo in cargo_list:
            load_task.items.append(cargo)
    return load_task

def carpooling_zero_one_knapsack(stock_list:List[Stock], MAX_LOAD_WEIGHT:int):
    #初始化第0行, 初始化第0列
    dp_matrix = [[0 for i in range(MAX_LOAD_WEIGHT+1)] for j in range(len(stock_list)+1)]
    result_matrix = [["" for i in range(MAX_LOAD_WEIGHT+1)] for j in range(len(stock_list)+1)]
    v = [0 for i in range(len(stock_list)+1)]
    w = [0 for i in range(len(stock_list)+1)]
    for i in range(1,len(stock_list) + 1):
        v[i] = stock_list[i-1].actual_weight / 1000
        w[i] = stock_list[i-1].actual_weight / 1000
    i = 0
    j = 0
    for i in range(1,len(stock_list)+1):
        for j in range(0, MAX_LOAD_WEIGHT+1):
            dp_matrix[i][j] = dp_matrix[i-1][j]
            if (j >= v[i]):
                if dp_matrix[i][j] > dp_matrix[i - 1][math.floor(j - v[i])] + w[i]:
                    dp_matrix[i][j] = dp_matrix[i-1][j]
                    result_matrix[i][j] = result_matrix[i-1][j]
                else:
                    dp_matrix[i][j] = dp_matrix[i - 1][math.floor(j - v[i])] + w[i]
                    # if dp_matrix[i][j] > MAX_LOAD_WEIGHT:
                    #     dp_matrix[i][j] = dp_matrix[i - 1][j]
                    #     result_matrix[i][j] = result_matrix[i - 1][j]
                    # else:
                    result_matrix[i][j] = result_matrix[i - 1][j]
                    result_matrix[i][j] += str(i)
    return dp_matrix[i][j], result_matrix[i][j]


def carpooling_zero_one_knapsack_with_two_load_restriction(stock_list:List[Stock], MAX_LOAD_WEIGHT:int):
    #初始化第0行, 初始化第0列
    dp_matrix = [[0 for i in range(MAX_LOAD_WEIGHT+1)] for j in range(len(stock_list)+1)]
    result_matrix = [["" for i in range(MAX_LOAD_WEIGHT+1)] for j in range(len(stock_list)+1)]
    v = [0 for i in range(len(stock_list)+1)]
    w = [0 for i in range(len(stock_list)+1)]
    for i in range(1,len(stock_list) + 1):
        v[i] = stock_list[i-1].actual_weight / 1000
        w[i] = stock_list[i-1].actual_weight / 1000
    i = 0
    j = 0
    for i in range(1,len(stock_list)+1):
        for j in range(MAX_LOAD_WEIGHT+1):
            dp_matrix[i][j] = dp_matrix[i-1][j]
            if (j >= v[i]):
                if dp_matrix[i][j] >= dp_matrix[i - 1][math.ceil(j - v[i])] + w[i]:
                    dp_matrix[i][j] = dp_matrix[i-1][j]
                    result_matrix[i][j] = result_matrix[i-1][j]
                else:
                    dp_matrix[i][j] = dp_matrix[i - 1][math.ceil(j - v[i])] + w[i]
                    if dp_matrix[i][j] > MAX_LOAD_WEIGHT:
                        dp_matrix[i][j] = dp_matrix[i-1][j]
                        result_matrix[i][j] = result_matrix[i - 1][j]
                    else:
                        result_matrix[i][j] = result_matrix[i - 1][j]
                        result_matrix[i][j] += str(i)
    return dp_matrix[i][j], result_matrix[i][j]


end = time.perf_counter()
print("knapsack_algorithm_rule", end-start)
