# -*- coding: utf-8 -*-
# Description: 摘单计划扣除相关服务
# Created: jjunf 2021/02/04
import copy
from collections import defaultdict
from typing import List
from flask import current_app, json

from app.main.steel_factory.dao.pick_plan_dao import pick_plan_dao
from app.main.steel_factory.dao.pick_stock_dao import pick_stock_dao
from app.main.steel_factory.entity.deduct_stock import DeductStock
from app.main.steel_factory.entity.pick_task import PickTask
from app.main.steel_factory.entity.plan import Plan
from app.util.round_util import round_util, round_util_by_digit
from app.util.split_group_util import split_group_util
from model_config import ModelConfig


def deduct_from_pick_list(pick_list: List[PickTask]):
    """
    摘单计划扣除服务：未开单有效调度单扣除、青岛的货物车次数减半、各城市最大发运重量的限制以及派单量的预留
    :param pick_list:
    :return:
    """
    # 查询各城市当天有效的派单、摘单重量：字典：{城市：[派单重量,摘单和派单的总重量]}（单位：吨）
    send_weight_dict = pick_stock_dao.select_send_weight_all_city()
    # 日志
    current_app.logger.info('各城市今天有效的派单、摘单重量：' + json.dumps(send_weight_dict, ensure_ascii=False))
    # 未开单对应的调度单列表
    deduct_pick_list = []
    # 扣除
    if pick_list:
        '''未开单有效调度单扣除-start'''
        if ModelConfig.RG_STOCK_DEDUCT_FLAG:
            '''使用库存扣除方案2'''
            deduct_pick_list.extend(deduct_from_pick_list_way2(pick_list))
        else:
            # 未开单有效调度单
            plan_list: List[Plan] = pick_plan_dao.get_plan()
            current_app.logger.info('摘单未开单明细' + str(len(plan_list)) + '条：' +
                                    json.dumps([i.as_dict() for i in plan_list], ensure_ascii=False))
            plan_dict = split_group_util(plan_list, ['trains_no'])
            for key in plan_dict.keys():
                deduct_pick_list.extend(deduct_from_pick_list_way1(plan_dict[key], pick_list))
        '''未开单有效调度单扣除-end'''
        for pick_task in copy.copy(pick_list):
            # 如果上面扣除后摘单计划车次小于等于0，移除，不生成最后的摘单计划
            if pick_task.truck_num <= 0:
                pick_list.remove(pick_task)
                continue
            # 一车的重量
            single_truck_weight = float(round_util_by_digit(pick_task.total_weight / pick_task.truck_num, 3))
            # 城市
            city = pick_task.city
            '''青岛货物的特殊处理'''
            if city == '青岛市':
                '''将青岛的货物车次数减半-start'''
                # 减半后的车次数（4车变2车，5车变2车）
                half_truck_num = round_util((pick_task.truck_num - 1) / 2)
                pick_task.total_weight = half_truck_num * single_truck_weight
                pick_task.truck_num = half_truck_num
                # 如果车次小于等于0，移除，不生成最后的摘单计划
                if pick_task.truck_num <= 0:
                    pick_list.remove(pick_task)
                    continue
                # 更新pick_task子项item的车次数、总重量
                for item in pick_task.items:
                    # 注：这里必须先修改重量，再修改车次数，因为在修改重量的时候需要用到原来的车次数item.truck_num
                    item.total_weight = half_truck_num * float(
                        round_util_by_digit(item.total_weight / item.truck_num, 3))
                    item.truck_num = half_truck_num
                '''将青岛的货物车次数减半-end'''
            '''各城市的发运量限制'''
            # 如果该城市对发运量有限制
            if city in ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT.keys():
                '''给运营预留的派单重量限制'''
                # 如果当前运营已派单重量<需要给运营预留的派单重量
                if send_weight_dict[city][0] < ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT[city][0]:
                    # 判断需要再预留多少车
                    remain_truck_num = 0
                    while (remain_truck_num < pick_task.truck_num and send_weight_dict[city][0] + single_truck_weight <=
                           ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT[city][0]):
                        remain_truck_num += 1
                        # 更新send_weight_dict[city][0]
                        send_weight_dict[city][0] += single_truck_weight
                    # 更新pick_task的车次数、总重量
                    pick_task.truck_num -= remain_truck_num
                    pick_task.total_weight = pick_task.truck_num * single_truck_weight
                    # 如果车次小于等于0，移除，不生成最后的摘单计划
                    if pick_task.truck_num <= 0:
                        pick_list.remove(pick_task)
                        continue
                    # 更新pick_task子项item的车次数、总重量
                    for item in pick_task.items:
                        # 注：这里必须先修改重量，再修改车次数，因为在修改重量的时候需要用到原来的车次数item.truck_num
                        item.total_weight = (item.truck_num - remain_truck_num) * float(
                            round_util_by_digit(item.total_weight / item.truck_num, 3))
                        item.truck_num -= remain_truck_num
                '''最大发运重量的限制-start'''
                # 如果摘单和派单的总重量 + 1车的重量 > 最大发运重量的限制，则移除，不生成最后的摘单计划
                if (send_weight_dict[city][1] + single_truck_weight >
                        ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT[city][1]):
                    pick_list.remove(pick_task)
                    continue
                # 如果可以再加上整个pick_task的总重量
                elif (send_weight_dict[city][1] + pick_task.total_weight <=
                      ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT[city][1]):
                    # 更新send_weight_dict[city][1]
                    send_weight_dict[city][1] += pick_task.total_weight
                # 否则，判断还可以发多少车
                else:
                    truck_num = 0
                    while (truck_num < pick_task.truck_num and send_weight_dict[city][1] + single_truck_weight <=
                           ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT[city][1]):
                        truck_num += 1
                        # 更新send_weight_dict[city][1]
                        send_weight_dict[city][1] += single_truck_weight
                    # 更新pick_task的车次数、总重量
                    pick_task.truck_num = truck_num
                    pick_task.total_weight = round_util(truck_num * single_truck_weight)
                    # 更新pick_task子项item的车次数、总重量
                    for item in pick_task.items:
                        # 注：这里必须先修改重量，再修改车次数，因为在修改重量的时候需要用到原来的车次数item.truck_num
                        item.total_weight = round_util(
                            truck_num * float(round_util_by_digit(item.total_weight / item.truck_num, 3)))
                        item.truck_num = truck_num
                '''最大发运重量的限制-end'''
    return pick_list, deduct_pick_list


