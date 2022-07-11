# -*- coding: utf-8 -*-
# Description: 智能下发服务
# Created: luchengkai 2021/05/10
import datetime
from threading import Thread

from app.main.steel_factory.rule import pick_timing_issue_rule, pick_save_result


def set_goods_issue():
    res1 = {}
    res2 = {}
    # 获取当前时间
    now = datetime.datetime.now()
    now_minute = now.minute
    now_time = now.strftime("%H:%M")

    """定时检查初始状态的委托单，根据库存判断是否可以修改状态"""
    # 判断是否到达委托单状态修改时间
    is_batch = pick_timing_issue_rule.get_batch_time(now_minute)
    # is_batch = True
    # 开始修改委托单状态
    if is_batch:
        line_list = pick_timing_issue_rule.get_batch_line()
        change_wt_list, res1 = pick_timing_issue_rule.change_wt_status(line_list)
        Thread(target=pick_save_result.save_batch_wt_log, args=(change_wt_list,)).start()

    """定时查询智能调度状态为“就绪中”的单子"""
    # 判断是否到达智能下发时间
    is_issue = pick_timing_issue_rule.get_issue_time(now_time)
    # is_issue = True
    if not is_issue:
        return res1, res2
    # 下发就绪中的单子
    res2 = pick_timing_issue_rule.push_wait_issue_wt_info()
    return res1, res2


if __name__ == '__main__':
    set_goods_issue()
