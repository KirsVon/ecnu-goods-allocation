# -*- coding: utf-8 -*-
# Description: 
# Created: shaoluyu 2020/9/29 9:12
import copy
from threading import Thread
from typing import List
from flask import current_app

from app.main.steel_factory.dao.pick_company_dao import pick_company_dao
from app.main.steel_factory.dao.pick_save_log import save_pick_log
from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.pick_task import PickTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule import pick_goods_dispatch_filter, pick_create_pick_task_rule
from app.main.steel_factory.rule.pick_compose_public_method import merge_split_stock
from app.main.steel_factory.rule.pick_wait_stock_compose import pick_wait_stock_compose
from app.main.steel_factory.service import pick_stock_service
from app.main.steel_factory.service.pick_deduct_result_service import deduct_from_pick_list
from app.test.jjunf.pick_optimization.pick_dispatch_optimization_service import dispatch_optimization_service
from app.util.date_util import get_now_date
from app.util.enum_util import LoadTaskType
from app.util.generate_id import GenerateId
from app.util.result import Result
from app.util.round_util import round_util
from app.util.uuid_util import UUIDUtil
from model_config import ModelConfig, set_model_config
from param_config import set_param_config, ParamConfig


def dispatch(json_data):
    """
    摘单分货入口
    :return:
    """
    """
    1.库存预处理
    2.将库存分为西区、老区两个部分，并且切分好
    3.将每个区的库存，按区县、客户分类排序，同区县同客户的按品种、出库仓库再分类排序
    4.同区县同客户的货物先组合配载，同品种优先组合
    5.同客户不同厂区、同厂区同区县不同客户 之间货物组合（哪一个更优？）
    """
    # 重置车次id
    GenerateId.set_id()
    # 从数仓表中读取模型配置
    set_model_config()
    # 使用动态参数配置
    if ParamConfig.FLAG:
        # 获取最新的参数配置
        set_param_config()
    # 尾货列表
    tail_list: List[Stock] = []
    # 车次列表
    load_task_list: List[LoadTask] = []
    # 获取经过预处理的库存列表
    stock_list, qingdao_stock_list, temp_tail_list, early_load_task_list = pick_stock_service.get_pick_stock(json_data)
    tail_list.extend(temp_tail_list)
    load_task_list.extend(early_load_task_list)
    # 配载，得到配载列表、无法配载的剩余尾货列表
    temp_load_task_list, temp_tail_list = pick_goods_dispatch_filter.dispatch_filter(stock_list)
    load_task_list.extend(temp_load_task_list)
    tail_list.extend(temp_tail_list)
    # 青岛的单独配载(不能跨客户拼货)
    temp_load_task_list, temp_tail_list = pick_goods_dispatch_filter.dispatch_filter_one_consumer(qingdao_stock_list)
    load_task_list.extend(temp_load_task_list)
    tail_list.extend(temp_tail_list)
    # 将tail_list中相同的订单合并
    tail_list = merge_split_stock(tail_list)
    # 将尾货中同客户等货的库存进行配货
    temp_load_task_list, tail_list = pick_wait_stock_compose(tail_list)
    load_task_list.extend(temp_load_task_list)
    '''分货优化'''
    try:
        # 是否使用遗传算法
        if ModelConfig.GA_USE_FLAG:
            copy_load_task_list = [i.as_dict() for i in copy.deepcopy(load_task_list)]
            copy_tail_list = [i.as_dict() for i in copy.deepcopy(tail_list)]
            from app.task.celery_task import dispatch_optimization
            dispatch_optimization.delay(copy_load_task_list, copy_tail_list)
            # ga_load_task_list, ga_tail_list = dispatch_optimization_service(copy.deepcopy(load_task_list),
            #                                                                 copy.deepcopy(tail_list))
            # 是否将遗传算法的结果作为输出
            # if ModelConfig.GA_USE_RESULT_FLAG:
            #     load_task_list = ga_load_task_list
            #     tail_list = ga_tail_list
    except:
        current_app.logger.info('优化出错！！！')
    '''分货优化'''
    # 合并车次，创建摘单计划
    pick_list = pick_create_pick_task_rule.create_pick_task(load_task_list)
    # 摘单记录、尾货保存到数据库
    Thread(target=save_result, args=(pick_list, tail_list,)).start()
    # 最后对pick_list的扣除操作：未开单有效调度单扣除操作、依据各城市摘单派单发运量限制从pick_list中扣除、青岛的货物车次数减半
    pick_list, deduct_pick_list = deduct_from_pick_list(pick_list)
    # 被扣除的已调度未开单的摘单记录保存到数据库
    Thread(target=save_deduct_pick, args=(deduct_pick_list,)).start()
    # 格式转换
    result_dic = data_format(pick_list, tail_list)
    return Result.success(data=result_dic)


