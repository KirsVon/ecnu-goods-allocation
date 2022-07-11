# -*- coding: utf-8 -*-
# Description: 摘单推荐服务通用方法类
# Created: luchengkai 2020/11/16
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import datetime

from app.main.steel_factory.entity.pick_propelling_driver import PickPropellingDriver
from app.main.steel_factory.service.pick_propelling_redis_service import get_pick_propelling_driver_list
from app.main.steel_factory.service.pick_propelling_redis_service import set_pick_propelling_driver_list
from app.util.date_util import get_now_date
from model_config import ModelConfig


def split_group(data_list, attr_list) -> Dict[str, List]:
    """
    将data_list按照attr_list属性list分组
    :param attr_list:
    :param data_list:
    :return:
    """
    # 结果字典：{‘attr_list’：[分组列表]}
    result_dict = defaultdict(list)
    for data in data_list:
        key = getattr(data, attr_list[0], '未知参数')
        for i in range(1, len(attr_list)):
            key = key + ', ' + getattr(data, attr_list[i], '未知参数')
        result_dict[key].append(data)
    return result_dict


def distance_screen(propelling):
    """
    根据dist筛选符合条件的司机
    :param propelling:
    :return:
    """
    # 筛出距离符合条件的司机
    for driver in propelling.drivers:
        # 如果距离符合条件
        if driver.dist <= propelling.dist_type:
            driver.is_in_distance = 1


def exist_driver_screen(propelling):
    """
    筛除已经收到摘单计划的司机
    :param propelling:
    :return:
    """
    propelling.drivers = [item for item in propelling.drivers if item.driver_id not in
                          propelling.exist_driver_id_list]


def get_path(static_name):
    cur_path = os.path.abspath(os.path.dirname(__file__))
    # print("cur",cur_path)
    root_path = cur_path[:cur_path.find("app") + len("app")]
    # print("root",root_path)
    # print(os.path.abspath(root_path + 'static/' + static_name))
    # return os.path.abspath(root_path + static_name)
    return Path(root_path + static_name).resolve()


def pick_cd_deal(driver_list: List[PickPropellingDriver]):
    """
    冷却期处理
    根据冷却期筛选司机集
    :return: driver_list
    """
    # 从redis中获取司机列表信息
    redis_driver_dict = get_pick_propelling_driver_list()
    redis_driver_list: List[PickPropellingDriver] = [PickPropellingDriver(driver) for driver in redis_driver_dict]
    # 如果redis为空
    if not redis_driver_list:
        # 放回redis
        driver_dict = [driver.as_dict() for driver in driver_list]
        set_pick_propelling_driver_list(driver_dict)
        return driver_list
    # 找出还在冷却期内的司机列表
    redis_driver_id_list = [driver.driver_id for driver in redis_driver_list
                            if driver.redis_date_time >= str((get_now_date() -
                                                              datetime.timedelta(
                                                                  hours=ModelConfig.PICK_PROPELLING_COLD_HOUR)))]
    # 如果没有冷却期内的司机
    if not redis_driver_id_list:
        # 放回redis
        driver_dict = [driver.as_dict() for driver in driver_list]
        set_pick_propelling_driver_list(driver_dict)
        return driver_list
    # 从driver_list中筛除掉还在冷却期内的司机
    driver_list = [driver for driver in driver_list if driver.driver_id not in redis_driver_id_list]
    driver_id_list = [driver.driver_id for driver in driver_list]
    # 找出在冷却期内、但不在driver_list中的司机
    temp_driver_list = [driver for driver in redis_driver_list if driver.driver_id not in driver_id_list]
    # 放回redis
    driver_dict = [driver.as_dict() for driver in driver_list + temp_driver_list]
    set_pick_propelling_driver_list(driver_dict)
    return driver_list

