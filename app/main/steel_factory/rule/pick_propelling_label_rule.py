# -*- coding: utf-8 -*-
# Description: 标签提取规则
# Created: luchengkai 2020/11/24
import copy
import os
from typing import List

import pandas as pd
from celery.utils.log import get_task_logger

import config
from app.main.steel_factory.dao.pick_propelling_filter_dao import pick_propelling_filter_dao
from app.main.steel_factory.dao.pick_propelling_label_dao import pick_label_dao
from app.main.steel_factory.rule import pick_normal_rule, pick_data_format_rule, pick_propelling_recall_screen_rule
from app.util.rest_template import RestTemplate
from app.main.steel_factory.entity.pick_propelling import PickPropelling
from model_config import ModelConfig
from app.util.model_trainer.transformer import TransformerGRU

# 获取celery执行器的日志记录器
logger = get_task_logger('celery_worker')


def pick_label_extract_new(propelling_list: List[PickPropelling], select_type):
    """
    标签提取
    标签提取总入口
    :param propelling_list:
    :param select_type:
    :return: wait_driver_list
    """
    if select_type == ModelConfig.PICK_SELECT_TYPE[3]:
        propelling_list = pick_cold_start(propelling_list, True)
    propelling_list = pick_active_deal(propelling_list)  # 活跃司机添加
    propelling_list = pick_propelling_recall_screen_rule.pick_distance_deal(propelling_list)  # 司机当前距日钢距离
    propelling_list, total_count = pick_capacity(propelling_list, select_type)  # 运力池
    propelling_list = label_deal(propelling_list)  # 将品名和摘单开始时间赋值给司机
    return propelling_list, total_count


def pick_label_extract(propelling_list: List[PickPropelling]):
    """
    标签提取
    标签提取总入口
    :param propelling_list:
    :return: wait_driver_list
    """
    # wait_driver_list.extend(pick_transport_poll(wait_propelling_list))  # 运力池
    propelling_list = pick_active_deal(propelling_list)  # 活跃司机添加
    propelling_list = pick_propelling_recall_screen_rule.pick_distance_deal(propelling_list)  # 司机当前距日钢距离
    propelling_list, driver_count = pick_capacity(propelling_list, ModelConfig.PICK_SELECT_TYPE[0])  # 多条件查询
    propelling_list = pick_cold_start(propelling_list)  # 冷启动
    propelling_list = pick_normal_flow(propelling_list)  # 常运流向
    propelling_list = pick_normal_product(propelling_list)  # 常运品种
    propelling_list = pick_preference(propelling_list)  # 新增司机响应概率

    propelling_list = label_deal(propelling_list)  # 将品名和摘单开始时间赋值给司机
    return propelling_list


def pick_preference(propelling_list: List[PickPropelling]):
    try:
        order_list = []
        for propelling in propelling_list:
            if propelling.dist_type == ModelConfig.PICK_RESULT_TYPE.get('DEFAULT'):
                order_dict = {'pickup_no': propelling.pickup_no,
                              'queries': (propelling.district_name + ' ' +
                                          propelling.consignee_company_ids + ' ' + propelling.prod_name)}
                order_list.append(order_dict)

        propelling_list = model_infer(propelling_list, order_list, top_k=100, threshold=0.005)
        return propelling_list
    except Exception as e:
        logger.error('pick_preference报错: ' + str(e))
        return propelling_list