def deduct_from_pick_list_way1(plan: List, pick_list: List[PickTask]):
    """
    已调度未开单的扣除操作
    :param plan:
    :param pick_list:
    :return:
    """
    no_plan = []
    for pick in pick_list:
        if pick.truck_num <= 0:
            continue
        match_or_not = [pick_item for pick_item in pick.items if
                        pick_item.city == plan[0].city and
                        pick_item.end_point == plan[0].district and
                        pick_item.big_commodity == plan[0].big_commodity_name and
                        pick_item.truck_count == plan[0].plan_quantity]
        if match_or_not:
            # 排除 跨厂区 和 不跨厂区 匹配成功的情况
            if len(plan) == len(pick.items):
                for item in pick.items:
                    # 平均一车重量
                    weight = item.total_weight / item.truck_num
                    # 摘单计划明细车次数减一
                    item.truck_num -= 1
                    pick.total_weight -= item.total_weight
                    # 重新计算重量
                    item.total_weight = round_util(weight * item.truck_num)
                    # 重新计算摘单计划重量
                    pick.total_weight += item.total_weight
                no_plan.append(pick)
                # 摘单计划车次数减一
                pick.truck_num -= 1
                return no_plan
    for pick in pick_list:
        if pick.truck_num <= 0:
            continue
        match_or_not = [pick_item for pick_item in pick.items if
                        pick_item.city == plan[0].city and
                        pick_item.end_point == plan[0].district and
                        pick_item.big_commodity == plan[0].big_commodity_name]
        if match_or_not:
            # 排除 跨厂区 和 不跨厂区 匹配成功的情况
            if len(plan) == len(pick.items):
                for item in pick.items:
                    # 平均一车重量
                    weight = item.total_weight / item.truck_num
                    # 摘单计划明细车次数减一
                    item.truck_num -= 1
                    pick.total_weight -= item.total_weight
                    # 重新计算重量
                    item.total_weight = round_util(weight * item.truck_num)
                    # 重新计算摘单计划重量
                    pick.total_weight += item.total_weight
                no_plan.append(pick)
                # 摘单计划车次数减一
                pick.truck_num -= 1
                return no_plan
    return no_plan


def deduct_from_pick_list_way2(pick_list: List[PickTask]):
    """
    没有开单明细的库存、或者只有部分有开单明细库存的扣除，由于deduct_stock_list_without_detail是按订单明细查询的，所以要进行一下去重
    :param pick_list:
    :return:
    """
    # 最后要扣除的库存列表
    deduct_stock_list = []
    # 按照车次号、('新产品'、'老区')分组后的字典
    temp_deduct_stock_dict = defaultdict(list)
    for deduct_stock in ModelConfig.deduct_stock_list_without_detail:
        deduct_stock: DeductStock
        temp_deduct_stock_dict[str(deduct_stock.trains_no) + ',' +
                               str(deduct_stock.big_commodity_name).split('-')[0]].append(deduct_stock)
    # 只取其中的一条记录即可
    for value_list in temp_deduct_stock_dict.values():
        deduct_stock_list.append(value_list[0])
    # 需要被扣除的车次记录
    deduct_pick_list = []
    deduct_stock_dict = split_group_util(deduct_stock_list, ['trains_no'])
    for value_list in deduct_stock_dict.values():
        deduct_pick_list.extend(deduct_from_pick_list_way1(value_list, pick_list))
    return deduct_pick_list
