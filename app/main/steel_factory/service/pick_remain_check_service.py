# -*- coding: utf-8 -*-
# Description: 摘单时判断剩余车次数
# Created: jjunf 2021/3/17 17:33
from app.main.steel_factory.dao.pick_remain_check_dao import pick_remain_check_dao
from app.main.steel_factory.entity.remain_check import RemainCheck
from app.main.steel_factory.rule.pick_remain_check_filter import check_filter
from app.util.result import Result


def check(json_data):
    """
    摘单时判断剩余车次数入口：输入当前摘单相关信息；返回True：当前摘单还有剩余，可摘单；False：当前摘单没有剩余，不可摘单
    :param json_data:
    :return:
    """
    # 转成对象
    remain_check = RemainCheck(json_data)
    # 校验必须字段：摘单号、剩余车次、城市、区县、品种
    if (remain_check.pickup_no and remain_check.remain_truck_num and remain_check.city
            and remain_check.district and remain_check.big_commodity_name):
        remain_check = check_filter(remain_check)
    # 保存日志记录
    pick_remain_check_dao.save_remain_check(remain_check)
    return Result.success(data=remain_check.result)
