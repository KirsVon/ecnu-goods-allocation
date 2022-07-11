# -*- coding: utf-8 -*-
# Description: 将列表stock_list按照属性attr1, attr2分组
# Created: jjunf 2020/09/29
import datetime
from collections import defaultdict

# 获取celery执行器的日志记录器
from celery.utils.log import get_task_logger

import config
from app.main.steel_factory.dao.pick_timing_issue_dao import pick_timing_issue_dao
from app.main.steel_factory.rule import pick_data_format_rule
from app.util.rest_template import RestTemplate

# 获取celery执行器的日志记录器
logger = get_task_logger('celery_worker')


def get_batch_time(now_minute):
    # flag = pick_timing_issue_dao.get_batch_info(now_hour)
    if not now_minute % 5:
        return True
    return False


def get_batch_line():
    line_list = pick_timing_issue_dao.get_batch_line()
    return line_list


def change_wt_status(line_list):
    correct_list = []
    res = {}
    if not line_list:
        return correct_list, res
    """判断条件：当前仓库中的实际库存 - 已派车库存 - 就绪中库存 - 摘单中的库存 > 当前委托单数量"""
    # 查询 当前委托单数量
    # line_list = ['500100000', '510100000', '510500000', '530100000']
    current_wt_list = pick_timing_issue_dao.get_current_wt_info(line_list)
    # 只有 自提 或 管厂代收&指定司机池 的委托单，走自动下发
    consignee_no_list = pick_timing_issue_dao.get_consignee_no_list()
    current_wt_list = [item for item in current_wt_list if
                       (item.business_nature == 'YWXZ50') or
                       (item.business_nature == 'YWXZ10' and item.consignee_company_id in consignee_no_list)]

    # logger.info("wt_dict: " + str(current_wt_dict))
    # 查询 当前仓库中的实际库存
    # current_wt_list = [item for item in current_wt_list if item.order_no == 'WT210524000002']
    current_wt_list = pick_timing_issue_dao.get_current_stock_info(current_wt_list)
    # logger.info("current_dict: " + str(current_wt_dict))
    if not current_wt_list:
        return correct_list, res

    # 查询 已派车库存
    current_wt_list = pick_timing_issue_dao.get_have_push_stock_info(current_wt_list)
    # logger.info("have_push_dict: " + str(current_wt_dict))
    if not current_wt_list:
        return correct_list, res

    # 查询 就绪中、摘单中库存
    current_wt_list = pick_timing_issue_dao.get_ready_push_stock_info(current_wt_list)
    # logger.info("jxz-zdz_dict: " + str(current_wt_dict))
    if not current_wt_list:
        return correct_list, res

    # 筛选出 可发库存 > 代发库存 的委托单
    correct_list = []  # 符合条件的委托单
    no_right_id_list = []  # 不符合条件的委托单
    no_right_bind_list = []     # 不符合条件的捆绑单号
    for current_wt in current_wt_list:
        if (current_wt.current_stock_total_sheet - current_wt.have_push_total_sheet -
                current_wt.ready_push_total_sheet >= current_wt.wait_compare_total_sheet
                and current_wt.current_stock_total_sheet):
            correct_list.append(current_wt)
        else:
            no_right_id_list.append(current_wt.order_no)
            if current_wt.bind_no:
                no_right_bind_list.append(current_wt.bind_no)
    # logger.info("correct_list: " + ''.join(correct_list))

    # 可能存在情况：一个委托单存在多个子委托单，某些子委托单符合条件，某些不符合
    correct_list = [wt_order for wt_order in correct_list if
                    (wt_order.order_no not in no_right_id_list) and
                    (wt_order.bind_no not in no_right_bind_list)]
    if not correct_list:
        return correct_list, res

    # 修改委托单状态
    try:
        url = config.get_active_config().COMMISSION_URL + "/order/updIntelligentStatus"
        post_list = pick_data_format_rule.to_trans_batch_service(correct_list)
        res = RestTemplate.do_post(url, post_list)
        logger.info("updIntelligentStatus: " + str(res))
        return correct_list, res
    except Exception as e:
        logger.error('updIntelligentStatus报错: ' + str(e))
        return [], {}


def get_issue_time(now_time):
    issue_list = pick_timing_issue_dao.get_issue_info()
    for issue in issue_list:
        if now_time == issue.get('push_time', ''):
            return True
    return False


def push_wait_issue_wt_info():
    # 直接下发委托单
    # get_wait_push_wt_info = pick_timing_issue_dao.get_wait_push_wt_info()
    # if not get_wait_push_wt_info:
    #     return
    try:
        url = config.get_active_config().COMMISSION_URL + "/order/distributeIntelligence"
        # for order in get_wait_push_wt_info:
        post_dic = pick_data_format_rule.to_trans_push_service()
        res = RestTemplate.do_post(url, post_dic)
        logger.info("distributeIntelligence: " + str(res))
        return res
    except Exception as e:
        logger.error('distributeIntelligence报错: ' + str(e))
        return {}


if __name__ == '__main__':
    # get_issue_time("16", "39")
    # push_wait_issue_wt_info()
    # change_wt_status()
    a = 6 % 5
    print(a)
