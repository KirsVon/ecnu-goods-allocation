# -*- coding: utf-8 -*-
# Description: 召回筛选规则
# Created: luchengkai 2020/11/24
import copy
from typing import List, Dict
import pandas as pd
import datetime

from geopy import distance
from app.main.steel_factory.dao.pick_propelling_dao import pick_propelling_dao
from app.main.steel_factory.dao.pick_propelling_filter_dao import pick_propelling_filter_dao
from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.main.steel_factory.entity.pick_propelling_driver import PickPropellingDriver
from app.main.steel_factory.rule import pick_data_format_rule, pick_normal_rule
from app.main.steel_factory.service.pick_propelling_redis_service import get_pick_propelling_driver_list
from app.main.steel_factory.service.pick_propelling_redis_service import set_pick_propelling_driver_list
from app.util.date_util import get_now_date
from model_config import ModelConfig


def pick_recall_screen(propelling_list: List[PickPropelling]):
    """
    召回筛选
    召回筛选总入口
    ①去重
    ②冷却期处理
    ③黑名单处理
    ④合并摘单计划和司机列表

    ⑤根据司机状态筛选
    ⑥司机当前距日钢距离
    ⑦活跃司机列表
    :return: driver_list
    """

    propelling_list = pick_driver_distinct(propelling_list)  # 去重
    # propelling_list = pick_black_list(propelling_list)  # 黑名单处理
    # propelling_driver_list = add_driver_to_propelling(propelling_list, driver_list)  # 合并

    propelling_list = pick_driver_condition_deal_weight(propelling_list)  # 根据司机状态筛选(重量)
    propelling_list = pick_kind_deal(propelling_list)  # 根据司机曾运品种筛除

    # 日钢优先处理
    propelling_list = pick_distance_deal(propelling_list)  # 司机当前距日钢距离

    propelling_list, current_count = screen_deal(propelling_list)  # 小条件筛除
    return propelling_list


def pick_driver_recall_screen(propelling_list: List[PickPropelling]):
    """
    新增摘单计划召回筛选
    :return: driver_list
    """
    propelling_list = pick_driver_distinct(propelling_list)  # 去重
    # propelling_driver_list = add_driver_to_propelling(propelling_list, driver_list)  # 合并
    propelling_list = pick_driver_condition_deal_weight(propelling_list)  # 根据司机状态筛选(重量)
    # propelling_driver_list = pick_active_deal(propelling_driver_list)  # 活跃司机添加
    # propelling_driver_list = pick_distance_deal(propelling_driver_list)  # 司机当前距日钢距离
    propelling_list = pick_kind_deal(propelling_list)  # 根据司机曾运品种筛除
    propelling_list, current_count = screen_deal(propelling_list)  # 小条件筛除
    return propelling_list, current_count


def pick_kind_deal(propelling_list):
    driver_kind_dict = pick_propelling_filter_dao.select_driver_kind()
    for propelling in propelling_list:
        propelling.drivers = [driver for driver in propelling.drivers if
                              propelling.prod_name in driver_kind_dict.get(driver.driver_id, "未知id")]
    return propelling_list


def screen_deal(propelling_list):
    current_count = 0
    for propelling in propelling_list:
        # 筛除已经收到摘单计划的司机
        pick_normal_rule.exist_driver_screen(propelling)

        # 对符合距离条件的司机赋值
        pick_normal_rule.distance_screen(propelling)

        # 筛出符合条件的司机：距离&活跃司机
        # 对除活跃司机外的司机按距离升序排序
        other_driver_list = copy.deepcopy([driver for driver in propelling.drivers
                                           if driver.is_in_distance == 1
                                           and driver.label_type != ModelConfig.PICK_LABEL_TYPE['L5']])
        other_driver_list.sort(key=lambda x: x.dist, reverse=False)
        # 将活跃司机直接加入司机列表
        propelling.drivers = [driver for driver in propelling.drivers if
                              driver.label_type == ModelConfig.PICK_LABEL_TYPE['L5']]
        propelling.drivers.extend(other_driver_list)

        # 司机数上限：remain_truck_num * ModelConfig.PICK_DRIVER_NUM_LIMIT
        propelling.drivers = propelling.drivers[0:propelling.wait_driver_count]
        current_count += len(propelling.drivers)

    return propelling_list, current_count


