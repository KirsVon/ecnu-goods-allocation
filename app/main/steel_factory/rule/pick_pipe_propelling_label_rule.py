# -*- coding: utf-8 -*-
# Description: 标签提取规则
# Created: luchengkai 2020/11/24
import copy
from typing import List

import config
from app.main.steel_factory.dao.pick_pipe_propelling_dao import pick_pipe_propelling_dao
from app.main.steel_factory.rule import pick_data_format_rule, pick_propelling_label_rule
from app.util.rest_template import RestTemplate
from app.main.steel_factory.entity.pick_propelling import PickPropelling
from model_config import ModelConfig


def pick_pipe_label_extract(propelling_list: List[PickPropelling]):
    """
    标签提取
    标签提取总入口
    :param propelling_list:
    :return: wait_driver_list
    """

    propelling_list, assign_drivers_list = distinct_propelling(propelling_list)  # 区分是否是客户指定车队
    # 单车车队
    if propelling_list:
        propelling_list, total_count = pick_capacity(propelling_list)  # 多条件查询
        flag = True
    # 指定车队
    else:
        propelling_list, total_count = get_assign_drivers(assign_drivers_list)
        flag = False

    return propelling_list, total_count, flag


def pick_capacity(wait_propelling_list: List[PickPropelling]):
    """
    运力池
    调用数仓接口，获取6个月内3个区县的司机集
    :return: wait_driver_list
    """
    total_count = 0
    url = config.get_active_config().CAPACITY_SERVICE_URL + "/pipe_capacity"
    for propelling in wait_propelling_list:
        post_dic = pick_data_format_rule.to_capacity(propelling, propelling.dist_type)
        res = RestTemplate.do_post(url, post_dic)
        propelling.drivers.extend(pick_data_format_rule.from_capacity(propelling, res.get('data')))
        total_count += len(propelling.drivers)

    return wait_propelling_list, total_count


def distinct_propelling(propelling_list: List[PickPropelling]):
    """
    区分客户是否指定司机池
    :param propelling_list:
    :return: wait_driver_list
    """
    assign_drivers_list = [driver for driver in propelling_list if driver.is_assign_drivers == '1']
    propelling_list = [driver for driver in propelling_list if driver.is_assign_drivers != '1']
    return propelling_list, assign_drivers_list


def get_assign_drivers(propelling_list: List[PickPropelling]):
    """
    获取指定司机池
    :param propelling_list:
    :return: wait_driver_list
    """
    if not propelling_list:
        return [], 0

    total_count = 0
    for propelling in propelling_list:
        driver_list = pick_pipe_propelling_dao.get_assign_drivers(propelling.consignee_company_ids)
        propelling.drivers = driver_list
        total_count += len(driver_list)
    return propelling_list, total_count


if __name__ == '__main__':
    dicts = {
        "a": 1,
        "b": 2,
        "c": 3
    }
    a = dicts.keys()
    print(a)
