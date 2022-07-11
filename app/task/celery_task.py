# -*- coding: utf-8 -*-
# Description: Celery任务示例
# Created: shaoluyu 2019/10/14
# Modified: shaoluyu 2019/10/16; shaoluyu 2019/10/25;
import json
import traceback

from celery.utils.log import get_task_logger

from app.main.pipe_factory.service.pick_dispatch_service import pick_cdpzjh_dispatch_service
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule.dict_convert_to_object_rule import convert_load_task
from app.main.steel_factory.rule.no_interest_count_rule import blacklist_timer
from app.main.steel_factory.service.pick_pipe_propelling_service import pipe_propelling
from app.main.steel_factory.service.pick_propelling_service import propelling
from app.main.steel_factory.service.pick_save_hour_stock_service import save_hour_stock
from app.main.steel_factory.service.pick_timing_issue_service import set_goods_issue
from app.main.steel_factory.service.single_delete_check_service import single_delete_check_service
from app.task.celery_app import celery
from app.test.jjunf.pick_optimization.pick_dispatch_optimization_service import dispatch_optimization_service
from model_config import ModelConfig
from report.route_weight_echo import route_weight_echo

# 获取celery执行器的日志记录器
logger = get_task_logger('celery_worker')


@celery.task(ignore_result=True)
def route_weight_check():
    try:
        logger.info('==========route_weight_echo_start=============')
        route_weight_echo()
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        logger.info('==========route_weight_echo_end===============')


@celery.task(ignore_result=True)
def push_message():
    try:
        logger.info('==========push_message_start=============')
        res1, res2 = propelling()
        logger.info(json.dumps(res1, ensure_ascii=False))
        logger.info(json.dumps(res2, ensure_ascii=False))
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        logger.info('==========push_message_end===============')


@celery.task(ignore_result=True)
def push_gc_message():
    try:
        logger.info('==========push_pipe_message_start=============')
        res1, res2 = pipe_propelling()
        logger.info(json.dumps(res1, ensure_ascii=False))
        logger.info(json.dumps(res2, ensure_ascii=False))
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        logger.info('==========push_pipe_message_end===============')


@celery.task(ignore_result=True)
def check_wt_status():
    try:
        logger.info('==========check_wt_status_start=============')
        res1, res2 = set_goods_issue()
        logger.info(json.dumps(res1, ensure_ascii=False))
        logger.info(json.dumps(res2, ensure_ascii=False))
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        logger.info('==========check_wt_status_end===============')


@celery.task(ignore_result=True)
def check_driver_behavior():
    try:
        logger.info('==========check_driver_behavior_start=============')
        blacklist_timer()
    except Exception as e:
        logger.error(str(e))
    finally:
        logger.info('==========check_driver_behavior_end===============')


@celery.task(ignore_result=True)
def save_hour_stock_():
    logger.info('==========start===stock==========')
    save_hour_stock()


@celery.task(ignore_result=True)
def dispatch_optimization(load_task_list, tail_list):
    logger.info('==========start===dispatch_optimization==========')
    load_task_list = convert_load_task(load_task_list)
    tail_list = [Stock(i) for i in tail_list]
    dispatch_optimization_service(load_task_list, tail_list)
    logger.info('==========end===dispatch_optimization==========')


@celery.task(ignore_result=True)
def pick_cdpzjh():
    try:
        logger.info('==========pick_cdpzjh_start=============')
        result = pick_cdpzjh_dispatch_service({"company_id": "C000000888", "data": ModelConfig.CDPZJH_REQUEST_FLAG,
                                               "business_module_id": "001"})
        logger.info(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        logger.info('==========pick_cdpzjh_end===============')


@celery.task(ignore_result=True)
def single_delete_check():
    try:
        logger.info('==========single_delete_check_start=============')
        single_delete_check_service()
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        logger.info('==========single_delete_check_end===============')


# def save_single_analysis():
#     try:
#         logger.info('==========save_single_analysis_start=============')
#
#     except Exception as e:
#         logger.error(traceback.format_exc())
#     finally:
#         logger.info('==========save_single_analysis_end===============')

# @celery.task()
# def print_log():
#     logger.info('==========start=============')
