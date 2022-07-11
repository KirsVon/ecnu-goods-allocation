# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12
import copy
import json
# from typing import Dict
from collections import defaultdict
from typing import List

import pandas as pd
from flask import current_app, g

from app.main.steel_factory.dao.loading_detail_dao import loading_detail_dao
from app.main.steel_factory.dao.out_stock_queue_dao import out_stock_queue_dao
from app.main.steel_factory.dao.single_stock_dao import stock_dao
from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
# from app.main.steel_factory.service import redis_service
from app.main.steel_factory.service.single_set_priority_service import set_priority_service
# from app.util.generate_id import HashKey
from app.util.get_weight_limit import get_lower_limit
from app.util.split_group_util import split_group_util
from model_config import ModelConfig

remark_num_set = set()


def get_stock_id(obj):
    """
    根据库存信息生成每条库存的唯一id
    """
    if isinstance(obj, Stock):
        return hash(obj.notice_num + obj.oritem_num + obj.deliware_house)
    elif isinstance(obj, LoadTaskItem):
        return hash(obj.notice_num + obj.oritem_num + obj.outstock_code)


def get_stock(truck):
    """
    根据车辆目的地和可运货物返回库存列表
    """
    # 是否是测试：测试时改为True，将读取app.test.singleGoodsAllocation.data_set包中SingleGoodsAllocationTestDataSet类中的测试数据
    test = False
    # 根据品种查询库存
    if test:
        all_stock_list = json.loads(SingleGoodsAllocationTestDataSet.all_stock_list)
    else:
        all_stock_list = stock_dao.select_stock(truck)
    # 打印库存日志
    #current_app.logger.info("库存数据：" + json.dumps([i for i in all_stock_list], ensure_ascii=False))
    if not all_stock_list:
        return []
    '''去除等待数较高的出库仓库-start'''
    df1 = pd.DataFrame(ModelConfig.WAREHOUSE_WAIT_DICT)
    # 查询各仓库排队信息：结果为字典{'仓库号': [仓库号列表], '排队车数量': [排队车数量列表]}
    if test:
        out_stock_dict = SingleGoodsAllocationTestDataSet.out_stock_dict
    else:
        out_stock_dict = out_stock_queue_dao.select_out_stock_queue()
    # 打印仓库排队日志
    #current_app.logger.info("仓库排队：" + json.dumps(out_stock_dict, ensure_ascii=False))
    df2 = pd.DataFrame(out_stock_dict)
    df = pd.merge(df1, df2, how='left', on='stock_name')
    df = df.dropna()
    df = df.drop(df[df['truck_count_real'] < df['truck_count_std']].index)
    out_stock_list = [i for i in df['stock_name']]
    # 打印仓库排队超标的仓库日志
    #current_app.logger.info("仓库排队超标的仓库：" + json.dumps(out_stock_list, ensure_ascii=False))
    # 去除等待数较高的出库仓库，暂不往该仓库开单
    if out_stock_list:
        all_stock_list = [i for i in all_stock_list if i.get('deliware_house') not in out_stock_list]
    '''去除等待数较高的出库仓库-end'''
    # 获取已开装车清单信息、预装车清单信息、最大更新时间、开单推荐但未经过确认
    if test:
        loading_detail_list = SingleGoodsAllocationTestDataSet.loading_detail_list
    else:
        loading_detail_list = loading_detail_dao.select_loading_detail(truck)
    # 打印需要扣除的日志
    #current_app.logger.info("需要扣除：" + json.dumps([i for i in loading_detail_list], ensure_ascii=False))
    # 扣除操作
    for stock_dict in all_stock_list:
        # 找出库存中被开单的子项
        temp_list = [j for j in loading_detail_list if j.get('notice_num') == stock_dict.get('notice_num')
                     and (j.get('oritem_num') if '-' in j.get('oritem_num') else
                          j.get('oritem_num')[0:-3] + '-' + j.get('oritem_num')[-3:]) == stock_dict.get('oritem_num')
                     and j.get('outstock_name') == stock_dict.get('deliware_house')]
        if temp_list:
            for i in temp_list:
                stock_dict['CANSENDWEIGHT'] = float(stock_dict.get('CANSENDWEIGHT', 0)) - float(i.get('weight', 0))
                stock_dict['CANSENDNUMBER'] = int(stock_dict.get('CANSENDNUMBER', 0)) - int(i.get('count', 0))
    if not all_stock_list:
        return []
    # 库存预处理
    target_stock_list = deal_stock(all_stock_list, truck)
    return target_stock_list