def model_infer(propelling_list, queries, top_k=1, threshold=0.):
    if not queries:
        return propelling_list

    # 数据集获取
    truck_map_dict = {}
    path = os.path.abspath('.') + "/app/util/model_trainer/truck_dict.csv"
    truck_dict = pd.read_csv(path, encoding='UTF-8')
    truck_dict_t = truck_dict.T
    truck_dict = truck_dict.to_dict()
    i = 0
    truck_no_list = []
    for key in truck_dict.keys():
        truck_map_dict[i] = key
        truck_no_list.append(key)
        i += 1

    path = os.path.abspath('.') + "/app/util/model_trainer/emb_dict.csv"
    emb_dict = pd.read_csv(path, encoding='UTF-8').to_dict()
    for key in emb_dict.keys():
        tmp_list = str(emb_dict[key].values()).lstrip('dict_values([').rstrip(')]').split(', ')
        tmp_list = [float(tmp) for tmp in tmp_list]
        emb_dict[key] = tmp_list

    # 格式转换
    query_set = []
    for data in queries:
        que = data['queries'].split(' ')
        query_set.append(que)

    # 向量字典获取
    word_dict = {}
    vec_set = []
    i = 0
    for key in emb_dict:
        word_dict[key] = i
        vec_set.append(emb_dict[key])  # vec_set.append(embedding_dict[key][0])
        i += 1

    # 模型计算
    model = TransformerGRU(q_set=query_set, t_set=truck_dict_t, dict_set=word_dict, vec_set=vec_set, is_train=False)
    model.init_model_parameters()
    model.generate_data_set()
    model.build_graph_by_cpu()
    model.start_session()
    result_prob_list, result_id_list = model.inference(top_k)

    # 格式转换
    answer_id_list = []
    answer_score_list = []
    for i in range(len(result_id_list)):
        tmp_id_list = result_id_list[i].tolist()
        tmp_score_list = result_prob_list[i].tolist()
        answer_id_list.append(tmp_id_list)
        answer_score_list.append(tmp_score_list)

    result_dict = {}
    for i in range(len(queries)):
        tmp_score_dict = {}
        for j in range(len(answer_id_list[i])):
            tmp_score_dict[truck_map_dict[answer_id_list[i][j]]] = answer_score_list[i][j]
        result_dict[queries[i]['pickup_no']] = tmp_score_dict

    # 获取车牌对应司机信息
    driver_list = pick_label_dao.select_truck_driver(truck_no_list)
    for propelling in propelling_list:
        tmp_driver_list = copy.deepcopy(driver_list)
        tmp_driver_list = [driver for driver in tmp_driver_list
                           if driver.driver_id not in propelling.exist_driver_id_list]
        for tmp_driver in tmp_driver_list:
            tmp_driver.response_probability = result_dict.get(propelling.pickup_no, {}).get(tmp_driver.vehicle_no, 0.0)
        tmp_driver_list = [driver for driver in tmp_driver_list
                           if driver.response_probability > 0.3]
        propelling.drivers.extend(tmp_driver_list)
    return propelling_list


def pick_capacity(wait_propelling_list: List[PickPropelling], select_type=None):
    """
    运力池
    调用数仓接口，获取6个月内3个区县的司机集
    :return: wait_driver_list
    """
    total_count = 0
    url = config.get_active_config().CAPACITY_SERVICE_URL + "/capacity"
    for propelling in wait_propelling_list:
        total_count += len(propelling.drivers)
        if propelling.dist_type == ModelConfig.PICK_RESULT_TYPE['DEFAULT']:
            select_type = ModelConfig.PICK_SELECT_TYPE[4]
        post_dic = pick_data_format_rule.to_capacity(propelling, propelling.dist_type, select_type)
        res = RestTemplate.do_post(url, post_dic)
        propelling.drivers.extend(pick_data_format_rule.from_capacity(propelling, res.get('data')))
        total_count += res.get('data').get('driver_count', 0)

    return wait_propelling_list, total_count


def pick_active_deal(wait_propelling_list):
    """
    将活跃司机列表并入propelling
    :param wait_propelling_list:
    :return:
    """
    # 活跃司机集
    active_list = pick_propelling_filter_dao.select_active_driver()
    for driver in active_list:
        # driver.driver_name += "(扩)"
        driver.label_type = ModelConfig.PICK_LABEL_TYPE['L5']
        # if not driver.district_name:
        #     driver.district_name = "未知区县"
        # if not driver.city_name:
        #     driver.city_name = "未知城市"

    # 将活跃司机列表并入propelling
    for wait_propelling in wait_propelling_list:

        # # 待推荐司机数已符合要求
        # if len(wait_propelling.drivers) >= wait_driver_count:
        #     wait_propelling.drivers = wait_propelling.drivers[0: wait_driver_count]
        #     continue

        # propelling对应城市区县的活跃司机列表
        tmp_list = [driver for driver in active_list if
                    driver.city_name == wait_propelling.city_name and
                    driver.district_name == wait_propelling.district_name]
        # 取活跃司机
        tmp_list = tmp_list[0: ModelConfig.PICK_ACTIVE_DRIVER_NUM.get(wait_propelling.district_name, 1)]
        if not tmp_list:
            wait_propelling.drivers = []
        else:
            wait_propelling.drivers = copy.deepcopy(tmp_list)
            # 筛除已经收到摘单计划的司机
            pick_normal_rule.exist_driver_screen(wait_propelling)

    # 筛除有任务且超重的司机
    pick_propelling_recall_screen_rule.pick_driver_condition_deal_weight(wait_propelling_list)
    # 根据司机曾运品种筛除
    pick_propelling_recall_screen_rule.pick_kind_deal(wait_propelling_list)

    for wait_propelling in wait_propelling_list:
        # 若len(wait_propelling.drivers)的长度小于wait_driver_count，不截取
        wait_propelling.drivers = wait_propelling.drivers[0: wait_propelling.wait_driver_count]

    return wait_propelling_list


