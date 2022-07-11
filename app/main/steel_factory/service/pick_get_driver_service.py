# -*- coding: utf-8 -*-
# Description:
# Created: luchengkai 2021/01/06 10:08
from threading import Thread

from app.main.steel_factory.dao.pick_propelling_filter_dao import pick_propelling_filter_dao
from app.main.steel_factory.rule import pick_propelling_label_rule, pick_data_format_rule, pick_save_result, \
    pick_propelling_rule, pick_pipe_propelling_label_rule, pick_pipe_propelling_screen_rule
from app.main.steel_factory.rule import pick_propelling_recall_screen_rule
from app.util.result import Result
from model_config import ModelConfig


def get_driver(json_data):
    """
    司机集获取入口
    :param json_data:
    :return:
    """
    """
    1.摘单计划筛选
    2.司机集获取(标签提取)
    3.司机集筛选(召回筛选)
    """
    """1.摘单计划筛选"""
    propelling_list = pick_data_format_rule.data_format_district(json_data)  # 待匹配摘单列表
    # 日钢摘单
    if propelling_list[0].company_id == 'C000062070' and propelling_list[0].business_module_id == '020':
        select_type = json_data.get("driverType", ModelConfig.PICK_SELECT_TYPE[0])
        if propelling_list[0].pickup_no:
            # 根据前端传入的摘单信息去数据库查找对应摘单计划
            temp_wait_propelling_list = pick_propelling_filter_dao.select_pick_truck_count(
                propelling_list[0].pickup_no)
            # 如果查不到，取前端传入的摘单信息
            propelling_list = temp_wait_propelling_list if temp_wait_propelling_list else propelling_list
        # 摘单计划预处理
        propelling_list = pick_propelling_rule.init_propelling_list(propelling_list, ModelConfig.PICK_OBJECT['PO1'])
        """2.司机集获取(从运力服务获取)，已筛过(根据距离)"""
        propelling_list, total_count = pick_propelling_label_rule.pick_label_extract_new(propelling_list, select_type)
        """3.司机集筛选(根据重量)"""
        propelling_list, current_count = pick_propelling_recall_screen_rule.pick_driver_recall_screen(propelling_list)
    # 管厂摘单
    else:
        # 摘单计划预处理
        propelling_list = pick_propelling_rule.init_propelling_list(propelling_list, ModelConfig.PICK_OBJECT['PO2'])
        if not propelling_list:
            return Result.success(data=[])
        """2.司机集获取(从运力服务获取)，已筛过(根据距离)"""
        propelling_list, total_count, flag = pick_pipe_propelling_label_rule.pick_pipe_label_extract(propelling_list)
        """3.司机集筛选(根据重量)"""
        propelling_list, current_count = pick_pipe_propelling_screen_rule.pick_pipe_screen(propelling_list, flag)
        # 如果 总车次 < 待推送司机数，司机返回0
        if flag and propelling_list[0].total_truck_num < current_count:
            total_count = 0
            current_count = 0
            propelling_list[0].drivers = []
    # 格式转换
    res1 = pick_data_format_rule.data_format_driver(propelling_list, total_count, current_count)
    # 结果保存到数据库
    Thread(target=pick_save_result.save_propelling_log, args=(propelling_list,)).start()
    return Result.success(data=res1)

# def deal_propelling(wait_propelling_list, truck_count_dict):
#     for propelling in wait_propelling_list:
#         if truck_count_dict[propelling.pickup_no]:
#             tmp_propelling = truck_count_dict[propelling.pickup_no][0]
#             propelling.total_truck_num = tmp_propelling.total_truck_num
#             propelling.pickup_start_time = tmp_propelling.pickup_start_time
#             propelling.remain_truck_num = tmp_propelling.reamin_truck_num
#             propelling.end_point = tmp_propelling.end_point
#             propelling.start_point = tmp_propelling.start_point
#             propelling.total_weight = tmp_propelling.total_weight
#             propelling.remain_total_weight = tmp_propelling.remain_total_weight
#
#     return wait_propelling_list