def data_format(pick_list: List[PickTask], tail_list):
    """
    格式转换
    :param tail_list:
    :param pick_list:
    :return:
    """
    result_dic = {}
    # 摘单记录的格式转换
    p_list = []
    if pick_list:
        for pick_task in pick_list:
            # 是否按客户取价格
            price_flag = True if pick_task.city in ModelConfig.GET_PRICE_BY_CONSUMER_CITY else False
            # 摘单收货用户id
            pick_consumer_id = pick_company_dao.select_company_id(list(pick_task.consumer))
            # 收货用户id，如果不按客户获取单价，这个id为空
            if price_flag:
                consumer_id = pick_consumer_id
            else:
                consumer_id = ''
            p_dic = {
                "sourceName": pick_task.source_name,
                "totalWeight": (round_util(ModelConfig.PICK_TRUCK_NUM_UP_LIMIT *
                                           pick_task.total_weight / pick_task.truck_num)
                                if pick_task.truck_num > ModelConfig.PICK_TRUCK_NUM_UP_LIMIT
                                else pick_task.total_weight),
                "truckNum": (ModelConfig.PICK_TRUCK_NUM_UP_LIMIT
                             if pick_task.truck_num > ModelConfig.PICK_TRUCK_NUM_UP_LIMIT
                             else pick_task.truck_num),
                "province": pick_task.province,
                "city": pick_task.city,
                "endPoint": pick_task.end_point,
                "bigCommodity": pick_task.big_commodity,
                "commodity": pick_task.commodity,
                "remark": pick_task.remark,
                "groupFlag": pick_task.group_flag,
                "templateNo": pick_task.template_no,
                "priceFlag": price_flag,
                "consumerId": consumer_id,
                "pickConsumerId": pick_consumer_id,
                "items": [{
                    "sourceName": item.source_name,
                    "totalWeight": (round_util(ModelConfig.PICK_TRUCK_NUM_UP_LIMIT * item.total_weight / item.truck_num)
                                    if item.truck_num > ModelConfig.PICK_TRUCK_NUM_UP_LIMIT
                                    else item.total_weight),
                    "truckNum": (ModelConfig.PICK_TRUCK_NUM_UP_LIMIT
                                 if item.truck_num > ModelConfig.PICK_TRUCK_NUM_UP_LIMIT
                                 else item.truck_num),
                    "truckCount": item.truck_count,
                    "province": pick_task.province,
                    "city": item.city,
                    "endPoint": item.end_point,
                    "bigCommodity": item.big_commodity,
                    "commodity": item.commodity,
                    "remark": item.remark
                } for item in pick_task.items]
            }
            p_list.append(p_dic)
    result_dic['pick_list'] = p_list
    # 尾货记录的格式转换
    s_list = []
    if tail_list:
        for stock in tail_list:
            temp_number = stock.can_split_number - stock.actual_number
            s_dict = {
                "sourceNumber": stock.source_number,
                "noticeNum": stock.notice_num,
                "oritemNum": stock.oritem_num,
                "deliwareHouse": stock.deliware_house,
                "sendNumber": temp_number,
                "sendWeight": 0 if temp_number == 0 else round(stock.can_split_weight - stock.actual_weight / 1000, 3)
            }
            s_list.append(s_dict)
    result_dic['tail_list'] = s_list
    return result_dic


