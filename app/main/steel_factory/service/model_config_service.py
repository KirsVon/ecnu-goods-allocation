# -*- coding: utf-8 -*-
# Description: 从数据表db_model.model_config中配置模型参数
# Created: jjunf 2021/5/21 12:48
from collections import defaultdict
from typing import List
from flask import current_app, json
from app.main.steel_factory.entity.model_config import ModelConfig
from app.util.split_group_util import split_group_util


def get_single_model_config_service():
    """
    从数据表中获取单车分货模型singleGoodsAllocation参数配置
    :return:
    """
    # 参数配置
    model_config = {}
    # 查询singleGoodsAllocation项目的参数
    model_config_list=[]
    # 模型配置参数名称（参数名称：项目配置文件model_config中的变量名）分组
    model_config_dict = split_group_util(model_config_list, ['config_name'])

    '''各仓库最大车辆容纳数'''   '''各仓库一般车辆容纳数'''
    warehouse_wait_dict_list: List[ModelConfig] = model_config_dict.get('WAREHOUSE_WAIT_DICT', [])
    if warehouse_wait_dict_list:
        # 各仓库最大车辆容纳数
        warehouse_wait_dict = defaultdict(list)
        # 各仓库一般车辆容纳数
        single_warehouse_wait_dict = {}
        for warehouse in warehouse_wait_dict_list:
            # 仓库名称
            warehouse_wait_dict["stock_name"].append(warehouse.str_1)
            # 仓库最大车辆容纳数
            warehouse_wait_dict["truck_count_std"].append(warehouse.int_1)
            # 各仓库一般车辆容纳数
            single_warehouse_wait_dict[warehouse.str_1] = warehouse.int_2 if warehouse.int_2 else 20
        model_config["WAREHOUSE_WAIT_DICT"] = warehouse_wait_dict
        model_config["SINGLE_WAREHOUSE_WAIT_DICT"] = single_warehouse_wait_dict

    '''超期清理的时间下限(小时)'''
    over_time_low_hour_list: List[ModelConfig] = model_config_dict.get('OVER_TIME_LOW_HOUR', [])
    if over_time_low_hour_list:
        model_config["OVER_TIME_LOW_HOUR"] = over_time_low_hour_list[0].int_1

    '''超期清理的时间上限(小时)'''
    over_time_up_hour_list: List[ModelConfig] = model_config_dict.get('OVER_TIME_UP_HOUR', [])
    if over_time_up_hour_list:
        model_config["OVER_TIME_UP_HOUR"] = over_time_up_hour_list[0].int_1

    '''拼货时各品种车上剩余最低重量限制（kg）'''
    compose_low_weight_list: List[ModelConfig] = model_config_dict.get('RG_COMMODITY_COMPOSE_LOW_WEIGHT', [])
    if compose_low_weight_list:
        compose_low_weight_dict = {}
        for compose_low_weight in compose_low_weight_list:
            compose_low_weight_dict[compose_low_weight.str_1] = compose_low_weight.int_1
        model_config["RG_COMMODITY_COMPOSE_LOW_WEIGHT"] = compose_low_weight_dict

    '''单车分货时最多匹配结果数量的一个阈值上限'''
    rg_single_compose_max_len_list: List[ModelConfig] = model_config_dict.get('RG_SINGLE_COMPOSE_MAX_LEN', [])
    if rg_single_compose_max_len_list:
        model_config["RG_SINGLE_COMPOSE_MAX_LEN"] = rg_single_compose_max_len_list[0].int_1

    '''单车分货中优先级的价值'''
    single_value_of_priority_list: List[ModelConfig] = model_config_dict.get('SINGLE_VALUE_OF_PRIORITY', [])
    if single_value_of_priority_list:
        model_config['SINGLE_VALUE_OF_PRIORITY'] = [single_value_of_priority_list[0].int_1,
                                                    single_value_of_priority_list[0].int_2]

    '''单车分货中卸点客户的价值'''
    single_value_of_consumer_list: List[ModelConfig] = model_config_dict.get('SINGLE_VALUE_OF_CONSUMER', [])
    if single_value_of_consumer_list:
        model_config['SINGLE_VALUE_OF_CONSUMER'] = [single_value_of_consumer_list[0].int_1,
                                                    single_value_of_consumer_list[0].int_2,
                                                    single_value_of_consumer_list[0].int_3]

    '''单车分货中装点仓库的价值'''
    single_value_of_deliware_list: List[ModelConfig] = model_config_dict.get('SINGLE_VALUE_OF_DELIWARE', [])
    if single_value_of_deliware_list:
        model_config['SINGLE_VALUE_OF_DELIWARE'] = [single_value_of_deliware_list[0].int_1,
                                                    single_value_of_deliware_list[0].int_2,
                                                    single_value_of_deliware_list[0].int_3]

    '''单车分货中装点仓库效率的价值:各仓库默认一般车辆容纳数、仓库作业效率放大的比例、联储仓库被扣减的价值'''
    single_value_of_deliware_efficiency_list: List[ModelConfig] = model_config_dict.get(
        'SINGLE_VALUE_OF_DELIWARE_EFFICIENCY', [])
    if single_value_of_deliware_efficiency_list:
        model_config['SINGLE_VALUE_OF_DELIWARE_EFFICIENCY'] = [single_value_of_deliware_efficiency_list[0].int_1,
                                                               single_value_of_deliware_efficiency_list[0].int_2,
                                                               single_value_of_deliware_efficiency_list[0].int_3]

    '''单车分货中装点厂区的价值'''
    single_value_of_factory_list: List[ModelConfig] = model_config_dict.get('SINGLE_VALUE_OF_FACTORY', [])
    if single_value_of_factory_list:
        model_config['SINGLE_VALUE_OF_FACTORY'] = [single_value_of_factory_list[0].int_1,
                                                   single_value_of_factory_list[0].int_2,
                                                   single_value_of_factory_list[0].int_3]

    '''单车分货中载重的价值'''
    single_value_of_weight_list: List[ModelConfig] = model_config_dict.get('SINGLE_VALUE_OF_WEIGHT', [])
    if single_value_of_weight_list:
        model_config['SINGLE_VALUE_OF_WEIGHT'] = [single_value_of_weight_list[0].int_1,
                                                  single_value_of_weight_list[0].int_2,
                                                  single_value_of_weight_list[0].int_3]

    '''单车分货中订单的价值'''
    single_value_of_order_num_list: List[ModelConfig] = model_config_dict.get('SINGLE_VALUE_OF_ORDER_NUM', [])
    if single_value_of_order_num_list:
        model_config['SINGLE_VALUE_OF_ORDER_NUM'] = [single_value_of_order_num_list[0].int_1]

    '''单车分货中额外添加的价值'''
    single_value_of_extra_list: List[ModelConfig] = model_config_dict.get('SINGLE_VALUE_OF_EXTRA', [])
    if single_value_of_extra_list:
        model_config['SINGLE_VALUE_OF_EXTRA'] = [single_value_of_extra_list[0].int_1]

    '''使用优化版本的城市'''
    single_use_optimal_city_list: List[ModelConfig] = model_config_dict.get('SINGLE_USE_OPTIMAL_CITY', [])
    optimal_city_list = []
    if single_use_optimal_city_list:
        for city in single_use_optimal_city_list:
            optimal_city_list.append(city.str_1)
    model_config['SINGLE_USE_OPTIMAL_CITY'] = optimal_city_list

    '''配载无结果后进行拆件配载的城市：支持全部，只要其中包含全部，就是全部城市'''
    single_sub_stowage_city_list: List[ModelConfig] = model_config_dict.get('SINGLE_SUB_STOWAGE_CITY', [])
    sub_stowage_city_list = []
    if single_sub_stowage_city_list:
        for city in single_sub_stowage_city_list:
            sub_stowage_city_list.append(city.str_1)
    model_config['SINGLE_SUB_STOWAGE_CITY'] = sub_stowage_city_list

    '''需要按备注指定客户的城市'''
    single_designate_consumer_city_list: List[ModelConfig] = model_config_dict.get('SINGLE_DESIGNATE_CONSUMER_CITY', [])
    if single_designate_consumer_city_list:
        consumer_city_list = []
        for city in single_designate_consumer_city_list:
            consumer_city_list.append(city.str_1)
        model_config['SINGLE_DESIGNATE_CONSUMER_CITY'] = consumer_city_list

    '''需要按备注指定客户的城市'''
    single_designate_consumer_flag_list: List[ModelConfig] = model_config_dict.get('SINGLE_DESIGNATE_CONSUMER_FLAG', [])
    if single_designate_consumer_flag_list:
        model_config['SINGLE_DESIGNATE_CONSUMER_FLAG'] = single_designate_consumer_flag_list[0].int_1

    '''单车分货中非生产用来存储货物的仓库'''
    single_storage_deliware_list: List[ModelConfig] = model_config_dict.get('SINGLE_STORAGE_DELIWARE', [])
    if single_storage_deliware_list:
        storage_deliware_list = []
        for deliware in single_storage_deliware_list:
            storage_deliware_list.append(deliware.str_1)
        model_config['SINGLE_STORAGE_DELIWARE'] = storage_deliware_list

    '''外贸对应的入库仓库'''
    rg_foreign_trade_deliware_list: List[ModelConfig] = model_config_dict.get('RG_FOREIGN_TRADE_DELIWARE', [])
    if rg_foreign_trade_deliware_list:
        deliware_list = []
        for deliware in rg_foreign_trade_deliware_list:
            deliware_list.append(deliware.str_1)
        model_config['RG_FOREIGN_TRADE_DELIWARE'] = deliware_list

    '''件重大于此值的优先排到前面配货'''
    single_big_piece_weight_list: List[ModelConfig] = model_config_dict.get('SINGLE_BIG_PIECE_WEIGHT', [])
    if single_big_piece_weight_list:
        model_config['SINGLE_BIG_PIECE_WEIGHT'] = single_big_piece_weight_list[0].int_1

    '''按流向只发哪些客户的货'''
    single_keep_consumer_list: List[ModelConfig] = model_config_dict.get('SINGLE_KEEP_CONSUMER', [])
    single_keep_consumer_dict = defaultdict(list)
    if single_keep_consumer_list:
        for single_keep_consumer in single_keep_consumer_list:
            single_keep_consumer_dict[','.join([single_keep_consumer.str_1, single_keep_consumer.str_2])].append(
                single_keep_consumer.str_3)
    model_config['SINGLE_KEEP_CONSUMER'] = single_keep_consumer_dict

    '''按流向不发哪些客户的货'''
    single_reject_consumer_list: List[ModelConfig] = model_config_dict.get('SINGLE_REJECT_CONSUMER', [])
    single_reject_consumer_dict = defaultdict(list)
    if single_reject_consumer_list:
        for single_reject_consumer in single_reject_consumer_list:
            single_reject_consumer_dict[','.join([single_reject_consumer.str_1, single_reject_consumer.str_2])].append(
                single_reject_consumer.str_3)
    model_config['SINGLE_REJECT_CONSUMER'] = single_reject_consumer_dict

    '''不使用推荐开单的（流向、车队）：['连云港市,连云区,源运物流', '连云港市,连云区,全部', '连云港市,全部,全部']'''
    single_black_list: List[ModelConfig] = model_config_dict.get('SINGLE_BLACK_LIST', [])
    black_list = []
    if single_black_list:
        for single_black in single_black_list:
            black_list.append(','.join([single_black.str_1 + ',' + single_black.str_2 + ',' + single_black.str_3]))
    model_config['SINGLE_BLACK_LIST'] = black_list

    '''相同的单子被删除多少次后将被锁定'''
    single_num_lock_list: List[ModelConfig] = model_config_dict.get('SINGLE_NUM_LOCK', [])
    if single_num_lock_list:
        model_config["SINGLE_NUM_LOCK"] = single_num_lock_list[0].int_1

    '''相同的单子被删除多少次后将被锁定的时间：小时'''
    single_lock_hour_list: List[ModelConfig] = model_config_dict.get('SINGLE_LOCK_HOUR', [])
    if single_lock_hour_list:
        model_config["SINGLE_LOCK_HOUR"] = single_lock_hour_list[0].int_1

    '''被删除后需要锁定的单子 是否需要筛掉：1筛掉，0不筛掉'''
    single_lock_order_flag_list: List[ModelConfig] = model_config_dict.get('SINGLE_LOCK_ORDER_FLAG', [])
    if single_lock_order_flag_list:
        model_config["SINGLE_LOCK_ORDER_FLAG"] = single_lock_order_flag_list[0].int_1

    '''被删除后需要锁定的单子：发货通知单号、订单号、出库仓库'''
    single_lock_order_list: List[ModelConfig] = model_config_dict.get('SINGLE_LOCK_ORDER', [])
    lock_order_list = []
    if single_lock_order_list:
        for lock_order in single_lock_order_list:
            lock_order_list.append(','.join([lock_order.str_1, lock_order.str_2, lock_order.str_3]))
    model_config["SINGLE_LOCK_ORDER"] = lock_order_list

    # 打印参数配置日志
    current_app.logger.info('数仓中模型配置：' + json.dumps(model_config, ensure_ascii=False))
    return model_config
