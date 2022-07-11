# -*- coding: utf-8 -*-
# Description: 筛选待二次推送的摘单计划
# Created: luchengkai 2020/11/16
import datetime
from typing import List
import config
from app.main.steel_factory.dao.pick_propelling_dao import pick_propelling_dao
from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.main.steel_factory.rule.pick_data_format_rule import data_format_insert, data_format_msg
from app.util.rest_template import RestTemplate
from model_config import ModelConfig


def init_propelling_list(wait_propelling_list: List[PickPropelling], select_object, exist_driver_list=None):
    """
    摘单计划预处理
    :return:
    """
    for wait_propelling in wait_propelling_list:
        # 推荐类型区分：接口调用、定时范围
        # 日钢汇好运单车 逐步扩大
        if select_object == ModelConfig.PICK_OBJECT['PO1']:
            wait_propelling.dist_type = get_dist_type(wait_propelling)
            wait_propelling.is_assign_drivers = 0
        # 成都管厂 5km
        else:
            wait_propelling.dist_type = ModelConfig.PICK_RESULT_TYPE['DIST5']

        # 客户id变更
        try:
            tmp_consignee_id = wait_propelling.consignee_company_ids.split(",")
            wait_propelling.consignee_company_ids = tmp_consignee_id[0]
        except Exception as e:
            wait_propelling.consignee_company_ids = '未知客户'
        # 品名变更
        tmp_prod = wait_propelling.prod_name.split(",")
        wait_propelling.prod_name = ModelConfig.PICK_REMARK.get(tmp_prod[0], '未知品种')
        # 计算待推送的司机上限
        wait_propelling.wait_driver_count = wait_propelling.remain_truck_num * ModelConfig.PICK_DRIVER_NUM_LIMIT
        # 已收到摘单消息的司机id列表
        if exist_driver_list:
            wait_propelling.exist_driver_id_list = [item.driver_id for item in exist_driver_list if
                                                    item.pickup_no == wait_propelling.pickup_no]
        # 总重量赋值
        try:
            wait_propelling.total_weight = float(wait_propelling.total_weight)
        except Exception as e:
            wait_propelling.total_weight = 0
            pass
        # 剩余重量重量赋值
        try:
            wait_propelling.remain_total_weight = float(wait_propelling.remain_total_weight)
        except Exception as e:
            wait_propelling.remain_total_weight = 0
            pass
        # 单车重量赋值
        try:
            wait_propelling.single_weight = float(wait_propelling.total_weight) / float(wait_propelling.total_truck_num)
        except Exception as e:
            wait_propelling.single_weight = 0
            pass
    return wait_propelling_list


def get_dist_type(wait_propelling):
    # 如果摘单开始时间为空，说明是初始状态单子，走十公里推荐;如果是策略2，走十公里推荐
    if (not wait_propelling.pickup_start_time) or (wait_propelling.driver_type == 'SJLY20'):
        return ModelConfig.PICK_RESULT_TYPE.get("DIST10")
    now_date = datetime.datetime.now()
    minutes = int((now_date - wait_propelling.pickup_start_time).total_seconds()) / 60
    if wait_propelling.create_date:
        temp_minutes = int((now_date - wait_propelling.create_date).total_seconds()) / 60
        if temp_minutes < minutes:
            minutes = temp_minutes
    # 摘单开始了10分钟以内
    if minutes <= ModelConfig.PICK_CONTINUE_TIME.get("MINUTE10"):
        result_type = ModelConfig.PICK_RESULT_TYPE.get("DIST10")
    # 摘单开始了15分钟以内
    elif minutes <= ModelConfig.PICK_CONTINUE_TIME.get("MINUTE15"):
        result_type = ModelConfig.PICK_RESULT_TYPE.get("DIST20")
    # 摘单开始了20分钟以内
    elif minutes <= ModelConfig.PICK_CONTINUE_TIME.get("MINUTE20"):
        result_type = ModelConfig.PICK_RESULT_TYPE.get("DIST30")
    # 摘单开始了25分钟以内
    elif minutes <= ModelConfig.PICK_CONTINUE_TIME.get("MINUTE25"):
        result_type = ModelConfig.PICK_RESULT_TYPE.get("DIST40")
    # 摘单开始了30分钟以内
    elif minutes <= ModelConfig.PICK_CONTINUE_TIME.get("MINUTE30"):
        result_type = ModelConfig.PICK_RESULT_TYPE.get("DIST50")
    # 摘单开始30分钟之后
    else:
        result_type = ModelConfig.PICK_RESULT_TYPE.get("DEFAULT")
    return result_type


def pick_list_filter(company_id, business_type):
    """
    从t_pick_order表中获取待摘单列表
    :return: wait_propelling_list
    """
    wait_propelling_list = pick_propelling_dao.select_wait_pick_list(company_id, business_type)
    return wait_propelling_list


def pick_driver_list(company_id, business_type):
    """
    从t_pick_order表中获取待摘单列表
    :return: wait_driver_list
    """
    wait_driver_list = pick_propelling_dao.select_wait_driver_list(company_id, business_type)
    return wait_driver_list


def interaction_with_java(propelling_driver_list: List[PickPropelling]):
    """
    和后台交互
    1、新增司机列表
    2、调用短信接口
    :param propelling_driver_list:
    :return:
    """
    res1 = None
    res2 = None
    """1、新增司机列表"""
    result_insert_list = data_format_insert(propelling_driver_list)
    if result_insert_list:
        for result_insert in result_insert_list:
            url = config.get_active_config().TENDER_SERVICE_URL + "/pickUpList/insertPickDriverList"
            res1 = RestTemplate.do_post(url, result_insert)

    """2、调用短信接口"""
    result_msg_list = data_format_msg(propelling_driver_list)
    if result_msg_list:
        url = config.get_active_config().TENDER_SERVICE_URL + "/pickUpMessage/incompletePickUp"
        res2 = RestTemplate.do_post(url, result_msg_list)
    return result_insert_list, result_msg_list