def save_result(pick_list, tail_list):
    """
    保存摘单分货的记录
    :param tail_list:
    :param pick_list:
    :return:
    """
    if not pick_list and not tail_list:
        return None
    values = []
    create_date = get_now_date()
    # 摘单记录
    if pick_list:
        # pick_list_item = []
        for pick in pick_list:
            # pick_list_item.extend(pick.items)
            pick_list_item = [pick.items[0]]
            """
            保存到数据库时可能存在问题，如果pick_task_item中把整车的货物都放进去，那么在跨厂区时会重复存储
            """
            for pick_item in pick_list_item:
                for load_task in pick_item.items:
                    for load_task_item in load_task.items:
                        item_tuple = (pick.pick_id,
                                      pick.total_weight,
                                      pick.truck_num,
                                      pick.remark,
                                      load_task.load_task_id,
                                      load_task.load_task_type,
                                      load_task.total_weight,
                                      load_task.count,
                                      load_task_item.weight,
                                      load_task_item.count,
                                      load_task_item.city,
                                      load_task_item.end_point,
                                      load_task_item.consumer,
                                      load_task_item.big_commodity,
                                      load_task_item.commodity,
                                      load_task_item.outstock_code,
                                      load_task_item.notice_num,
                                      load_task_item.oritem_num,
                                      create_date
                                      )
                        values.append(item_tuple)
    # 尾货
    if tail_list:
        for stock in tail_list:
            tail_id = UUIDUtil.create_id('tail')
            train_id = GenerateId.get_id()
            item_tuple = (tail_id,
                          -1,
                          -1,
                          '',
                          train_id,
                          LoadTaskType.TYPE_5.value,
                          -1,
                          -1,
                          stock.actual_weight / 1000,
                          stock.actual_number,
                          stock.city,
                          stock.dlv_spot_name_end,
                          stock.consumer,
                          stock.big_commodity_name,
                          stock.commodity_name,
                          stock.deliware_house,
                          stock.notice_num,
                          stock.oritem_num,
                          create_date
                          )
            values.append(item_tuple)
    # 库存预处理中被扣除的
    if ModelConfig.be_deducted_stock_list:
        for stock in ModelConfig.be_deducted_stock_list:
            tail_id = UUIDUtil.create_id('deduct')
            train_id = GenerateId.get_id()
            item_tuple = (tail_id,
                          -2,
                          -2,
                          '',
                          train_id,
                          LoadTaskType.TYPE_0.value,
                          -2,
                          -2,
                          stock.actual_weight / 1000,
                          stock.actual_number,
                          stock.city,
                          stock.dlv_spot_name_end,
                          stock.consumer,
                          stock.big_commodity_name,
                          stock.commodity_name,
                          stock.deliware_house,
                          stock.notice_num,
                          stock.oritem_num,
                          create_date
                          )
            values.append(item_tuple)
    save_pick_log.save_pick_log(values)


def save_deduct_pick(deduct_pick_list):
    """
    保存被扣除的已调度未开单的摘单记录
    :param deduct_pick_list: 被扣除的已调度未开单的摘单记录
    :return:
    """
    if not deduct_pick_list:
        return None
    create_date = get_now_date()
    # 被扣除的已调度未开单的摘单记录
    deduct_values = []
    for pick in deduct_pick_list:
        across_factory = 1 if len(pick.deliware_district) > 1 else 0
        pick_item = pick.items[0]
        load_task = pick_item.items[0]
        # 如果跨厂区，则保存每个厂区的记录
        if len(pick.deliware_district) > 1:
            for load_task_item in load_task.items:
                item_tuple = (pick.pick_id,
                              pick.remark,
                              load_task_item.city,
                              load_task_item.end_point,
                              load_task_item.big_commodity,
                              across_factory,
                              create_date
                              )
                deduct_values.append(item_tuple)
        # 否则只保留一条记录
        else:
            load_task_item = load_task.items[0]
            item_tuple = (pick.pick_id,
                          pick.remark,
                          load_task_item.city,
                          load_task_item.end_point,
                          load_task_item.big_commodity,
                          across_factory,
                          create_date
                          )
            deduct_values.append(item_tuple)
    save_pick_log.save_pick_deduct_log(deduct_values)
