# -*- coding: utf-8 -*-
# Description: 日钢西门推荐开单，删单子检测服务
# Created: jjunf 2021/6/11 15:13
import json
from collections import defaultdict
from typing import List

from app.main.steel_factory.dao.model_config_dao import model_config_dao
from app.main.steel_factory.dao.single_delete_check_dao import single_delete_check_dao
from app.main.steel_factory.entity.order import Order
from app.util.split_group_util import split_group_util
from model_config import ModelConfig


def single_delete_check_service():
    # 查询推荐开单的单子和实际开单的单子
    order_list = single_delete_check_dao.select_recommend_and_open(ModelConfig.SINGLE_LOCK_HOUR)
    # print(json.dumps([i.as_dict() for i in order_list]))
    # 对比找出删除次数>=SINGLE_NUM_LOCK的单子，以及操作时间
    delete_order_dict_list = find_delete_order(order_list)
    # 找出order_list中下发过的单子，以及其最新下发的时间
    open_order_dict = find_open_order(order_list)
    # 判断delete_order_dict_list中的单子是否在open_order_dict中出现，若出现，则判断在其最新下发的时间之后是否还被删除了>=SINGLE_NUM_LOCK次
    result_list = get_result_list(delete_order_dict_list, open_order_dict)
    # print(json.dumps([i for i in result_list]))
    # 将结果保存到数据表中
    save_result(result_list)


def find_delete_order(order_list: List[Order]):
    """
    对比找出删除次数>=SINGLE_NUM_LOCK的单子，以及操作时间
    :param order_list:
    :return:
    """
    '''对比找出被删除的单子，以及操作时间'''
    # 中间结果字典
    result_dict = defaultdict(list)
    # 按车次号分组
    order_dict = split_group_util(order_list, ['schedule_no'])
    # 对比找出被删除的单子，以及操作时间
    for temp_order_list in order_dict.values():
        # 推荐的单子
        recommend_order_list = [order for order in temp_order_list if order.style == '推荐开单']
        recommend_order_dict = get_order_attr(recommend_order_list)
        # 实际开单的单子
        open_order_list = [order for order in temp_order_list if order.style == '实际开单']
        open_order_dict = get_order_attr(open_order_list)
        # 推荐的被删除的单子
        for recommend_key in recommend_order_dict.keys():
            # 推荐的单子没有被采纳，并且该报道号开单了，没有被作废
            if recommend_key not in open_order_dict.keys() and open_order_list:
                result_dict[recommend_key].extend(recommend_order_dict[recommend_key])
    '''对比找出被删除的单子，以及操作时间'''
    '''找出其中删除次数>=SINGLE_NUM_LOCK的单子'''
    # 结果列表：order对象，只有key和create_date属性有值
    delete_order_dict_list = {}
    # 根据单子，按创建时间排序，并且找出其中删除次数>=SINGLE_NUM_LOCK的单子
    for key in result_dict.keys():
        value_list = result_dict[key]
        if len(value_list) >= ModelConfig.SINGLE_NUM_LOCK:
            # 按时间升序
            value_list.sort(reverse=False)
            delete_order_dict_list[key] = value_list
    '''找出其中删除次数>=SINGLE_NUM_LOCK的单子'''
    return delete_order_dict_list


def get_order_attr(temp_order_list):
    """

    :param temp_order_list:
    :return:
    """
    # 结果字典：发货通知单号、订单号、出库仓库：创建时间列表
    result_dict = defaultdict(list)
    for order in temp_order_list:
        result_dict[','.join([order.notice_num, order.oritem_num, order.outstock_code])].append(order.create_date)
    return result_dict


def find_open_order(order_list: List[Order]):
    """
    查找这些被删除的单子在该时间段内是否发过以及下发的最新时间
    :param order_list:
    :return:
    """
    # 结果字典
    result_dict = {}
    # 实际开单的
    open_order_list = [order for order in order_list if order.style == '实际开单']
    open_order_dict = get_order_attr(open_order_list)
    # 找出最新下发时间
    for key in open_order_dict.keys():
        value_list = open_order_dict[key]
        # 按时间升序
        # value_list.sort(key=lambda x: x.create_date, reverse=False)
        value_list.sort(reverse=False)
        result_dict[key] = value_list[-1]
    return result_dict


def get_result_list(delete_order_dict_list, open_order_dict):
    """
    找出最后达到删除次数的订单结果
    :param delete_order_dict_list:
    :param open_order_dict:
    :return:
    """
    # 达到删除次数的订单结果
    result_list = []
    # 判断delete_order_dict_list中的单子是否在open_order_dict中出现
    for key in delete_order_dict_list.keys():
        if key in open_order_dict:
            # 最新开单时间
            open_time = open_order_dict[key]
            # 在最新开单时间之后被删除的时间
            newest_delete_time_list = [delete_time for delete_time in delete_order_dict_list[key] if
                                       delete_time > open_time]
            # 如果没有达到被删除的次数
            if len(newest_delete_time_list) < ModelConfig.SINGLE_NUM_LOCK:
                continue
        result_list.append(key)
    return result_list


def save_result(result_list: List[str]):
    """
    将结果保存到数据表中
    :param result_list: 发货通知单号、订单号、出库仓库
    :return:
    """
    value_list = []
    # 保存结果
    for item in result_list:
        item_list = item.split(',')
        item_tuple = (
            'singleGoodsAllocation',
            'SINGLE_LOCK_ORDER',

            item_list[0],
            item_list[1],
            item_list[2],
            None,

            None,
            None,
            None,
            None,

            None,
            None,
            None,
            None
        )
        value_list.append(item_tuple)
    # 清除上一次数据的条件
    delete_condition_dict = {'interface_name': 'singleGoodsAllocation',
                             'config_name': 'SINGLE_LOCK_ORDER'}
    model_config_dao.save_model_config(value_list, delete_condition_dict)


if __name__ == '__main__':
    single_delete_check_service()
