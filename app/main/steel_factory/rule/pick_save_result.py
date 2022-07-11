# -*- coding: utf-8 -*-
# Description: 筛选待二次推送的摘单计划
# Created: luchengkai 2021/01/06
from typing import List
from datetime import datetime
from app.main.steel_factory.dao.pick_propelling_dao import pick_propelling_dao
from app.main.steel_factory.dao.pick_propelling_log_dao import pick_propelling_log_dao
from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.util.round_util import round_util_by_digit


def save_propelling_log(propelling_driver_list: List[PickPropelling]):
    """
    保存待推送摘单计划的司机列表
    :param propelling_driver_list:
    :return:
    """
    if not propelling_driver_list:
        return
    values = []
    create_date = datetime.now()
    for data in propelling_driver_list:
        for driver in data.drivers:
            item_tuple = (data.pickup_no,
                          data.prod_name,
                          data.start_point,
                          data.end_point,
                          data.city_name,
                          data.district_name,
                          data.total_truck_num,
                          data.remain_truck_num,

                          driver.driver_id,
                          driver.driver_phone,
                          driver.district_name,
                          driver.label_type,
                          create_date,
                          data.driver_type,
                          driver.location_flag,

                          driver.app_latitude,
                          driver.app_longitude,
                          round_util_by_digit(driver.app_dist, 5),
                          driver.truck_latitude,
                          driver.truck_longitude,
                          round_util_by_digit(driver.truck_dist, 5),
                          data.company_id,
                          data.business_module_id,
                          data.is_assign_drivers,
                          driver.response_probability
                          )
            values.append(item_tuple)
    # 存在driver_list不为空，但是推荐司机为空的情况
    if values:
        pick_propelling_log_dao.save_pick_log(values)


def save_msg_log(result_msg_list):
    """
    保存推送短信的司机列表
    :param result_msg_list:
    :return:
    """
    if not result_msg_list:
        return
    values = []
    create_date = datetime.now()
    for data in result_msg_list:
        for driver in data.get('driver_list', []):
            item_tuple = (data.get('pickup_no', '未知摘单号'),
                          data.get('company_id', '未知业务公司'),
                          data.get('business_module_id', '未知业务板块'),
                          driver.get('userId', '未知用户'),
                          create_date
                          )
            values.append(item_tuple)
    # 存在driver_list不为空，但是推荐司机为空的情况
    if values:
        pick_propelling_log_dao.save_msg_log(values)


def save_batch_wt_log(result_msg_list):
    """
    保存修改委托单状态的记录
    :param result_msg_list:
    :return:
    """
    if not result_msg_list:
        return
    values = []
    create_date = datetime.now()
    for data in result_msg_list:
        item_tuple = (data.spec_desc,
                      data.spec_desc_name,
                      data.warehouse_out_no,
                      data.city_code,

                      data.order_no,
                      data.pick_no,

                      data.wait_compare_total_sheet,
                      data.current_stock_total_sheet,
                      data.have_push_total_sheet,
                      data.ready_push_total_sheet,
                      create_date
                      )
        values.append(item_tuple)
    # 存在driver_list不为空，但是推荐司机为空的情况
    if values:
        pick_propelling_log_dao.save_batch_wt_log(values)
