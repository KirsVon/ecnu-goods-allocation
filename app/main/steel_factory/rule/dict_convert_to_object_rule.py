# -*- coding: utf-8 -*-
# Description: 将字典转换成对象的方法
# Created: jjunf 2021/3/30 11:31
from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock


def convert_load_task(load_task_dict):
    """
    将字典转换成load_task对象
    :param load_task_dict:
    :return:
    """
    load_task_list = []
    for item in load_task_dict:
        load_task = LoadTask(item)
        load_task.items = [LoadTaskItem(i) for i in load_task.items]
        for load_task_item in load_task.items:
            load_task_item.stock = Stock(load_task_item.stock)
        load_task_list.append(load_task)
    return load_task_list
