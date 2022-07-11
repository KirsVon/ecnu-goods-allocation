# -*- coding: utf-8 -*-
# Description: 从数据表中获取模型参数配置
# Created: jjunf 2021/3/22 10:40
from collections import defaultdict
from typing import List
from flask import current_app, json
from app.main.steel_factory.entity.pick_model_config import PickModelConfig
from app.util.split_group_util import split_group_util


def get_model_config_service():
    """
    从数据表中获取模型参数配置
    :return:
    """
    # 所有的参数配置
    model_config = {}
    # 查询参数
    model_config_list = []
    # 模型配置参数名称（参数名称：项目配置文件model_config中的变量名）分组
    model_config_dict = split_group_util(model_config_list, ['config_name'])

    '''使用表中配置的标记：1使用表中的配置；0：使用配置文件model_config中的默认配置'''
    flag_list: List[PickModelConfig] = model_config_dict.get('FLAG', [])
    if flag_list:
        # 获取flag的值
        model_config['FLAG'] = flag_list[0].int_1

    '''各城市的发运量限制：字典：{城市：[给运营预留的派单重量,摘单和派单的重量上限]}（单位：吨）'''
    weight_limit_list: List[PickModelConfig] = model_config_dict.get('CITY_DISPATCH_WEIGHT_LIMIT_DICT', [])
    weight_limit_dict = defaultdict(list)
    if weight_limit_list:
        for weight_limit in weight_limit_list:
            # 城市
            weight_limit_city = weight_limit.str_1
            # 重量下限
            weight_limit_low = weight_limit.int_1 if weight_limit.int_1 else 0
            # 重量上限
            weight_limit_up = weight_limit.int_2 if weight_limit.int_2 else 9999
            #
            weight_limit_dict[weight_limit_city].append(weight_limit_low)
            weight_limit_dict[weight_limit_city].append(weight_limit_up)
    model_config['CITY_DISPATCH_WEIGHT_LIMIT_DICT'] = weight_limit_dict

    '''每条摘单计划的最大车次数限制'''
    truck_num_limit_list: List[PickModelConfig] = model_config_dict.get('PICK_TRUCK_NUM_UP_LIMIT', [])
    if truck_num_limit_list:
        # 获取车次数限制值
        model_config['PICK_TRUCK_NUM_UP_LIMIT'] = truck_num_limit_list[0].int_1

    '''相同客户配置'''
    consumer_list: List[PickModelConfig] = model_config_dict.get('CONSUMER_DICT', [])
    if consumer_list:
        # 客户字典
        consumer_dict = {}
        # 获取相同客户配置
        for consumer in consumer_list:
            consumer_dict[consumer.str_1] = consumer.str_2
        model_config['CONSUMER_DICT'] = consumer_dict

    '''厂区仓库配置'''
    warehouse_list: List[PickModelConfig] = model_config_dict.get('RG_WAREHOUSE_GROUP', [])
    if warehouse_list:
        warehouse_dict = {}
        for warehouse in warehouse_list:
            warehouse_dict[warehouse.str_1] = warehouse.str_2.split(',')
        model_config['RG_WAREHOUSE_GROUP'] = warehouse_dict

    '''调度人员联系方式'''
    dispatcher_phone_list: List[PickModelConfig] = model_config_dict.get('DISPATCHER_PHONE_DICT', [])
    if dispatcher_phone_list:
        # 联系方式字典
        dispatcher_phone_dict = {}
        for dispatcher_phone in dispatcher_phone_list:
            # 如果需要加上我们的联系方式，则将我们的联系方式放在前面
            if dispatcher_phone.str_3:
                phone = dispatcher_phone.str_3 + '/' + dispatcher_phone.str_2
            else:
                phone = dispatcher_phone.str_2
            dispatcher_phone_dict[dispatcher_phone.str_1] = phone
        model_config['DISPATCHER_PHONE_DICT'] = dispatcher_phone_dict

    '''载重上限'''
    max_weight_list: List[PickModelConfig] = model_config_dict.get('RG_MAX_WEIGHT', [])
    if max_weight_list:
        model_config['RG_MAX_WEIGHT'] = max_weight_list[0].int_1

    '''载重下限'''
    min_weight_list: List[PickModelConfig] = model_config_dict.get('RG_MIN_WEIGHT', [])
    if min_weight_list:
        model_config['RG_MIN_WEIGHT'] = min_weight_list[0].int_1

    '''使用遗传算法的标志'''
    ga_use_flag_list: List[PickModelConfig] = model_config_dict.get('GA_USE_FLAG', [])
    if ga_use_flag_list:
        model_config['GA_USE_FLAG'] = ga_use_flag_list[0].int_1

    '''使用遗传算法的结果作为输出的标志'''
    ga_use_result_flag_list: List[PickModelConfig] = model_config_dict.get('GA_USE_RESULT_FLAG', [])
    if ga_use_result_flag_list:
        model_config['GA_USE_RESULT_FLAG'] = ga_use_result_flag_list[0].int_1

    '''遗传中迭代的次数、交叉的次数'''
    ga_param_list: List[PickModelConfig] = model_config_dict.get('GA_PARAM', [])
    if ga_param_list:
        model_config['GA_PARAM'] = [ga_param_list[0].int_1, ga_param_list[0].int_2]

    '''遗传算法中车次数减少1的价值、尾货的价值'''
    ga_fitness_value_param_list: List[PickModelConfig] = model_config_dict.get('GA_FITNESS_VALUE_PARAM', [])
    if ga_fitness_value_param_list:
        model_config['GA_FITNESS_VALUE_PARAM'] = [ga_fitness_value_param_list[0].int_1,
                                                  ga_fitness_value_param_list[0].int_2]

    '''遗传算法中卸点客户的价值'''
    ga_fitness_value_consumer_list: List[PickModelConfig] = model_config_dict.get('GA_FITNESS_VALUE_CONSUMER', [])
    if ga_fitness_value_consumer_list:
        model_config['GA_FITNESS_VALUE_CONSUMER'] = [ga_fitness_value_consumer_list[0].int_1,
                                                     ga_fitness_value_consumer_list[0].int_2,
                                                     ga_fitness_value_consumer_list[0].int_3]

    '''遗传算法中装点仓库的价值'''
    ga_fitness_value_deliware_list: List[PickModelConfig] = model_config_dict.get('GA_FITNESS_VALUE_DELIWARE', [])
    if ga_fitness_value_deliware_list:
        model_config['GA_FITNESS_VALUE_DELIWARE'] = [ga_fitness_value_deliware_list[0].int_1,
                                                     ga_fitness_value_deliware_list[0].int_2,
                                                     ga_fitness_value_deliware_list[0].int_3]

    '''遗传算法中装点厂区的价值'''
    ga_fitness_value_factory_list: List[PickModelConfig] = model_config_dict.get('GA_FITNESS_VALUE_FACTORY', [])
    if ga_fitness_value_factory_list:
        model_config['GA_FITNESS_VALUE_FACTORY'] = [ga_fitness_value_factory_list[0].int_1,
                                                    ga_fitness_value_factory_list[0].int_2,
                                                    ga_fitness_value_factory_list[0].int_3]

    # 打印参数配置日志
    current_app.logger.info('数仓中模型配置：' + json.dumps(model_config, ensure_ascii=False))
    return model_config