# def add_driver_to_propelling(wait_propelling_list: List[PickPropelling]):
#     """
#     将司机列表写入对应propelling的对象
#     :param wait_propelling_list:
#     :return:
#     """
#
#     # 将司机列表并入propelling
#     for wait_propelling in wait_propelling_list:
#         # 将司机拼接到driver_list后
#         try:
#             wait_propelling.total_weight = float(wait_propelling.total_weight)
#         except Exception as e:
#             wait_propelling.total_weight = 0
#             pass
#         try:
#             wait_propelling.remain_total_weight = float(wait_propelling.remain_total_weight)
#         except Exception as e:
#             wait_propelling.remain_total_weight = 0
#             pass
#         # 根据driver_id去重
#         # 取driver_list中的driver_id列表
#         driver_id_list = [driver.driver_id for driver in wait_propelling.drivers]
#         driver_list = [driver for driver in driver_list if driver.driver_id not in driver_id_list]
#         wait_propelling.drivers.extend(driver_list)
#     return wait_propelling_list


# def pick_active_deal(wait_propelling_list):
#     """
#     将活跃司机列表并入propelling
#     :param wait_propelling_list:
#     :return:
#     """
#     # 活跃司机集
#     active_list = pick_propelling_filter_dao.select_active_driver()
#     # 有任务司机id列表
#     have_work_driver_id_list = pick_propelling_filter_dao.select_have_work_driver()
#     for driver in active_list:
#         # driver.driver_name += "(扩)"
#         driver.label_type = ModelConfig.PICK_LABEL_TYPE['L5']
#         if not driver.district_name:
#             driver.district_name = "未知区县"
#         if not driver.city_name:
#             driver.city_name = "未知城市"
#
#     # 将活跃司机列表并入propelling
#     for wait_propelling in wait_propelling_list:
#
#         # # 待推荐司机数已符合要求
#         # if len(wait_propelling.drivers) >= wait_driver_count:
#         #     wait_propelling.drivers = wait_propelling.drivers[0: wait_driver_count]
#         #     continue
#
#         # propelling对应城市区县的活跃司机列表
#         tmp_list = [driver for driver in active_list if
#                     driver.city_name == wait_propelling.city_name and
#                     driver.district_name == wait_propelling.district_name]
#         # 取活跃司机
#         tmp_list = tmp_list[0: ModelConfig.PICK_ACTIVE_DRIVER_NUM.get(wait_propelling.district_name, 1)]
#         # 筛除已经收到摘单计划的司机
#         tmp_list = [item for item in tmp_list if
#                     item.driver_id not in wait_propelling.exist_driver_id_list]
#         # 筛除有任务的司机
#         tmp_list = copy.deepcopy([driver for driver in tmp_list if driver.driver_id not in have_work_driver_id_list])
#         if not tmp_list:
#             continue
#         # 将活跃司机插入wait_propelling.drivers
#         wait_propelling.drivers.extend(tmp_list)
#         # 若len(wait_propelling.drivers)的长度小于wait_driver_count，不截取
#         wait_propelling.drivers = wait_propelling.drivers[0: wait_propelling.wait_driver_count]
#         # for driver in wait_propelling.drivers:
#         #     driver.is_in_distance = 1
#
#         # # 推荐司机数达到上限
#         # if len(wait_propelling.drivers) >= wait_propelling.wait_driver_count:
#         #     wait_propelling.driver_is_fit = 1
#
#     return wait_propelling_list


def joint_active_driver(driver_list, active_list, wait_driver_count) -> Dict[str, List]:
    """
    将data_list按照attr_list属性list分组
    :param driver_list: 当前司机集
    :param active_list: 活跃司机集
    :param wait_driver_count: 待推送的司机上限
    :return:
    """
    # 根据driver_id去重
    # 取driver_list中的driver_id列表
    driver_id_list = [driver.driver_id for driver in driver_list]
    active_filter_list = [driver for driver in active_list if driver.driver_id not in driver_id_list]
    # 取前15%的活跃司机
    active_num = int(len(active_filter_list) * 0.15)
    active_filter_list = active_filter_list[0: active_num]

    tmp_driver_list = driver_list
    tmp_driver_list.extend(active_filter_list)
    # 若len(tmp_driver_list)的长度小于wait_driver_count，不截取
    result_list = tmp_driver_list[0: int(min(wait_driver_count, len(tmp_driver_list)))]
    return result_list


def pick_driver_distinct(propelling_list: List[PickPropelling]):
    """
    去重
    根据摘单号筛除重复司机
    :return: result_driver_list
    """
    for propelling in propelling_list:
        # 筛除重复司机后的司机列表
        result_driver_list = []
        driver_dict = pick_normal_rule.split_group(propelling.drivers, ["driver_id"])
        # 记录存入redis的时间
        # redis_date_time = get_now_date()
        #
        for key in driver_dict.keys():
            driver = driver_dict[key][0]
            # driver.redis_date_time = redis_date_time
            result_driver_list.append(driver)
        propelling.drivers = result_driver_list
    return propelling_list


