# -*- coding: utf-8 -*-
# Description: 召回筛选规则
# Created: luchengkai 2021/03/26
from typing import List
import pandas as pd
import datetime

from app.main.steel_factory.dao.pick_pipe_propelling_dao import pick_pipe_propelling_dao
from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.main.steel_factory.entity.pick_propelling_driver import PickPropellingDriver
from app.main.steel_factory.rule import pick_normal_rule
from app.util.date_util import get_now_date


def pick_pipe_screen(propelling_list: List[PickPropelling], flag):
    """
    召回筛选
    召回筛选总入口

    ①根据司机状态筛选
    :return: driver_list
    """
    # 根据司机状态筛选: 是否已收到摘单计划 & 是否在完成任务后一小时内
    propelling_list, current_count = pick_pipe_driver_condition_deal(propelling_list)
    # 根据司机数与剩余车次数筛选
    if flag:    # 表示是单车的单子
        propelling_list = pick_prod_truck_screen(propelling_list)

    return propelling_list, current_count


def pick_prod_truck_screen(propelling_list: List[PickPropelling]):
    """
    根据司机数与剩余车次数筛选
    如果 总车次 < 已推送司机数 + 待推送司机数，返回0
    :return: result_driver_list
    """
    for propelling in propelling_list:
        if propelling.total_truck_num < len(propelling.exist_driver_id_list) + len(propelling.drivers):
            propelling.drivers = []
    return propelling_list


def pick_pipe_driver_condition_deal(propelling_driver_list: List[PickPropelling]):
    """
    根据司机状态筛选司机集
    ①筛除已收到摘单计划的司机
    ②筛除完成任务的，出厂一小时以内的司机
    :return: result_driver_list
    """
    current_count = 0
    for propelling in propelling_driver_list:
        # 筛除已经收到摘单计划的司机
        pick_normal_rule.exist_driver_screen(propelling)
        # 筛除完成任务的，出厂一小时以内的司机/身上有任务的司机
        propelling.drivers = in_time_screen(propelling.drivers)
        current_count += len(propelling.drivers)
    return propelling_driver_list, current_count


def in_time_screen(drivers: List[PickPropellingDriver]):
    driver_id_list = pick_pipe_propelling_dao.select_no_work_in_time_driver_id()
    drivers = [item for item in drivers if item.driver_id not in driver_id_list]
    have_work_id_list = pick_pipe_propelling_dao.have_work_drivers()
    drivers = [item for item in drivers if item.driver_id not in have_work_id_list]
    return drivers


if __name__ == '__main__':
    a = get_now_date()
    b = a - datetime.timedelta(hours=6)
    print(a)
    print(b)

    data = pd.read_excel('driver.xls')
    df = pd.DataFrame(data)
    dic = df.to_dict(orient="record")
    driver_list22 = [PickPropellingDriver(obj) for obj in dic]
    # driver_list22 = pick_recall_screen(driver_list22)
