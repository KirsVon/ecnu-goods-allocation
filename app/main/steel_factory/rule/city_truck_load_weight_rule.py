# -*- coding: utf-8 -*-
# Description: 各城市车辆推荐参考载重规则
# Created: jjunf 2021/5/10 13:28
import datetime
from typing import List

from flask import current_app

from app.main.steel_factory.dao.city_truck_load_weight_dao import city_truck_load_weight_dao
from app.main.steel_factory.entity.city_truck_load_weight import CityTruckLoadWeight
from app.util.bean_convert_utils import BeanConvertUtils
from app.util.split_group_util import split_group_util
from app.util.round_util import round_util


def get_city_truck_load_weight_reference(city_truck_load_weight_list: List[CityTruckLoadWeight]):
    """
    各城市车辆推荐参考载重规则
    :param city_truck_load_weight_list:
    :return:
    """
    # 各城市车辆推荐参考载重列表
    result_city_truck_load_weight_list = []
    # 按照公司、业务板块、车牌、省份、城市进行分组
    city_truck_load_weight_dict = split_group_util(city_truck_load_weight_list,
                                                   ['company_id', 'business_module_id', 'truck_no', 'province', 'city'])
    #
    for value_list in city_truck_load_weight_dict.values():
        # 按照开单重量顺序排序
        value_list.sort(key=lambda x: x.open_weight, reverse=False)
        # 新建一个city_truck_load_weight对象，并且拷贝value_list[0]的属性值
        city_truck_load_weight: CityTruckLoadWeight = BeanConvertUtils.copy_properties(value_list[0],
                                                                                       CityTruckLoadWeight)
        # 赋值最小最大开单重量
        city_truck_load_weight.min_weight = value_list[0].open_weight
        city_truck_load_weight.max_weight = value_list[-1].open_weight
        # 开单重量列表
        open_weight_list = [value.open_weight for value in value_list]
        # 获取推荐参考载重
        city_truck_load_weight.reference_weight = get_optimal_weight(open_weight_list)
        result_city_truck_load_weight_list.append(city_truck_load_weight)
    return result_city_truck_load_weight_list


def get_optimal_weight(weight_list):
    """
    从多个重量列表中选取一个最优的参考重量
    :param weight_list:
    :return:
    """
    # 如果只有一个重量，直接返回
    if len(weight_list) == 1:
        return weight_list[0]
    # 如果有多个重量，取
    else:
        index = round_util(len(weight_list) * 0.9)
        return weight_list[index - 1]


def city_truck_load_weight_filter(city_truck_load_weight_list: List[CityTruckLoadWeight]):
    """
    通过参考载重对比，排除调不需要更新的记录，并且找出需要更新的记录，将这些记录从表中删除，最后将记录保存到表中
    :param city_truck_load_weight_list:
    :return:
    """
    # 查询条件列表
    sql_condition_list = []
    for item in city_truck_load_weight_list:
        sql_condition_list.append(
            item.company_id + ',' + item.business_module_id + ',' + item.city + ',' + item.truck_no)
    # 将sql_condition_list分成多个列表，每个列表长度为1800，因为sql查询中的in条件中最多只能有2000个
    sql_condition_list = split_list(sql_condition_list, 1800)
    # 查找数据表中已有的数据
    exist_reference_list: List[CityTruckLoadWeight] = []
    t1 = datetime.datetime.now()
    for sql_condition in sql_condition_list:
        exist_reference_list.extend(city_truck_load_weight_dao.select_city_truck_load_weight_reference(sql_condition))
    t2 = datetime.datetime.now()
    current_app.logger.info('查找数据表中已有数据耗时：' + str(int((t2 - t1).total_seconds() * 1000)))
    # 表中需要更新(删除)的记录（先删再插入）
    need_update_list = []
    # 表中不需要更新的记录
    not_need_update_list = []
    # 与表中数据进行对比，判断是否需要更新
    if exist_reference_list:
        for exist_item in exist_reference_list:
            for item in city_truck_load_weight_list:
                if (exist_item.company_id == item.company_id
                        and exist_item.business_module_id == item.business_module_id
                        and exist_item.city == item.city and exist_item.truck_no == item.truck_no):
                    # 找出需要更新的记录
                    if (item.min_weight < exist_item.min_weight or item.max_weight > exist_item.max_weight
                            or item.reference_weight != exist_item.reference_weight):
                        need_update_list.append(item)
                        break
                    else:
                        not_need_update_list.append(item)
                        break
    # 从city_truck_load_weight_list中去除不需要更新的记录，将剩余是记录全部插入表中
    city_truck_load_weight_list = [i for i in city_truck_load_weight_list if i not in not_need_update_list]
    return need_update_list, city_truck_load_weight_list


def split_list(init_list, sep_len):
    """
    将列表init_list按照sep_len个一组进行切分
    :param init_list:初始列表
    :param sep_len:将多少个切分为一组
    :return:
    """
    result_list = []
    sum_len = 0
    while sum_len < len(init_list):
        result_list.append(init_list[sum_len:sum_len + sep_len])
        sum_len += sep_len
    return result_list


if __name__ == '__main__':
    b = [1, 2, 3, 4, 5, 6]
    a = get_optimal_weight(b)
    print(a)
