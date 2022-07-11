# -*- coding: utf-8 -*-
# Description: 库存扣除服务
# Created: jjunf 2021/02/04
import copy
from datetime import datetime
from typing import List
import numpy as np
from flask import current_app, json
import pandas
import pandas as pd
from pandas._libs.tslibs.nattype import NaT
from app.main.steel_factory.dao.pick_stock_dao import pick_stock_dao
from app.main.steel_factory.entity.deduct_stock import DeductStock
from app.main.steel_factory.entity.stock import Stock
from app.util.bean_convert_utils import BeanConvertUtils
from app.util.split_group_util import split_group_util
from model_config import ModelConfig


def pick_deduct_stock_service(init_stock_list):
    """
    库存扣除服务
    :param init_stock_list:
    :return:
    """
    # 获取需要扣除的库存数据
    deduct_stock_list = deduct_stock_deal()
    # 将deduct_stock_list分为2类：
    # 1.一车次均有开单明细的库存 deduct_stock_list_with_detail；
    # 2.没有开单明细的库存、或者只有部分有开单明细 deduct_stock_list_without_detail（这部分在生成摘单计划后扣除）
    deduct_stock_list_with_detail, deduct_stock_list_without_detail = group_by_if_open_order(deduct_stock_list)
    # 扣除有开单明细的库存
    init_stock_list = deduct_operation(init_stock_list, deduct_stock_list_with_detail)
    return init_stock_list, deduct_stock_list_without_detail


def deduct_stock_deal():
    """
    获取需要扣除的库存数据
    :return:
    """
    # 查询需要扣除的库存数据
    deduct_stock_list = pick_stock_dao.select_pick_deduct_stock()
    # 日志
    current_app.logger.info('可能需要扣除的库存数据：' + json.dumps(deduct_stock_list, ensure_ascii=False))
    # 库存列表预处理
    df_deduct_stock = pd.DataFrame(deduct_stock_list)
    # 仓库名称、编码对照字典
    deliware_house_dict = {
        '大棒库(一棒)': 'B1',
        '小棒库(二棒)': 'B2',
        '#1热轧卷成品库': 'E1',
        '#2热轧卷成品库': 'E2',
        '#3热轧卷成品库': 'E3',
        '#4热轧卷成品库': 'E4',
        '#5热轧卷成品库': 'E5',
        '成品中间库': 'F1',
        '山东联储中间库': 'F2',
        '大H型钢成品库': 'H1',
        '小H型钢成品库': 'T1',
        '高线库': 'X1',
        '多头盘螺库': 'X2',
        '热轧#1580成品库': 'Z1',
        '热轧#2150成品': 'Z2',
        '精整1#成品库': 'Z4',
        '开平1、2#成品库': 'Z5',
        '开平3#成品库': 'Z8',
        '开平5#成品库': 'ZA',
        '精整2#成品库': 'ZC',
        'P5冷轧成品库': 'P5',
        'P6冷轧成品库': 'P6',
        'P7剪切成品1库': 'P7',
        'P8精整黑卷成品库': 'P8',
        'P8平整卷成品库': 'P8',
        '运输处临港东库': 'F10',
        '运输处临港西库': 'F20'
    }
    if not df_deduct_stock.empty:
        # 根据仓库名称deliware_house_name赋值仓库编码deliware_house
        df_deduct_stock['deliware_house'] = df_deduct_stock['deliware_house_name'].apply(
            lambda x: deliware_house_dict.get(x, x))
        # 对订单号的处理，在后3位前面加上‘-’
        df_deduct_stock['oritem_num'] = df_deduct_stock['oritem_num'].apply(
            lambda x: pandas.Series(str(x)).str.slice_replace(12, 12, "-"))
    # 初始化对象列表
    dic = df_deduct_stock.to_dict(orient="record")
    deduct_stock_list = [DeductStock(obj) for obj in dic]
    # 日志
    # current_app.logger.info('可能需要扣除的库存数据：' + json.dumps([i.as_dict() for i in deduct_stock_list], ensure_ascii=False))
    return deduct_stock_list


def group_by_if_open_order(deduct_stock_list):
    """
    根据一车次是否均有开单明细分为2类，并且找出该车次货物所在厂区('新产品'、'老区')
    :param deduct_stock_list:
    :return:
    """
    # 按车次号分组
    deduct_stock_dict = split_group_util(deduct_stock_list, ['trains_no'])
    # 一车次均有开单明细的库存
    deduct_stock_list_with_detail = []
    # 没有开单明细的库存、或者只有部分有开单明细
    deduct_stock_list_without_detail = []
    # 将库存按照是否已开单，即是否有开单明细，分为2类
    for one_train_deduct_stock_list in deduct_stock_dict.values():
        # 该车次是否均有开单明细的标志
        flag = True
        for deduct_stock in one_train_deduct_stock_list:
            # 如果没有开单明细、或者没有开单时间，flag置为False
            if (not deduct_stock.notice_num or not deduct_stock.oritem_num or
                    not deduct_stock.deliware_house or
                    deduct_stock.open_order_time is NaT or not deduct_stock.open_order_time):
                flag = False
        # 如果均有开单明细
        if flag:
            deduct_stock_list_with_detail.extend(one_train_deduct_stock_list)
        # 如果没有开单明细
        else:
            deduct_stock_list_without_detail.extend(one_train_deduct_stock_list)
    return deduct_stock_list_with_detail, deduct_stock_list_without_detail


