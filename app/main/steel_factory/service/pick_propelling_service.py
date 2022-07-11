# -*- coding: utf-8 -*-
# Description:
# Created: luchengkai 2020/11/16 9:12
from threading import Thread

from celery.utils.log import get_task_logger

from app.main.steel_factory.rule import pick_propelling_rule, pick_propelling_label_rule, pick_save_result
from app.main.steel_factory.rule import pick_propelling_recall_screen_rule
from flask import json

# 获取celery执行器的日志记录器
from model_config import ModelConfig

logger = get_task_logger('celery_worker')


def propelling():
    """
    摘单计划推送入口
    :return:
    """
    """
    1.摘单计划筛选
    2.司机集获取(标签提取)
    3.司机集筛选(召回筛选)
    4.摘单计划与司机集合并
    """
    """1.摘单计划筛选"""
    res1 = None
    res2 = None
    # 待推送摘单计划列表
    propelling_list = pick_propelling_rule.pick_list_filter(ModelConfig.PICK_COMPANY_CONFIG["PCC1"][0],
                                                            ModelConfig.PICK_COMPANY_CONFIG["PCC1"][1])
    logger.info('摘单列表：' + json.dumps([i.as_dict() for i in propelling_list], ensure_ascii=False))
    # 摘单计划中已经存在的司机集
    exist_driver_list = pick_propelling_rule.pick_driver_list(ModelConfig.PICK_COMPANY_CONFIG["PCC1"][0],
                                                              ModelConfig.PICK_COMPANY_CONFIG["PCC1"][1])
    logger.info('已推送摘单的司机列表：' + json.dumps([i.as_dict() for i in exist_driver_list], ensure_ascii=False))

    # 待推送摘单计划中已存在的司机列表
    if propelling_list:
        # 摘单计划预处理
        propelling_list = pick_propelling_rule.init_propelling_list(propelling_list,
                                                                    ModelConfig.PICK_OBJECT['PO1'], exist_driver_list)
        """2.司机集获取(标签提取)"""
        wait_propelling_list = pick_propelling_label_rule.pick_label_extract(propelling_list)
        """3.司机集筛选(召回筛选)"""
        propelling_driver_list = pick_propelling_recall_screen_rule.pick_recall_screen(wait_propelling_list)
        # 结果保存到数据库
        Thread(target=pick_save_result.save_propelling_log, args=(propelling_driver_list,)).start()
        """4.后台交互"""
        res1, res2 = pick_propelling_rule.interaction_with_java(propelling_driver_list)
        # 将推送短信的司机列表写入日志
        Thread(target=pick_save_result.save_msg_log, args=(res2,)).start()
    return res1, res2


if __name__ == '__main__':
    propelling()