# def pick_transport_poll(wait_propelling_list: List[PickPropelling]):
#     """
#     运力池
#     调用数仓接口，获取6个月内3个区县的司机集
#     :return: wait_driver_list
#     """
#     result_list = []
#     url = config.get_active_config().DATA_WAREHOUSE_URL + "/DelegatedDispatching/getListDistrictDriver"
#     for propelling in wait_propelling_list:
#         post_dic = pick_data_format_rule.data_format_to_java(propelling, 6)
#         res = RestTemplate.do_post(url, post_dic)
#         result_list.extend(pick_data_format_rule.data_format_from_java(propelling, res.get('data')))
#
#     return result_list


def pick_cold_start(wait_propelling_list: List[PickPropelling], select_type=None):
    """
    冷启动
    根据摘单列表中的流向信息获取适合推送的新司机
    :param wait_propelling_list: {city:[PickPropelling_entity]}
    :param select_type
    :return: wait_driver_list
    """
    # 获取新司机表格
    new_driver_list = pick_label_dao.select_new_driver()
    for new_driver in new_driver_list:
        new_driver.label_type = ModelConfig.PICK_LABEL_TYPE['L2']
        if select_type is True:
            new_driver.is_in_distance = 1

    # 判断是否有符合摘单要求的司机
    for propelling in wait_propelling_list:
        propelling.drivers.extend(copy.deepcopy(new_driver_list))

    return wait_propelling_list


def pick_normal_flow(wait_propelling_list: List[PickPropelling]):
    """
    常运流向
    根据摘单列表中的流向信息获取常运流向司机列表
    :return: wait_driver_list
    """
    # 查询司机常运流向
    tmp_driver_list = pick_label_dao.select_user_common_flow()
    if not tmp_driver_list:
        return wait_propelling_list
    # 根据城市分组
    driver_dict = pick_normal_rule.split_group(tmp_driver_list, ['city_name'])
    # 循环摘单列表
    for propelling in wait_propelling_list:
        if propelling.dist_type == ModelConfig.PICK_RESULT_TYPE.get('DEFAULT'):
            # 根据摘单城市获取司机
            temp_driver_list = driver_dict.get(propelling.city_name, [])
            for driver in temp_driver_list:
                driver.pickup_no = propelling.pickup_no
                driver.label_type = ModelConfig.PICK_LABEL_TYPE['L3']
            propelling.drivers.extend(temp_driver_list)
    return wait_propelling_list


def pick_normal_product(wait_propelling_list: List[PickPropelling]):
    """
    常运品种
    根据摘单列表中的品种信息获取常运品种司机列表
    :return: wait_driver_list
    """
    # 根据品名分组
    propelling_dict = pick_normal_rule.split_group(wait_propelling_list, ['prod_name'])
    values = propelling_dict.keys()
    # 查询司机常运品种,并根据品种分组
    tmp_driver_list = pick_label_dao.select_user_common_kind(values)
    if not tmp_driver_list:
        return wait_propelling_list
    driver_dict = pick_normal_rule.split_group(tmp_driver_list, ['prod_name'])
    # 循环摘单列表
    for propelling in wait_propelling_list:
        if propelling.dist_type == ModelConfig.PICK_RESULT_TYPE.get('DEFAULT'):
            # 根据摘单城市获取司机
            temp_driver_list = driver_dict.get(propelling.prod_name, [])
            for driver in temp_driver_list:
                driver.pickup_no = propelling.pickup_no
                # driver.driver_name = driver.driver_name + '(扩)'
                driver.label_type = ModelConfig.PICK_LABEL_TYPE['L4']
            propelling.drivers.extend(temp_driver_list)
    return wait_propelling_list


def label_deal(propelling_list):
    """
    将品名和摘单开始时间赋值给司机
    :return: wait_driver_list
    """
    propelling_dict = pick_normal_rule.split_group(propelling_list, ["pickup_no"])
    for propelling in propelling_list:
        for driver in propelling.drivers:
            driver.pickup_prod_name = propelling_dict.get(driver.pickup_no, [PickPropelling()])[0].prod_name
            driver.pickup_start_time = propelling_dict.get(driver.pickup_no, [PickPropelling()])[0].pickup_start_time
    return propelling_list


if __name__ == '__main__':
    dicts = {
        "a": 1,
        "b": 2,
        "c": 3
    }
    a = dicts.keys()
    print(a)