def deal_stock(all_stock_list, truck: Truck):
    # 获取库存列表
    df_stock = pd.DataFrame(all_stock_list)
    # 需与卸货的订单地址，数据库中保存的地址及经纬度合并
    # df_stock = merge_stock(df_stock)
    df_stock["CANSENDWEIGHT"] = df_stock["CANSENDWEIGHT"].astype('float64')
    df_stock["CANSENDNUMBER"] = df_stock["CANSENDNUMBER"].astype('int64')
    df_stock["NEED_LADING_WT"] = df_stock["NEED_LADING_WT"].astype('float64')
    df_stock["NEED_LADING_NUM"] = df_stock["NEED_LADING_NUM"].astype('int64')
    df_stock["OVER_FLOW_WT"] = df_stock["OVER_FLOW_WT"].astype('float64')
    df_stock["waint_fordel_number"] = df_stock["waint_fordel_number"].astype('int64')
    df_stock["waint_fordel_weight"] = df_stock["waint_fordel_weight"].astype('float64')
    # 根据公式，计算实际可发重量，实际可发件数
    df_stock["actual_weight"] = (df_stock["CANSENDWEIGHT"] + df_stock["NEED_LADING_WT"]) * 1000
    df_stock["actual_number"] = df_stock["CANSENDNUMBER"] + df_stock["NEED_LADING_NUM"]
    # 根据公式计算件重
    df_stock["piece_weight"] = round(df_stock["actual_weight"] / df_stock["actual_number"])
    # 需短溢处理
    df_stock["OVER_FLOW_WT"] = df_stock["OVER_FLOW_WT"] * 1000
    df_stock.loc[df_stock["OVER_FLOW_WT"] > 0, ["actual_number"]] = df_stock["actual_number"] + (
            -df_stock["OVER_FLOW_WT"] // df_stock["piece_weight"])
    df_stock["actual_weight"] = df_stock["piece_weight"] * df_stock["actual_number"]
    # 计算待生产重量
    df_stock["waint_fordel_weight"] = df_stock["waint_fordel_weight"] * 1000
    df_stock["wait_product_weight"] = df_stock["waint_fordel_weight"] - df_stock["actual_weight"]

    def rename(row):
        # global flag
        # if not flag:
        #     flag = True
        #     return row
        if row['big_commodity_name'].find('新产品') != -1 or row['big_commodity_name'].find('老区') != -1:
            return row
        # 将所有黑卷置成卷板
        if row['big_commodity_name'] == '黑卷':
            row['big_commodity_name'] = '卷板'
        # 如果是西区开平板，则改为新产品-冷板
        if row['deliware_house'].startswith("P") and row['big_commodity_name'] == '开平板':
            row['big_commodity_name'] = '新产品-冷板'
        # 如果是西区非开平板，则品名前加新产品-
        elif row['deliware_house'].startswith("P") and row['big_commodity_name'] != '开平板':
            row['big_commodity_name'] = '新产品-' + row['big_commodity_name']
        # 如果是外库，且是西区品种，则品名前加新产品-
        elif (row['deliware_house'].find('F10') != -1 or row['deliware_house'].find('F20') != -1) and row[
            'big_commodity_name'] in ['白卷', '窄带', '冷板']:
            row['big_commodity_name'] = '新产品-' + row['big_commodity_name']
        # 其余全部是老区-
        else:
            row['big_commodity_name'] = '老区-' + row['big_commodity_name']
        return row

    df_stock = df_stock.apply(rename, axis=1)
    # 窄带按捆包数计算，实际可发件数 = 捆包数
    df_stock.loc[(df_stock["big_commodity_name"] == "新产品-窄带") & (df_stock["PACK_NUMBER"] > 0), ["actual_number"]] = \
        df_stock["PACK_NUMBER"]
    # 单独计算窄带的件重
    df_stock.loc[
        (df_stock["big_commodity_name"] == "新产品-窄带") & (df_stock["PACK_NUMBER"] > 0), ["piece_weight"]] = round(
        df_stock["actual_weight"] / df_stock["actual_number"])
    # 将终点统一赋值到实际终点，方便后续处理联运
    df_stock["actual_end_point"] = df_stock["dlv_spot_name_end"]
    # 入库仓库除U289-绿色通道库外，其余set到actual_end_point，港口批号set到standard_address
    df_stock.loc[(df_stock["deliware"].str.startswith("U")) & (df_stock["deliware"] != ModelConfig.RG_U289),
                 ["actual_end_point"]] = df_stock["deliware"]
    df_stock.loc[(df_stock["deliware"].str.startswith("U")) & (df_stock["deliware"] != ModelConfig.RG_U289),
                 ["standard_address"]] = df_stock["port_num"]
    df_stock.loc[(df_stock["port_name_end"].isin(ModelConfig.RG_PORT_NAME_END_LYG)) & (
        df_stock["big_commodity_name"].isin(ModelConfig.RG_COMMODITY_LYG)), ["actual_end_point"]] = "U288-岚北港口库2LYG"
    # 筛选
    df_stock = stock_filter(df_stock, truck)
    if df_stock.empty:
        return []
    df_stock.loc[df_stock["standard_address"].isnull(), ["standard_address"]] = df_stock["detail_address"]
    dic = df_stock.to_dict(orient="records")
    init_stock_list = [Stock(i) for i in dic]
    # 设置库存的优先级别
    set_priority_service(init_stock_list, truck)
    # 存放stock的结果
    stock_list = []
    # # 急发字典：{订单：{报道号1：1，报道号2：1}}
    # priority_dict = redis_service.get_priority_dict()
    for stock in init_stock_list:
        # 如果可发小于待发，并且待发在标载范围内，就不参与配载
        if (stock.actual_number < stock.waint_fordel_number and get_lower_limit(
                stock.big_commodity_name) <= stock.waint_fordel_weight <= ModelConfig.RG_MAX_WEIGHT):
            # 打印日志
            #current_app.logger.info("不参与配载的货物：" + json.dumps(stock.as_dict(), ensure_ascii=False))
            continue
        stock.parent_stock_id = get_stock_id(stock)
        stock.actual_number = int(stock.actual_number)
        stock.actual_weight = int(stock.actual_weight)
        stock.piece_weight = int(stock.piece_weight)
        stock.wait_product_weight = int(stock.wait_product_weight)
        stock_list.append(stock)
        # stock.priority = ModelConfig.RG_PRIORITY.get(stock.priority, 4)
        # # 如果stock发运车次数 >= 设置车次数，将priority设置为4，如果报道号已经被分过急发货物，将对应的redis记录删除
        # key = HashKey.get_key([stock.notice_num, stock.oritem_num, stock.contract_no])
        # schedule_dict: Dict = priority_dict.get(key, None)
        # if schedule_dict:
        #     schedule_dict.pop(truck.schedule_no, 404)
        #     if len(schedule_dict) >= stock.load_task_count:
        #         stock.priority = 4
        # 组数
        # target_group_num = 0
        # # 临时组数
        # temp_group_num = 0
        # # 最后一组件数
        # target_left_num = 0
        # # 一组几件
        # target_num = 0
        # for weight in range(get_lower_limit(stock.big_commodity_name), ModelConfig.RG_MAX_WEIGHT + 1000, 1000):
        #     # 一组几件
        #     num = weight // stock.piece_weight
        #     if num < 1 or num > stock.actual_number:
        #         target_num = num
        #         continue
        #     # 如果还没轮到最后，并且标准组重量未达到标载，就跳过
        #     if weight < ModelConfig.RG_MAX_WEIGHT and (num * stock.piece_weight) < get_lower_limit(
        #             stock.big_commodity_name):
        #         continue
        #     # 组数
        #     group_num = stock.actual_number // num
        #     # 最后一组件数
        #     left_num = stock.actual_number % num
        #     # 如果最后一组符合标载条件，临时组数加1
        #     temp_num = 0
        #     if (left_num * stock.piece_weight) >= get_lower_limit(stock.big_commodity_name):
        #         temp_num = 1
        #     # 如果分的每组件数更多，并且组数不减少，就替换
        #     if (group_num + temp_num) >= temp_group_num:
        #         target_group_num = group_num
        #         temp_group_num = group_num + temp_num
        #         target_left_num = left_num
        #         target_num = num
        # # 标准件每组件数
        # count_list = [target_num] * target_group_num
        # # 如果还有尾货
        # if target_left_num:
        #     # 将每组进行检查
        #     for group_index in range(target_group_num):
        #         # 当每组件数*件重<=最大重量时
        #         while (((count_list[group_index] + 1) * stock.piece_weight <= ModelConfig.RG_MAX_WEIGHT)
        #                and target_left_num > 0):
        #             # 当前组件数+1
        #             count_list[group_index] += 1
        #             target_left_num -= 1
        # # 按33000将货物分成若干份
        # # num = (truck.load_weight + ModelConfig.RG_SINGLE_UP_WEIGHT) // stock.piece_weight
        # # 首先去除 件重大于33000的货物
        # if target_num < 1:
        #     continue
        # # 其次如果可装的件数大于实际可发件数，不用拆分，直接添加到stock_list列表中
        # elif target_num > stock.actual_number:
        #     # 可装的件数大于实际可发件数，并且达到标载
        #     if stock.actual_weight >= get_lower_limit(stock.big_commodity_name):
        #         stock.limit_mark = 1
        #     else:
        #         stock.limit_mark = 0
        #     stock_list.append(stock)
        # # 最后不满足则拆分
        # else:
        #     # limit_mark = 1
        #     for q in range(int(target_group_num)):
        #         copy_2 = copy.deepcopy(stock)
        #         copy_2.actual_weight = target_num * stock.piece_weight
        #         copy_2.actual_number = int(target_num)
        #         if copy_2.actual_weight < get_lower_limit(stock.big_commodity_name):
        #             copy_2.limit_mark = 0
        #         else:
        #             copy_2.limit_mark = 1
        #
        #         stock_list.append(copy_2)
        #     if target_left_num:
        #         copy_1 = copy.deepcopy(stock)
        #         copy_1.actual_number = int(target_left_num)
        #         copy_1.actual_weight = target_left_num * stock.piece_weight
        #         if copy_1.actual_weight < get_lower_limit(stock.big_commodity_name):
        #             copy_1.limit_mark = 0
        #         else:
        #             copy_1.limit_mark = 1
        #         stock_list.append(copy_1)
    # # 更新
    # redis_service.set_priority_dict(priority_dict)
    # 按照优先发运和最新挂单时间排序
    # stock_list.sort(key=lambda x: (x.priority, x.latest_order_time, x.actual_weight * -1), reverse=False)
    stock_list = stock_sort(stock_list)
    return stock_list


def stock_filter(df_stock, truck):
    """
    货物筛选函数
    """
    # 筛选出大于0的数据
    df_stock = df_stock.loc[
        (df_stock["actual_weight"] > 0) & (df_stock["actual_number"] > 0) & (
            df_stock["latest_order_time"].notnull())]

    # # 异常仓库的货物不参与配载
    # abnormal_deliware_house_list = stock_dao.select_abnormal_deliware_house()
    # if abnormal_deliware_house_list:
    #     df_stock = df_stock[~df_stock["deliware_house"].isin(abnormal_deliware_house_list)]

    # 暂时筛除流向确认人是WL00075的货
    df_stock = df_stock.loc[df_stock["flow_confirm_person"] != "WL00075"]

    # 如果报道品种为新产品-白卷，并且备注中没有包含草垫子，则库存中去掉小品名为热镀锌钢卷的货，不参与配载
    if truck.big_commodity_name == "新产品-白卷" and "草垫子" not in truck.remark:
        df_stock = df_stock.loc[df_stock["commodity_name"] != "热镀锌钢卷"]

    # 按车辆流向(区县)筛选，青岛流向可不按报道区县开单；外贸的不按流向筛选
    if truck.actual_end_point and not truck.foreign_trade_deliware:
        # 青岛市的特殊处理
        if truck.city == '青岛市':
            # 先按区县筛选或入库仓库是U289-绿色通道库的情况下详细地址包括报道区县
            temp_df_stock = df_stock.loc[(df_stock['actual_end_point'].str.find(truck.actual_end_point[0][:-1]) != -1)
                                         | (
                                                 (df_stock["deliware"] == ModelConfig.RG_U289) &
                                                 (df_stock['detail_address'].str.find(
                                                     truck.actual_end_point[0][:-1]) != -1))
                                         ]
            sum_weight = 0
            if not temp_df_stock.empty:
                # 计算货物总重量
                sum_weight = temp_df_stock['actual_weight'].sum()
            # 如果指定区县无货或者货物重量不足，则直接筛选青岛市的货物
            if temp_df_stock.empty or (sum_weight < get_lower_limit(
                    truck.big_commodity_name) and sum_weight < truck.load_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT):
                df_stock = df_stock.loc[df_stock['city'] == truck.city]
            else:
                df_stock = temp_df_stock
        else:
            df_stock = df_stock.loc[(df_stock['actual_end_point'].str.find(truck.actual_end_point[0][:-1]) != -1)
                                    | (
                                            (df_stock["deliware"] == ModelConfig.RG_U289) &
                                            (df_stock['detail_address'].str.find(
                                                truck.actual_end_point[0][:-1]) != -1))
                                    ]

    # 按流向筛选客户（从数仓数据库中配置）
    try:
        df_stock = deal_special_consumer(df_stock, truck)
    except Exception as e:
        # 打印日志
        #current_app.logger.error("按客户进行筛选出错：" + str(e))
        print(1)

    # 按车辆流向筛选，临沂不开品相为35，38的货物
    if truck.city == '临沂市':
        df_stock = df_stock.loc[(df_stock['prod_level_code'] != 35) & (df_stock['prod_level_code'] != 38)]

    # 按备注进行筛选
    try:
        if (truck.city in ModelConfig.SINGLE_DESIGNATE_CONSUMER_CITY
                or '全部' in ModelConfig.SINGLE_DESIGNATE_CONSUMER_CITY):
            df_stock = deal_truck_remark(df_stock, truck)
    except Exception as e:
        # 打印日志
        #current_app.logger.error("按备注进行筛选出错：" + str(e))
        print(1)

    # 处理被删除后需要锁定的单子
    try:
        df_stock = deal_lock_order(df_stock)
    except Exception as e:
        # 打印日志
        #current_app.logger.error("处理被删除后需要锁定的单子出错：" + str(e))
        print(1)
    return df_stock


def stock_sort(stock_list: List[Stock]):
    """
    库存排序：优先级、挂单时间、重量（件重）
    :param stock_list:
    :return:
    """
    if not stock_list:
        return stock_list
    # 排序后的结果
    result_list: List[Stock] = []
    # 按照优先发运、最新挂单时间、重量排序
    stock_list.sort(key=lambda x: (x.priority, x.latest_order_time, x.actual_weight * -1), reverse=False)
    # 按照优先级分组
    stock_dict = split_group_util(stock_list, ['priority'])
    # 将件重大于ModelConfig.RG_MAX_WEIGHT/2的货物，不按挂单时间排序，直接放到其他货物的前面
    for temp_stock_list in stock_dict.values():
        # 找出件重大于设定下限的货物
        max_weight_list = [stock for stock in temp_stock_list
                           if
                           ModelConfig.SINGLE_BIG_PIECE_WEIGHT < stock.piece_weight < ModelConfig.RG_J_PIECE_MIN_WEIGHT]
        # 按件重排序
        max_weight_list.sort(key=lambda x: x.piece_weight, reverse=True)
        # 剩下的货物
        min_weight_list = [stock for stock in temp_stock_list if stock not in max_weight_list]
        result_list.extend(max_weight_list + min_weight_list)
    return result_list


def deal_special_consumer(df_stock, truck):
    """
    按流向筛选客户（从数仓数据库中配置）
    :param df_stock:
    :param truck:
    :return:
    """
    # 查询条件
    condition = ','.join([truck.city, truck.dlv_spot_name_end])
    '''1.只筛选哪些客户的货'''
    if condition in ModelConfig.SINGLE_KEEP_CONSUMER.keys():
        df_stock = df_stock.loc[df_stock['consumer'].isin(ModelConfig.SINGLE_KEEP_CONSUMER.get(condition))]
        # 打印日志
        #current_app.logger.info("筛选的客户：" + json.dumps(ModelConfig.SINGLE_KEEP_CONSUMER.get(condition), ensure_ascii=False))
    '''2.筛掉哪些客户的货'''
    if condition in ModelConfig.SINGLE_REJECT_CONSUMER.keys():
        df_stock = df_stock.loc[~df_stock['consumer'].isin(ModelConfig.SINGLE_REJECT_CONSUMER.get(condition))]
        # 打印日志
        #current_app.logger.info("筛掉的客户：" + json.dumps(ModelConfig.SINGLE_REJECT_CONSUMER.get(condition), ensure_ascii=False))
    return df_stock


def deal_truck_remark(df_stock, truck: Truck):
    """
    根据车的备注来筛选货物
    :param df_stock:
    :param truck:
    :return:
    """
    if not truck.remark:
        return df_stock
    # 对车的备注的处理
    remark = str(truck.remark)
    # 特殊判断是否是华龙库
    if truck.city == '青岛市' and '中集华龙库' not in remark:
        df_stock = df_stock.loc[df_stock['detail_address'] != '山东省青岛市胶州市海尔大道与云溪路交叉口向东300米胶州华龙库']
    remark = remark.split(',')[-1]
    g.remark_num_set = set()
    # 备注里面没有除了车辆配件之外的其他备注
    if remark in ModelConfig.RG_FITTINGS_OF_VEHICLE:
        return df_stock
    # 识别备注中的钢卷数量
    num_dict = {'1': 1, '一': 1, '2': 2, '二': 2, '两': 2, '俩': 2, '3': 3, '三': 3, '4': 4, '四': 4, '5': 5, '五': 5}
    if '大卷' in remark:
        g.remark_num_set.add(1)
    import re
    s = re.findall(r"(.?)[副,个,卷]", remark)
    for i in s:
        num = num_dict.get(i, 0)
        if num:
            g.remark_num_set.add(num)
    if g.remark_num_set and len(g.remark_num_set) > 0:
        #current_app.logger.info("匹配到的备注钢卷数量：" + json.dumps(list(g.remark_num_set), ensure_ascii=False))
        print(1)
    # 查询该流向的历史常用备注简写
    history_remark_simplify_list = stock_dao.select_attribute_simplify('C000000882', '020', truck.province, truck.city)
    # 打印日志
    #current_app.logger.info(truck.province + truck.city + "常用的历史备注简写：" + json.dumps(history_remark_simplify_list, ensure_ascii=False))
    # 是否指定客户
    flag = False
    # # 查找是否存在简写对应的情况
    # remark_dict = {}
    # 简写备注的字典列表(可能有一个简写备注对应多个详细备注的情况)：键为属性(consumer或者detail_address)；值为remark_dict列表
    remark_dict_list = defaultdict(list)
    for remark_dict in history_remark_simplify_list:
        # 匹配成功
        if remark_dict.get('short_attribute', '') in remark:
            flag = True
            # 打印日志
            #current_app.logger.info("匹配到的简写备注：" + json.dumps(remark_dict, ensure_ascii=False))
            remark_dict_list[remark_dict['attribute']].append(remark_dict)
            # break
    # 如果没指定客户
    if not flag:
        return df_stock
    # 对于备注中可能有多个简写备注的处理：筛选出满足所有简写条件的货物
    for value_list in remark_dict_list.values():
        # 属性：consumer或者detail_address
        attribute = value_list[0]['attribute']
        # 详细属性列表
        detail_attribute_list = [value['detail_attribute'] for value in value_list]
        # 先按照指定的客户筛选，没货后放宽条件，开其他客户的货
        if ModelConfig.SINGLE_DESIGNATE_CONSUMER_FLAG:
            # temp_df_stock = df_stock.loc[df_stock[remark_dict.get('attribute')] == remark_dict.get('detail_attribute')]
            temp_df_stock = df_stock.loc[df_stock[attribute].isin(detail_attribute_list)]
            sum_weight = 0
            if not temp_df_stock.empty:
                # 计算货物总重量
                sum_weight = temp_df_stock['actual_weight'].sum()
            # 打印日志
            #current_app.logger.info("筛选后的货物总重量(t)：" + json.dumps(sum_weight / 1000, ensure_ascii=False))
            # 如果筛选后有货并且够一车，则按条件筛选
            if not temp_df_stock.empty and (sum_weight > get_lower_limit(
                    truck.big_commodity_name) or sum_weight > truck.load_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT):
                df_stock = temp_df_stock
        # 完全按照指定的客户筛选
        else:
            # df_stock = df_stock.loc[df_stock[remark_dict.get('attribute')] == remark_dict.get('detail_attribute')]
            df_stock = df_stock.loc[df_stock[attribute].isin(detail_attribute_list)]
    return df_stock


def deal_lock_order(df_stock):
    """
    处理被删除后需要锁定的单子
    :param df_stock:
    :return:
    """
    if ModelConfig.SINGLE_LOCK_ORDER_FLAG and ModelConfig.SINGLE_LOCK_ORDER:
        # df_stock.apply(lambda row: print(row['notice_num'] + ',' + row['oritem_num'] + ',' + row['deliware_house']),
        #                axis=1)
        df_stock = df_stock.loc[
            ~(df_stock['notice_num'] + ',' + df_stock['oritem_num'] + ',' + df_stock['deliware_house']).isin(
                ModelConfig.SINGLE_LOCK_ORDER)]
    return df_stock
