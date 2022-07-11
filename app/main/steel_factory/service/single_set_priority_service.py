# -*- coding: utf-8 -*-
# Description: 设置库存的优先发运
# Created: jjunf 2021/5/8 11:23
import datetime
from typing import List
from flask import current_app, json

from app.main.steel_factory.dao.single_priority_dao import priority_dao
from app.main.steel_factory.dao.load_task_item_dao import load_task_item_dao
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from model_config import ModelConfig


def set_priority_service(init_stock_list: List[Stock], truck: Truck):
    """
    设置库存的优先发运
    :param truck:
    :param init_stock_list:
    :return:
    """
    # # 查询需要设置为优先发运的货物优先级字典列表：键为发货通知单号+','+订单号；值为[优先等级(1或者2)，优先发运量]
    priority_dict = priority_dao.select_priority()
    # 日志
    #current_app.logger.info('设置为优先发运的货物：' + json.dumps(priority_dict, ensure_ascii=False))
    # 查询已经优先发运的货物的量
    priority_send_weight_dict = load_task_item_dao.select_priority_send_weight(priority_dict.keys(), truck.schedule_no)
    # 日志
    #current_app.logger.info('已经优先发运的货物：' + json.dumps(priority_send_weight_dict, ensure_ascii=False))
    # 查找出哪些仓库没达到车次数上限   各仓库一般车辆容纳数
    free_deliware_list = []
    for deliware in ModelConfig.SINGLE_WAREHOUSE_WAIT_DICT:
        if ModelConfig.SINGLE_NOW_WAREHOUSE_DICT.get(deliware, 0) < ModelConfig.SINGLE_WAREHOUSE_WAIT_DICT.get(
                deliware):
            free_deliware_list.append(deliware)
    # 日志
    #current_app.logger.info('未达车次数上限的仓库：' + json.dumps(free_deliware_list, ensure_ascii=False))
    # 设置库存的优先级
    for stock in init_stock_list:
        key = stock.notice_num + ',' + stock.oritem_num
        # 设置的优先发运量
        priority_weight = priority_dict.get(key, [0, 0])[1]
        # 已经优先发运的量
        send_weight = priority_send_weight_dict.get(key, 0)
        # 如果没有达到优先发运量，则设置优先级
        if send_weight < priority_weight:
            stock.priority = priority_dict.get(key)[0]
        # stock.priority = priority_dict.get(stock.notice_num + ',' + stock.oritem_num + ',' + stock.deliware_house, 4)
        # stock.priority = int(stock.priority) if stock.priority == '1' or stock.priority == '2' else 4
        # 将闲置仓库的优先级设置为3
        if stock.priority == 9 and stock.deliware_house in free_deliware_list:
            stock.priority = 3
        # 超期清理
        if stock.latest_order_time and stock.priority == 9:
            # 获取当前时间
            date_now = datetime.datetime.now()
            # # 调试时使用请求的时间点
            # date_now = datetime.datetime.strptime('2021-05-31 06:35:26', "%Y%m%d%H%M%S")
            # 4.超期清理1(24-48小时)
            if (datetime.timedelta(hours=ModelConfig.OVER_TIME_LOW_HOUR) < date_now - datetime.datetime.strptime(
                    stock.latest_order_time, "%Y%m%d%H%M%S") <= datetime.timedelta(
                    hours=ModelConfig.OVER_TIME_UP_HOUR)):
                stock.priority = 4
            # 5.超期清理2(>48小时)
            if (datetime.timedelta(hours=ModelConfig.OVER_TIME_UP_HOUR) < date_now - datetime.datetime.strptime(
                    stock.latest_order_time, "%Y%m%d%H%M%S")):
                stock.priority = 5


if __name__ == '__main__':
    # latest_order_time = '2021-05-01 20:39:20'
    # # 获取当前时间
    # date_now = datetime.datetime.now()
    # if date_now - datetime.datetime.strptime(latest_order_time, "%Y-%m-%d %H:%M:%S") > datetime.timedelta(days=2):
    #     print(11)
    # else:
    #     print(222)
    #
    # a = datetime.datetime.strptime(latest_order_time, "%Y-%m-%d %H:%M:%S")
    # c = date_now - a

    pass