def pick_driver_condition_deal_weight(propelling_driver_list: List[PickPropelling]):
    """
    根据司机状态筛选司机集
    ①筛除重量超限的司机
    ②最多推送 remain_truck_num * 3 数量的司机
    :return: result_driver_list
    """
    # 筛除有任务且重量超限的司机
    # 获取司机调度单的重量信息
    driver_weight_dict = pick_propelling_dao.select_driver_weight()
    for propelling in propelling_driver_list:
        # 重量未超限的司机
        propelling.drivers = [item for item in propelling.drivers if
                              item.driver_id not in driver_weight_dict.keys()
                              or (driver_weight_dict.get(item.driver_id, 0.0) + propelling.single_weight <=
                                  ModelConfig.PICK_TOTAL_WEIGHT)]
    return propelling_driver_list


# def pick_black_list(driver_list: List[PickPropelling]):
#     """
#     黑名单处理
#     根据黑名单筛选司机集
#     :return: driver_list
#     """
#     # 从blacklist中获取在黑名单的司机列表
#     black_driver_list = pick_propelling_dao.select_black_list()
#
#     # 过滤司机集
#     if not black_driver_list:
#         return driver_list
#
#     for black_driver in black_driver_list:
#         driver_list = [item for item in driver_list if black_driver.driver_id != item.driver_id or
#                        black_driver.prod_name != item.pickup_prod_name or
#                        black_driver.district_name != item.district_name]
#
#     return driver_list


def pick_distance_deal(propelling_driver_list: List[PickPropelling]):
    """
    司机当前距日钢距离
    距日钢越近，越容易获取摘单消息
    ①通过app查询司机位置
    ②通过中交兴路轨迹数据查询车辆位置
    :param propelling_driver_list:
    """
    if not propelling_driver_list:
        return propelling_driver_list
    # 遍历摘单
    for propelling in propelling_driver_list:
        # 司机id列表
        driver_id_list = [driver.driver_id for driver in propelling.drivers]
        """通过app查询司机位置"""
        driver_location_dict = pick_propelling_filter_dao.select_driver_location(driver_id_list)
        # 查询司机对应的车牌号列表
        driver_truck_dict = pick_propelling_dao.select_driver_truck(driver_id_list)
        vehicle_no_for_zjxl_list = []
        for vehicle_no_list in driver_truck_dict.values():
            vehicle_no_for_zjxl_list.extend(vehicle_no_list)
        # 查询车辆位置信息
        truck_location_dict = pick_propelling_dao.select_lat_and_lon_by_vehicle_no(vehicle_no_for_zjxl_list)
        # 日钢位置：纬度、经度
        rg_tuple = (ModelConfig.PICK_RG_LAT.get("日钢纬度"), ModelConfig.PICK_RG_LON.get("日钢经度"))
        # 遍历司机列表
        for driver in propelling.drivers:
            # 如果有app位置
            lat, lon = driver_location_dict.get(driver.driver_id, [None, None])
            if lat and lon:
                # 司机位置：纬度、经度
                driver_tuple = (lat, lon)
                # 计算距离：千米
                dist = distance.great_circle(driver_tuple, rg_tuple).km
                driver.app_latitude = lat
                driver.app_longitude = lon
                driver.latitude = lat
                driver.longitude = lon
                driver.app_dist = dist
                driver.dist = dist
            # 给司机的车牌号列表赋值
            driver.vehicle_no_list = driver_truck_dict.get(driver.driver_id, [])
            # 司机的车牌号为空
            if not driver.vehicle_no_list:
                continue
            # 遍历此司机所有的车辆，选出最近的一台车的位置
            target_lat = 0
            target_lon = 0
            target_dist = 9999
            target_vehicle_no = None
            for inner_vehicle_no in driver.vehicle_no_list:
                lat, lon = truck_location_dict.get(inner_vehicle_no, [None, None])
                if lat and lon:
                    # 计算车的距离
                    truck_dist = distance.great_circle((lat, lon), rg_tuple).km
                    if truck_dist < target_dist:
                        target_lat = lat
                        target_lon = lon
                        target_dist = truck_dist
                        target_vehicle_no = inner_vehicle_no
            driver.truck_latitude = target_lat
            driver.truck_longitude = target_lon
            driver.vehicle_no = target_vehicle_no
            driver.truck_dist = target_dist
            # 取app和车的位置中最近的一个
            if driver.truck_dist < driver.dist:
                driver.latitude = driver.truck_latitude
                driver.longitude = driver.truck_longitude
                driver.dist = driver.truck_dist
        # 按距离升序排序
        propelling.drivers.sort(key=lambda x: x.dist, reverse=False)
        # 筛除已经收到摘单计划的司机
        pick_normal_rule.exist_driver_screen(propelling)
        # 筛出距离符合条件的司机
        pick_normal_rule.distance_screen(propelling)
    return propelling_driver_list


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