def deduct_operation(init_stock_list: List[Stock], deduct_stock_list_with_detail: List[DeductStock]):
    """
    有开单明细的库存的扣除操作
    :param init_stock_list:
    :param deduct_stock_list_with_detail:
    :return:
    """
    # 初始化
    ModelConfig.be_deducted_stock_list = []
    # 如果init_stock_list为空
    if not init_stock_list:
        return init_stock_list
    # 找出日钢业务库操作时间最早的时间
    earliest_calculate_time = min([init_stock.calculate_time for init_stock in init_stock_list])
    # 扣除
    for deduct_stock in deduct_stock_list_with_detail:
        # 开单时间在日钢业务库操作最早时间之前的不用扣除
        if deduct_stock.open_order_time < earliest_calculate_time:
            continue
        # 扣除成功的标志
        flag = False
        # 如果匹配到发货通知单号、订单号、出库仓库，精确扣除
        for init_stock in copy.copy(init_stock_list):
            if (deduct_stock.notice_num == init_stock.notice_num
                    and deduct_stock.oritem_num == init_stock.oritem_num
                    and deduct_stock.deliware_house == init_stock.deliware_house):
                # 扣除件数
                init_stock.actual_number -= deduct_stock.actual_number
                # 扣除重量
                init_stock.actual_weight -= init_stock.piece_weight * deduct_stock.actual_number
                flag = True
                # 如果扣除完了，移除
                if init_stock.actual_number <= 0 or init_stock.actual_weight <= 0:
                    init_stock_list.remove(init_stock)
                """保存被扣除的库存"""
                stock: Stock = BeanConvertUtils.copy_properties(init_stock, Stock)
                stock.actual_number = deduct_stock.actual_number
                stock.actual_weight = init_stock.piece_weight * deduct_stock.actual_number
                stock.deliware_house = init_stock.deliware_house + '-' + deduct_stock.deliware_house
                ModelConfig.be_deducted_stock_list.append(stock)
                """保存被扣除的库存"""
                break
        # 如果上面没有精确扣除，按发货通知单号、订单号匹配（因为可能存在倒库的现象）
        if not flag:
            for init_stock in copy.copy(init_stock_list):
                # 按发货通知单号、订单号扣除
                if (deduct_stock.notice_num == init_stock.notice_num
                        and deduct_stock.oritem_num == init_stock.oritem_num):
                    # 扣除件数
                    init_stock.actual_number -= deduct_stock.actual_number
                    # 扣除重量
                    init_stock.actual_weight -= init_stock.piece_weight * deduct_stock.actual_number
                    # 如果扣除完了，移除
                    if init_stock.actual_number <= 0 or init_stock.actual_weight <= 0:
                        init_stock_list.remove(init_stock)
                    """保存被扣除的库存"""
                    stock: Stock = BeanConvertUtils.copy_properties(init_stock, Stock)
                    stock.actual_number = deduct_stock.actual_number
                    stock.actual_weight = init_stock.piece_weight * deduct_stock.actual_number
                    stock.deliware_house = init_stock.deliware_house + '-' + deduct_stock.deliware_house
                    ModelConfig.be_deducted_stock_list.append(stock)
                    """保存被扣除的库存"""
                    break
    return init_stock_list


if __name__ == '__main__':
    df = pd.Series(['张三一班00001', '李四二班00002', '王五三班00003'])
    # result = pd.DataFrame(df.map(lambda x: x.split()), columns=['姓名', '班级', '学号'])
    # result = df.str.split(pat=None, n=-1, expand=False)
    s = pandas.Series(['a_b_c'])
    print(s)
    result = pandas.Series('DH2101250254001').str.slice_replace(12, 12, "-")
    print(result)
    print(min(["2021-02-03 11:22:22", "2021-02-03 11:22:22", "2021-02-01 12:22:22"]))

    t_list = ["2021-02-03 11:22:22", NaT, "2021-02-03 11:22:22", "2021-02-01 12:22:22"]
    for t in t_list:
        if t and t is not NaT:
            t = datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
            print(t)
        elif t is NaT:
            print('111')
        else:
            print(1)

    if np.nan:
        print('nan')
    if None:
        print('N')
