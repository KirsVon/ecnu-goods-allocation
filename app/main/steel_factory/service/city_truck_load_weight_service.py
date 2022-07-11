# -*- coding: utf-8 -*-
# Description: 各城市车辆历史载重分析服务
# Created: jjunf 2021/5/8 14:52
import datetime
from threading import Thread
from typing import List, Dict

import pandas as pd
from flask import current_app

from app.main.steel_factory.dao.city_truck_load_weight_dao import city_truck_load_weight_dao
from app.main.steel_factory.entity.city_truck_load_weight import CityTruckLoadWeight
from app.main.steel_factory.rule.city_truck_load_weight_rule import get_city_truck_load_weight_reference
from app.main.steel_factory.rule.city_truck_load_weight_rule import city_truck_load_weight_filter
from app.util.date_util import get_now_date
from app.util.result import Result


def city_truck_load_weight_service(json_data):
    """
    各城市车辆历史载重分析服务
    :param json_data:
    :return:
    """
    # 获取各城市车辆历史载重
    city_truck_load_weight_list = get_city_truck_load_weight(json_data)
    if not city_truck_load_weight_list:
        return Result.info(msg='没有需要更新的数据！')
    # 根据历史载重情况计算各城市车辆推荐参考载重
    city_truck_load_weight_list = get_city_truck_load_weight_reference(city_truck_load_weight_list)
    # 通过参考载重对比，排除调不需要更新的记录，并且找出需要更新的记录，将这些记录从表中删除，最后将记录保存到表中
    need_update_list, city_truck_load_weight_list = city_truck_load_weight_filter(city_truck_load_weight_list)
    # 将推荐参考载重保存到数据库
    Thread(target=save_city_truck_load_weight_reference, args=(need_update_list, city_truck_load_weight_list,)).start()
    return Result.success()


def get_city_truck_load_weight(json_data: Dict):
    """
    获取city_truck_load_weight对象列表
    :return:
    """
    # 查询历史运单数据
    t1 = datetime.datetime.now()
    df_history_waybill = city_truck_load_weight_dao.select_history_waybill(json_data['company_id'],
                                                                           json_data['business_module_id'],
                                                                           json_data.get('total_day', None))
    t2 = datetime.datetime.now()
    current_app.logger.info('查询历史运单数据耗时：' + str(int((t2 - t1).total_seconds() * 1000)))
    # 查询开单详情数据
    df_loading_detail = city_truck_load_weight_dao.select_loading_detail(json_data.get('total_day', None))
    t3 = datetime.datetime.now()
    current_app.logger.info('查询开单详情数据耗时：' + str(int((t3 - t2).total_seconds() * 1000)))
    if df_history_waybill.empty or df_loading_detail.empty:
        return []
    # 根据调度号schedule_no、车牌truck_no进行关联
    df = pd.merge(df_history_waybill, df_loading_detail, how='inner', on=['schedule_no', 'truck_no'])
    # pandas转对象列表
    dic = df.to_dict(orient='records')
    city_truck_load_weight_list = [CityTruckLoadWeight(i) for i in dic]
    return city_truck_load_weight_list


def save_city_truck_load_weight_reference(need_update_list: List[CityTruckLoadWeight],
                                          city_truck_load_weight_list: List[CityTruckLoadWeight]):
    """
    保存各城市车辆推荐参考载重
    :param need_update_list:
    :param city_truck_load_weight_list:
    :return:
    """

    # 需要删除的记录need_update_list
    delete_values = []
    if need_update_list:
        for item in need_update_list:
            delete_values.append(
                item.company_id + ',' + item.business_module_id + ',' + item.city + ',' + item.truck_no)
    # 需要插入的记录city_truck_load_weight_list
    insert_values = []
    if city_truck_load_weight_list:
        create_date = get_now_date()
        for item in city_truck_load_weight_list:
            item_tuple = (item.company_id,
                          item.business_module_id,
                          item.province,
                          item.city,
                          item.truck_no,
                          item.reference_weight,
                          item.min_weight,
                          item.max_weight,
                          create_date
                          )
            insert_values.append(item_tuple)
        city_truck_load_weight_dao.save_city_truck_load_weight_reference(delete_values, insert_values)


if __name__ == '__main__':
    city_truck_load_weight_service(
        {
            "company_id": "C000000882",
            "business_module_id": "009",
            "total_day": 10
        }
    )
