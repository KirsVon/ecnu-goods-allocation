# -*- coding: utf-8 -*-
# Description: 创建摘单计划
# Created: jjunf 2021/3/30 15:15
from typing import List

from app.main.pipe_factory.entity.order_wt import OrderWt
from app.main.pipe_factory.entity.pick_task import PickTask
from app.main.pipe_factory.entity.pick_task_item import PickTaskItem
from app.util.bean_convert_utils import BeanConvertUtils
from app.util.split_group_util import split_group_util
from app.util.uuid_util import UUIDUtil


def create_pick_task_rule(order_wt_list: List[OrderWt], attr_list: List):
    """
    创建摘单计划：根据attr_list属性，将order_wt_list分组合并，委托单号order_no、总重量total_weight合并
    :param order_wt_list:
    :param attr_list:
    :return:
    """
    # 分组
    order_wt_dict = split_group_util(order_wt_list, attr_list)
    # 合并后的摘单计划
    pick_list: List[PickTask] = []
    # 拼车的订单进行合并操作
    for value_list in order_wt_dict.values():
        order_wt: OrderWt = value_list[0]
        # 初始化一个pick_task对象
        pick_task = PickTask()
        pick_task.consumer_name = order_wt.consumer_name
        pick_task.pick_id = UUIDUtil.create_id('pick')
        pick_task.company_id = order_wt.company_id
        pick_task.driver_pool_id = order_wt.driver_pool_id
        pick_task.driver_pool_name = order_wt.driver_pool_name
        pick_task.business_module_id = order_wt.business_module_id
        pick_task.start_point = order_wt.start_point
        # 将各车的委托单号order_no拼接在一起
        pick_task.order_no = ';'.join([order_wt.order_no for order_wt in value_list])
        # 重量求和
        pick_task.total_weight = sum([order_wt.total_weight for order_wt in value_list])
        # 车次数
        pick_task.truck_num = len(value_list)
        pick_task.province = order_wt.province
        pick_task.city = order_wt.city
        pick_task.district = order_wt.district
        pick_task.town = order_wt.town
        # pick_task.remark = order_wt.province + order_wt.city + order_wt.district  # + order_wt.town(town有None的)
        pick_task.remark = ''.join([order_wt.province if order_wt.province else '',
                                    order_wt.city if order_wt.city else ''])
        pick_task.r_vehicle = order_wt.r_vehicle
        pick_task.recommend_mobile = order_wt.recommend_mobile
        pick_task.recommend_driver = order_wt.recommend_driver
        consumer_list = []
        for order_wt in value_list:
            for order_wt_item in order_wt.items:
                consumer_list.append(order_wt_item.consumer)
            # consumer_list.extend(list(order_wt.consumer_set))
        pick_task.consumer = set(consumer_list)
        # 初始化一个pick_task_item对象
        pick_task_item: PickTaskItem = BeanConvertUtils.copy_properties(pick_task, PickTaskItem)
        # pick_task_item.remark += '(以上运费仅供参考,运费结算以实际装载重量计算)'
        # 在pick_task_item中加入委托订单子项
        pick_task_item.items.extend(value_list)
        # 在pick_task中加入pick_task_item子项
        pick_task.items = [pick_task_item]
        pick_list.append(pick_task)
    return pick_list
