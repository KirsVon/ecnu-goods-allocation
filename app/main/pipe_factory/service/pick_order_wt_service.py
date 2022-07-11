# -*- coding: utf-8 -*-
# Description: 委托订单处理服务
# Created: jjunf 2021/3/29 16:59
import random
from typing import List
import json

from app.main.pipe_factory.dao.pick_order_wt_dao import order_wt_dao
from app.main.pipe_factory.dao.pick_special_consumer_dao import pick_special_consumer_dao
from app.main.pipe_factory.entity.order_wt import OrderWt
from app.main.pipe_factory.entity.special_consumer import SpecialConsumer
from app.util.bean_convert_utils import BeanConvertUtils
from app.util.split_group_util import split_group_util
from model_config import ModelConfig


def get_order_wt(data):
    """
    获取委托订单
    :return:
    """
    # 查询指定司机的客户
    special_consumer_list: List[SpecialConsumer] = pick_special_consumer_dao.select_special_consumer_list()
    # 从数据库中查询需要委托的订单
    if data == ModelConfig.CDPZJH_REQUEST_FLAG:
        order_wt_list = order_wt_dao.select_order_wt()
        from celery.utils.log import get_task_logger
        # 获取celery执行器的日志记录器
        logger = get_task_logger('celery_worker')
        # 打印日志
        logger.info('委托订单' + str(len(order_wt_list)) + '条：' +
                    json.dumps([order_wt.as_dict() for order_wt in order_wt_list], ensure_ascii=False))
        # 打印日志
        logger.info('指定司机的客户：' + json.dumps([i.as_dict() for i in special_consumer_list], ensure_ascii=False))
    # 获取传入的委托资源
    else:
        order_wt_list = [OrderWt(order_wt) for order_wt in data]
        consumer_id_list = [item.consumer for item in order_wt_list]
        consumer_dict = order_wt_dao.get_company_name(consumer_id_list)
        for order_wt in order_wt_list:
            order_wt.consumer_name = consumer_dict.get(order_wt.consumer, '')
        # # 按照订单的最新更新时间升序排序
        # order_wt_list.sort(key=lambda x: x.update_date, reverse=False)
        from flask import current_app
        # 打印日志
        current_app.logger.info('指定司机的客户：' +
                                json.dumps([i.as_dict() for i in special_consumer_list], ensure_ascii=False))
    # 指定司机的客户列表
    designated_drivers_consumer_list = [special_consumer.consumer_id for special_consumer in special_consumer_list
                                        if special_consumer.driver_id is not None]
    # 指定司机的客户字典{客户id：客户所属司机池}
    consumer_group_dict = {}
    pool_name_dict = {}
    for special_consumer in special_consumer_list:
        consumer_group_dict[special_consumer.consumer_id] = special_consumer.driver_pool_id
        pool_name_dict[special_consumer.consumer_id] = special_consumer.driver_pool_name
    # 客户绑定
    for order_wt in order_wt_list:
        order_wt.driver_pool_id = consumer_group_dict.get(order_wt.consumer, order_wt.consumer)
        order_wt.driver_pool_name = pool_name_dict.get(order_wt.consumer, order_wt.consumer)

    # 将委托订单分为自提(YWXZ50)和非自提(YWXZ10)
    self_pick_order_wt_list = [order_wt for order_wt in order_wt_list if order_wt.business_nature == 'YWXZ50']
    non_self_pick_order_wt_list = [order_wt for order_wt in order_wt_list if order_wt.business_nature == 'YWXZ10']
    # 将非自提(YWXZ10)中客户指定司机的委托订单单独拿出来
    special_consumer_order_wt_list = [order_wt for order_wt in non_self_pick_order_wt_list
                                      if order_wt.consumer in designated_drivers_consumer_list]
    non_self_pick_order_wt_list = [order_wt for order_wt in non_self_pick_order_wt_list
                                   if order_wt not in special_consumer_order_wt_list]
    # 将拼车的多条订单合并成1条
    self_pick_order_wt_list = merge_truck_order_wt(self_pick_order_wt_list)
    non_self_pick_order_wt_list = merge_truck_order_wt(non_self_pick_order_wt_list)
    special_consumer_order_wt_list = merge_truck_order_wt(special_consumer_order_wt_list)
    return self_pick_order_wt_list, non_self_pick_order_wt_list, special_consumer_order_wt_list


def merge_truck_order_wt(order_wt_list: List[OrderWt]):
    """
    将拼车的多条记录合并为一条记录。根据捆绑单号bind_no判断是否有拼车的，如果捆绑单号bind_no不为空，则bind_no相同的为一车
    :param order_wt_list:
    :return:
    """
    # 根据捆绑单号bind_no是否为空，将order_wt_list分为2类：拼车、不拼车
    # 不拼车的
    single_order_wt_list = [order_wt for order_wt in order_wt_list if order_wt.bind_no is None]
    for single_order_wt in single_order_wt_list:
        # single_order_wt.consumer_set.add(single_order_wt.consumer)
        single_order_wt.items.append(single_order_wt)
    # 拼车的
    compose_order_wt_list = [order_wt for order_wt in order_wt_list if order_wt.bind_no is not None]
    # 将拼车的按捆绑单号bind_no分组
    compose_order_wt_dict = split_group_util(compose_order_wt_list, ['bind_no'])
    # 将拼车的处理成一车只有一条记录的结果
    single_compose_order_wt_list = []
    # 拼车的订单进行合并操作
    for value_list in compose_order_wt_dict.values():
        # 初始化一个OrderWt对象
        order_wt: OrderWt = BeanConvertUtils.copy_properties(value_list[0], OrderWt)
        # 将一个车的委托单号order_no拼接在一起
        order_wt.order_no = ','.join([str(order_wt.order_no) for order_wt in value_list])
        # 重量求和
        order_wt.total_weight = sum([order_wt.total_weight for order_wt in value_list])
        # # 收货单位
        # order_wt.consumer_set = set([order_wt.consumer for order_wt in value_list])
        # 加入子对象
        order_wt.items.extend(value_list)
        #
        single_compose_order_wt_list.append(order_wt)
    result_list = single_order_wt_list + single_compose_order_wt_list
    # 随机打乱
    random.shuffle(result_list)
    # 按照订单的优先级（YXJ10最低（默认），YXJ20普通，YXJ30加急）降序排序
    result_list.sort(key=lambda x: x.delegation_priority, reverse=True)
    return result_list
