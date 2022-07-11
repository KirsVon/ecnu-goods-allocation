# -*- coding: utf-8 -*-
# Description: 
# Created: jjunf 2021/3/18 10:49
from typing import List

from flask import current_app, json

from app.main.steel_factory.dao.pick_plan_dao import pick_plan_dao
from app.main.steel_factory.entity.plan import Plan
from app.main.steel_factory.entity.remain_check import RemainCheck
from app.util.split_group_util import split_group_util


def check_filter(remain_check: RemainCheck):
    """
    摘单时判断剩余车次数
    :param remain_check:
    :return:
    """
    # 未开单有效调度单
    plan_list: List[Plan] = pick_plan_dao.get_plan()
    # 按城市、区县筛选
    plan_list: List[Plan] = [plan for plan in plan_list
                             if plan.city == remain_check.city and plan.district == remain_check.district]
    # 日志记录
    current_app.logger.info(remain_check.city + remain_check.district + '的摘单未开单明细' + str(len(plan_list)) + '条：'
                            + json.dumps([i.as_dict() for i in plan_list], ensure_ascii=False))
    # 将该条摘单计划的品种用,分隔，得到品种列表
    commodity_list = remain_check.big_commodity_name.split(',')
    # 如果不跨厂区
    if len(commodity_list) == 1:
        # 筛选出该城市该区县该品种已经发了多少车
        plan_list: List[Plan] = [plan for plan in plan_list if
                                 plan.big_commodity_name == remain_check.big_commodity_name]
        # 该条计划的总车次>已发车次
        if remain_check.total_truck_num > len(plan_list):
            remain_check.result = True
    # 跨厂区的处理
    else:
        # 将plan_list按车次号分组
        plan_dict = split_group_util(plan_list, ['trains_no'])
        # 已发车次数
        send_truck_num = 0
        # 筛选出匹配到的跨厂区的
        for value_list in plan_dict.values():
            # 跨厂区个数相同的
            if len(value_list) == len(commodity_list):
                # 找出value_list中的品种
                value_commodity_list = [value.big_commodity_name for value in value_list]
                # 排序
                value_commodity_list.sort()
                commodity_list.sort()
                # 品种是否匹配的标记：True匹配，False不匹配
                flag = True
                # 判断品种是否匹配
                for i in range(len(commodity_list)):
                    if commodity_list[i] != value_commodity_list[i]:
                        flag = False
                # 如果匹配上，车次数+1
                if flag:
                    send_truck_num += 1
        # 该条计划的总车次>已发车次
        if remain_check.total_truck_num > send_truck_num:
            remain_check.result = True
    return remain_check
