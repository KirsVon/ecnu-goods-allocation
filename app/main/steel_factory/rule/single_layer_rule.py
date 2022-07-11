import math
from typing import List, Dict
from flask import current_app,g
import json

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.goods_filter_rule import goods_filter
from app.main.steel_factory.rule.split_rule import split
from app.util.enum_util import DispatchType, LoadTaskType
from app.util.get_weight_limit import get_lower_limit
from app.util.math_util import MathUtil
from app.util.round_util import round_util
from model_config import ModelConfig


def layer_filter(stock_list: List, stock_dict: Dict, truck: Truck):
    """
    按层次分货
    第一层：一装一卸
    第二层：同库两装一卸
    第三层：异库两装一卸
    第四层：一装两卸
    第五层：同库两装两卸
    """
    max_weight = truck.load_weight
    tail_list = stock_dict['tail']
    huge_list = stock_dict['huge']
    # function_list = [first_deal_general_stock, second_deal_general_stock, fourth_deal_general_stock,
    #                  fifth_deal_general_stock]
    function_list = [first_deal_general_stock, second_deal_general_stock]
    # 先跟tail_list执行拼货
    for i in stock_list:
        # 如果没有当前车指定的品种，并且品种不等于全部
        if (truck.big_commodity_name and i.big_commodity_name != truck.big_commodity_name
                and truck.big_commodity_name != '全部'):
            continue
        # 超过车辆载重
        if i.actual_weight > (max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT):
            continue
        # 先跟tail_list执行拼货
        for function in function_list:
            load_task = function(tail_list, i, DispatchType.SECOND, max_weight)
            if load_task:
                return merge_result(load_task)
        # # 再跟huge_list执行拼货
        # for function in function_list:
        #     load_task = function(huge_list, i, DispatchType.SECOND, max_weight)
        #     if load_task:
        #         return merge_result(load_task)
    return None


def layer_filter_2(stock_list: List, stock_dict: Dict, truck: Truck):
    """
    按层次分货
    第一层：一装一卸
    第二层：同库两装一卸
    第三层：异库两装一卸
    第四层：一装两卸
    第五层：同库两装两卸
    """
    # 车辆载重
    max_weight = truck.load_weight
    # 拼货的结果列表(拼完后从中选取一个最优的)
    load_task_list = []
    # 拼货记录标记
    parent_stock_id_list = []
    # 对于上面拼货结果的id标记
    load_task_id_list = []
    # 配载货物列表：尾货
    tail_list = stock_dict['tail']
    # 配载货物列表：标载
    huge_list = stock_dict['huge']
    # 配载方法
    function_list = [first_deal_general_stock, second_deal_general_stock]
    # function_list = [first_deal_general_stock, second_deal_general_stock, fourth_deal_general_stock,
    #                  fifth_deal_general_stock]
    for i in stock_list:
        # 如果没有当前车指定的品种，并且品种不等于全部
        if (truck.big_commodity_name and i.big_commodity_name != truck.big_commodity_name
                and truck.big_commodity_name != '全部'):
            continue
        # 超过车辆载重
        if i.actual_weight > (max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT):
            continue
        # 车的剩余重量不足以再拿来拼货的情况
        if max_weight - i.actual_weight < ModelConfig.RG_COMMODITY_COMPOSE_LOW_WEIGHT.get(i.big_commodity_name, 0):
            # 如果车辆报道载重是标载范围内
            if get_lower_limit(
                    i.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
                # 如果满足最低载重或者卷类一件大于26，生成车次
                if i.actual_weight >= get_lower_limit(i.big_commodity_name) or (i.big_commodity_name
                                                                                in ModelConfig.RG_J_GROUP
                                                                                and i.actual_number == 1
                                                                                and i.actual_weight >= ModelConfig.RG_J_PIECE_MIN_WEIGHT):
                    load_task = create_load_task([i], None, LoadTaskType.TYPE_1.value)
                    load_task_list, load_task_id_list = keep_result(load_task, load_task_list, load_task_id_list)
                    # 匹配结果数量达到阈值时结束匹配
                    if len(load_task_list) >= ModelConfig.RG_SINGLE_COMPOSE_MAX_LEN:
                        break
                    continue
            # 车辆报道载重不在标载范围内，直接生成车次
            else:
                load_task = create_load_task([i], None, LoadTaskType.TYPE_1.value)
                load_task_list, load_task_id_list = keep_result(load_task, load_task_list, load_task_id_list)
                # 匹配结果数量达到阈值时结束匹配
                if len(load_task_list) >= ModelConfig.RG_SINGLE_COMPOSE_MAX_LEN:
                    break
                continue
        # 如果该子项已经参与过拼货，则跳过再次拼货
        if ','.join([str(i.parent_stock_id), str(i.actual_number)]) in parent_stock_id_list:
            continue
        # 否则就加进去，并进行拼货
        else:
            parent_stock_id_list.append(','.join([str(i.parent_stock_id), str(i.actual_number)]))
        # 获取配载方案
        load_task = do_stowage(function_list, i, tail_list, huge_list, max_weight)
        if load_task:
            load_task_list, load_task_id_list = keep_result(load_task, load_task_list, load_task_id_list)
        # 匹配结果数量达到阈值时结束匹配
        if len(load_task_list) >= ModelConfig.RG_SINGLE_COMPOSE_MAX_LEN:
            break
    # 将中间结果保存到数据库
    # from app.main.steel_factory.service.single_dispatch_service import save_load_task
    # p = 1
    # for load_task in load_task_list:
    #     load_task.schedule_no = p
    #     save_load_task(load_task)
    #     p += 1
    # 评判从load_task_list中选取哪一个load_task返回
    return select_optimal_load_task(load_task_list, max_weight)


def keep_result(load_task: LoadTask, load_task_list: List[LoadTask], load_task_id_list: List):
    """
    判断load_task在load_task_list中是否已经有相同的，如果没有测添加到load_task_list中
    :param load_task:
    :param load_task_list:
    :param load_task_id_list:
    :return:
    """
    load_task = merge_result(load_task)
    id_flag_list = []
    sum_count = 0
    # 父id+件数
    for item in load_task.items:
        id_flag_list.append(','.join([str(item.parent_load_task_id), str(item.count)]))
        sum_count += item.count
    # 如果返回的结果是卷类
    if load_task.items[0].big_commodity in ModelConfig.RG_J_GROUP:
        if g.remark_num_set and len(g.remark_num_set) > 0 and sum_count not in g.remark_num_set:
            return load_task_list, load_task_id_list
    # 排序
    id_flag_list.sort()
    id_flag = ','.join(id_flag_list)
    # 如果没有相同的，加入
    if id_flag not in load_task_id_list:
        load_task_list.append(load_task)
        load_task_id_list.append(id_flag)
    return load_task_list, load_task_id_list


def first_deal_general_stock(stock_list, i, dispatch_type, max_weight):
    """
    一装一卸筛选器
    :param i:
    :param max_weight:
    :param stock_list:
    :param dispatch_type:
    :return:
    """
    # 取第i个元素作为目标库存
    temp_stock = i
    # 拆散的情况下，最大重量等于车辆最大载重，下浮1000
    if dispatch_type is DispatchType.THIRD:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT
        new_min_weight = surplus_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT
    # 如果拉标载
    elif get_lower_limit(
            temp_stock.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = get_lower_limit(temp_stock.big_commodity_name) - temp_stock.actual_weight
    # 不拉标载，最小重量等于车辆最大载重扣除目标货物的重量，下浮2000
    else:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = max_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT - temp_stock.actual_weight
    # 得到待匹配列表
    filter_list = [stock for stock in stock_list if stock is not temp_stock
                   and stock.deliware_house == temp_stock.deliware_house
                   and stock.deliware == temp_stock.deliware
                   and stock.standard_address == temp_stock.standard_address
                   and stock.piece_weight <= surplus_weight
                   and stock.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(
        temp_stock.big_commodity_name, [temp_stock.big_commodity_name])]
    # 入库仓库为U289-绿色通道库，只能一个客户配载
    filter_list = check_deliware(temp_stock, filter_list)
    # # 如果卷重小于24或者大于29，则不拼线材
    # if temp_stock.big_commodity_name == '老区-卷板' and (
    #         temp_stock.actual_weight >= ModelConfig.RG_J_MIN_WEIGHT or
    #         temp_stock.actual_weight < ModelConfig.RG_SECOND_MIN_WEIGHT):
    #     filter_list = [stock_j for stock_j in filter_list if stock_j.big_commodity_name == '老区-卷板']
    if filter_list:
        for i in range(0, len(filter_list), 2):
            temp_filter_list = filter_list[:i + 2]
            if temp_stock.big_commodity_name == '老区-型钢':
                temp_max_weight: int = 0
                # 目标拼货组合
                target_compose_list: List[Stock] = list()
                temp_set: set = set([i.specs for i in temp_filter_list])
                for i in temp_set:
                    temp_list = [v for v in temp_filter_list if v.specs == i or v.specs == temp_stock.specs]
                    result_list = split(temp_list)
                    # 选中的列表
                    compose_list, value = goods_filter(result_list, surplus_weight)
                    if value >= new_min_weight:
                        if temp_max_weight < value:
                            temp_max_weight = value
                            target_compose_list = compose_list
                if temp_max_weight:
                    temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
                    if temp_stock:
                        target_compose_list.append(temp_stock)
                    return create_load_task(target_compose_list, None, LoadTaskType.TYPE_1.value)
            else:
                temp_list = split(temp_filter_list)
                # 选中的列表
                compose_list, value = goods_filter(temp_list, surplus_weight)
                if value >= new_min_weight:
                    temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
                    if temp_stock:
                        compose_list.append(temp_stock)
                    return create_load_task(compose_list, None, LoadTaskType.TYPE_1.value)
    # 一单在达标重量之上并且无货可拼的情况生成车次
    if new_min_weight <= 0:
        return create_load_task([temp_stock], None, LoadTaskType.TYPE_1.value)
    if (temp_stock.big_commodity_name
            in ModelConfig.RG_J_GROUP
            and temp_stock.actual_number == 1
            and temp_stock.actual_weight >= ModelConfig.RG_J_PIECE_MIN_WEIGHT
            and max_weight <= ModelConfig.RG_MAX_WEIGHT):
        return create_load_task([temp_stock], None, LoadTaskType.TYPE_1.value)
    else:
        return None


def second_deal_general_stock(stock_list, i, dispatch_type, max_weight):
    """
    两装一卸（同区仓库）筛选器
    :param max_weight:
    :param i:
    :param stock_list:
    :param dispatch_type:
    :return:
    """
    # 取第i个元素作为目标库存
    temp_stock = i
    # 拆散的情况下，最大重量等于车辆最大载重，下浮1000
    if dispatch_type is DispatchType.THIRD:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT
        new_min_weight = surplus_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT
    # 如果拉标载
    elif get_lower_limit(
            temp_stock.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = get_lower_limit(temp_stock.big_commodity_name) - temp_stock.actual_weight
    # 不拉标载，最大重量等于车辆最大载重扣除目标货物的重量，下浮2000
    else:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = max_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT - temp_stock.actual_weight
    # 获取可拼货同区仓库
    warehouse_out_group = get_warehouse_out_group(temp_stock)
    # 条件筛选
    filter_list = [stock for stock in stock_list if stock is not temp_stock
                   and stock.standard_address == temp_stock.standard_address
                   and stock.deliware_house in warehouse_out_group
                   and stock.deliware == temp_stock.deliware
                   and stock.piece_weight <= surplus_weight
                   and stock.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(
        temp_stock.big_commodity_name, [temp_stock.big_commodity_name])]
    # 入库仓库为U289-绿色通道库，只能一个客户配载
    filter_list = check_deliware(temp_stock, filter_list)
    optimal_weight, target_compose_list = get_optimal_group(filter_list, temp_stock, surplus_weight, new_min_weight,
                                                            'deliware_house')
    if optimal_weight:
        temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
        if temp_stock:
            target_compose_list.append(temp_stock)
        return create_load_task(target_compose_list, None, LoadTaskType.TYPE_2.value)
    else:
        return None


def fourth_deal_general_stock(stock_list, i, dispatch_type, max_weight):
    """
    一装两卸筛选器
    :param max_weight:
    :param i:
    :param stock_list:
    :param dispatch_type:
    :return:
    """
    # 取第i个元素作为目标库存
    temp_stock = i
    # 拆散的情况下，最大重量等于车辆最大载重，下浮1000
    if dispatch_type is DispatchType.THIRD:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT
        new_min_weight = surplus_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT
    # 如果拉标载
    elif get_lower_limit(
            temp_stock.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = get_lower_limit(temp_stock.big_commodity_name) - temp_stock.actual_weight
    # 不拉标载，最大重量等于车辆最大载重扣除目标货物的重量，下浮2000
    else:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = max_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT - temp_stock.actual_weight
    filter_list = [stock for stock in stock_list if stock is not temp_stock
                   and stock.deliware_house == temp_stock.deliware_house
                   and stock.deliware == temp_stock.deliware
                   and stock.actual_end_point == temp_stock.actual_end_point
                   and stock.piece_weight <= surplus_weight
                   and stock.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(
        temp_stock.big_commodity_name, [temp_stock.big_commodity_name])]
    # 入库仓库为U289-绿色通道库，只能一个客户配载
    filter_list = check_deliware(temp_stock, filter_list)
    optimal_weight, target_compose_list = get_optimal_group(filter_list, temp_stock, surplus_weight, new_min_weight,
                                                            'standard_address')
    if optimal_weight:
        temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
        if temp_stock:
            target_compose_list.append(temp_stock)
        return create_load_task(target_compose_list, None, LoadTaskType.TYPE_4.value)
    else:
        return None


def fifth_deal_general_stock(stock_list, i, dispatch_type, max_weight):
    """
    两装两卸筛（同区仓库）选器
    :param max_weight:
    :param i:
    :param stock_list:
    :param dispatch_type:
    :return:
    """
    # 取第i个元素作为目标库存
    temp_stock = i
    # 拆散的情况下，最大重量等于车辆最大载重，下浮1000
    if dispatch_type is DispatchType.THIRD:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT
        new_min_weight = surplus_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT
    # 如果拉标载
    elif get_lower_limit(
            temp_stock.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = get_lower_limit(temp_stock.big_commodity_name) - temp_stock.actual_weight
    # 不拉标载，最大重量等于车辆最大载重扣除目标货物的重量，下浮2000
    else:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = max_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT - temp_stock.actual_weight
    # 获取可拼货同区仓库
    warehouse_out_group = get_warehouse_out_group(temp_stock)
    # 仓库集合
    deliware_house_set: set = set([getattr(s, 'deliware_house') for s in stock_list])
    for i in deliware_house_set:
        # 保证两装、同区仓库
        if i != temp_stock.deliware_house and i in warehouse_out_group:
            filter_list = [stock for stock in stock_list if stock is not temp_stock
                           and (stock.deliware_house == temp_stock.deliware_house or stock.deliware_house == i)
                           and stock.deliware == temp_stock.deliware
                           and stock.actual_end_point == temp_stock.actual_end_point
                           and stock.piece_weight <= surplus_weight
                           and stock.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(
                temp_stock.big_commodity_name, [temp_stock.big_commodity_name])]
            # 入库仓库为U289-绿色通道库，只能一个客户配载
            filter_list = check_deliware(temp_stock, filter_list)
            optimal_weight, target_compose_list = get_optimal_group(filter_list, temp_stock, surplus_weight,
                                                                    new_min_weight, 'standard_address')
            if optimal_weight:
                temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
                if temp_stock:
                    target_compose_list.append(temp_stock)
                return create_load_task(target_compose_list, None, LoadTaskType.TYPE_6.value)
    return None


def get_optimal_group(filter_list, temp_stock, surplus_weight, new_min_weight, attr_name):
    """
    获取最优组别
    :param attr_name:
    :param filter_list:
    :param temp_stock:
    :param surplus_weight:
    :param new_min_weight:
    :return:
    """
    # # 如果卷重小于24或者大于29，则不拼线材
    # if temp_stock.big_commodity_name == '老区-卷板' and (
    #         temp_stock.actual_weight >= ModelConfig.RG_J_MIN_WEIGHT or
    #         temp_stock.actual_weight <= ModelConfig.RG_SECOND_MIN_WEIGHT):
    #     filter_list = [stock_j for stock_j in filter_list if stock_j.big_commodity_name == '老区-卷板']
    if not filter_list:
        return 0, []
    for item in range(0, len(filter_list), 2):
        temp_filter_list = filter_list[:item + 2]
        temp_max_weight: int = 0
        # 目标拼货组合
        target_compose_list: List[Stock] = list()
        temp_set: set = set([getattr(i, attr_name) for i in temp_filter_list])
        # 如果目标货物品类为型钢
        if temp_stock.big_commodity_name == '老区-型钢':
            for i in temp_set:
                if i != getattr(temp_stock, attr_name):
                    temp_list = [v for v in temp_filter_list if
                                 getattr(v, attr_name) == i or getattr(v, attr_name) == getattr(temp_stock, attr_name)]
                    # 获取规格信息
                    spec_set = set([j.specs for j in temp_list])
                    for spec in spec_set:
                        xg_list = [v for v in temp_list if v.specs == temp_stock.specs or v.specs == spec]
                        result_list = split(xg_list)
                        # 选中的列表
                        compose_list, value = goods_filter(result_list, surplus_weight)
                        if value >= new_min_weight:
                            if temp_max_weight < value:
                                temp_max_weight = value
                                target_compose_list = compose_list
        else:
            for i in temp_set:
                if i != getattr(temp_stock, attr_name):
                    temp_list = [v for v in temp_filter_list if
                                 getattr(v, attr_name) == i or getattr(v, attr_name) == getattr(temp_stock, attr_name)]
                    result_list = split(temp_list)
                    # 选中的列表
                    compose_list, value = goods_filter(result_list, surplus_weight)
                    if value >= new_min_weight:
                        if temp_max_weight < value:
                            temp_max_weight = value
                            target_compose_list = compose_list
        if temp_max_weight:
            return temp_max_weight, target_compose_list
    return 0, []


def get_warehouse_out_group(temp_stock: Stock) -> List[str]:
    for group in ModelConfig.RG_WAREHOUSE_GROUP:
        if temp_stock.deliware_house in group:
            return group


def do_stowage(function_list, i, tail_list, huge_list, max_weight):
    """
    配载
    :param function_list:
    :param i:
    :param tail_list:
    :param huge_list:
    :param max_weight:
    :return:
    """
    # 先跟tail_list执行拼货
    for function in function_list:
        load_task = function(tail_list, i, DispatchType.SECOND, max_weight)
        if load_task:
            return load_task
    # 再跟huge_list执行拼货
    for function in function_list:
        load_task = function(huge_list, i, DispatchType.SECOND, max_weight)
        if load_task:
            return load_task
    return None


def merge_result(load_task):
    if load_task:
        result_dict = dict()
        for item in load_task.items:
            result_dict.setdefault(item.parent_load_task_id, []).append(item)
        # 暂时清空items
        load_task.items = []
        for res_list in result_dict.values():
            sum_list = [(i.weight, i.count) for i in res_list]
            sum_weight = sum(i[0] for i in sum_list)
            sum_count = sum(i[1] for i in sum_list)
            res_list[0].weight = round(sum_weight, 3)
            res_list[0].count = sum_count
            load_task.items.append(res_list[0])
        return load_task
    else:
        return None


def select_optimal_load_task(load_task_list: List[LoadTask], max_weight):
    """
    评判从load_task_list中选取哪一个load_task返回
    :param max_weight:
    :param load_task_list:
    :return:
    """
    if not load_task_list:
        return None
    # 最优的load_task
    best_load_task = load_task_list[0]
    # 最优的load_task的价值
    best_load_task_value = -1
    # 计算每个load_task的价值
    for load_task in load_task_list:
        load_task_value = calculate_value(load_task.items, max_weight)
        # 如果找到了更优的则更新
        if load_task_value > best_load_task_value:
            best_load_task = load_task
            best_load_task_value = load_task_value
    return best_load_task


def calculate_value(load_task_item_list: List[LoadTaskItem], max_weight):
    """
    计算价值
    :param max_weight:
    :param load_task_item_list:
    :return:
    """
    # 打印load_task_item日志
    #current_app.logger.info("预返回结果：" + json.dumps([i.as_dict() for i in load_task_item_list], ensure_ascii=False))
    # 初始化0
    value = 0
    '''优先级'''
    priority_list = [i.priority for i in load_task_item_list]
    # 优先级的价值
    priority_value = 0
    for priority in priority_list:
        # 优先级的价值为（10-优先等级）*10
        priority_value += (ModelConfig.SINGLE_VALUE_OF_PRIORITY[0] - priority) * ModelConfig.SINGLE_VALUE_OF_PRIORITY[1]
    # 对于优先级需要做一个归一化，例如优先级相同的2车货物，一个中1条记录，一个中2条记录
    priority_value = priority_value / len(priority_list)
    value += priority_value
    '''卸点客户'''
    consumer_set = set([i.consumer for i in load_task_item_list])
    # 卸点客户的价值：1:2；2:0；3:-2
    consumer_value = (ModelConfig.SINGLE_VALUE_OF_CONSUMER[0] -
                      len(consumer_set)) * ModelConfig.SINGLE_VALUE_OF_CONSUMER[1]
    value += consumer_value
    '''装点仓库'''
    outstock_code_set = set([str(i.outstock_code).split('-')[0] for i in load_task_item_list])
    # 装点仓库的价值：1:1；2:0；3:-1
    outstock_value = (ModelConfig.SINGLE_VALUE_OF_DELIWARE[0] -
                      len(outstock_code_set)) * ModelConfig.SINGLE_VALUE_OF_DELIWARE[1]
    value += outstock_value
    '''仓库作业效率'''   '''联储仓库'''
    # 仓库作业效率价值
    outstock_code_value_list = []
    # 联储仓库价值
    storage_outstock_code_value_list = []
    for outstock_code in outstock_code_set:
        # 各仓库一般车辆容纳数
        normal_num = ModelConfig.SINGLE_WAREHOUSE_WAIT_DICT.get(outstock_code,
                                                                ModelConfig.SINGLE_VALUE_OF_DELIWARE_EFFICIENCY[0])
        # 各仓库当前查询到的车辆数
        now_num = ModelConfig.SINGLE_NOW_WAREHOUSE_DICT.get(outstock_code, 0)
        outstock_code_value_list.append(
            float(normal_num - now_num) / normal_num * ModelConfig.SINGLE_VALUE_OF_DELIWARE_EFFICIENCY[1])
        # 联储仓库
        if outstock_code in ModelConfig.SINGLE_STORAGE_DELIWARE:
            storage_outstock_code_value_list.append(float(ModelConfig.SINGLE_VALUE_OF_DELIWARE_EFFICIENCY[2]))
    outstock_code_value = MathUtil.min(outstock_code_value_list, 0)
    storage_outstock_code_value = MathUtil.min(storage_outstock_code_value_list, 0)
    value += outstock_code_value
    value += storage_outstock_code_value
    '''装点厂区'''
    factory_set = get_factory_set(outstock_code_set)
    # 装点厂区的价值：1:2；2:0；3:-2
    factory_value = (ModelConfig.SINGLE_VALUE_OF_FACTORY[0] -
                     len(factory_set)) * ModelConfig.SINGLE_VALUE_OF_FACTORY[1]
    value += factory_value
    '''重量'''
    # 计算总重量
    total_weight = sum([i.weight for i in load_task_item_list])
    # 以max_weight为标准，每多一吨价值函数+2，每少一吨价值函数-2
    weight_value = (round_util(total_weight) - max_weight / 1000) * ModelConfig.SINGLE_VALUE_OF_WEIGHT[0]
    value += weight_value
    '''订单'''
    # 订单的价值：个数*0.5
    order_value = len(load_task_item_list) * ModelConfig.SINGLE_VALUE_OF_ORDER_NUM[0]
    value += order_value
    '''如果有件重大于ModelConfig.SINGLE_BIG_PIECE_WEIGHT / 1000的货物，并且不是单独一件'''
    # 额外的价值
    extra_value = 0
    if (ModelConfig.SINGLE_BIG_PIECE_WEIGHT / 1000 < max(
            [i.weight / i.count for i in load_task_item_list]) < ModelConfig.RG_J_PIECE_MIN_WEIGHT / 1000
            and sum([i.count for i in load_task_item_list]) != 1):
        extra_value += ModelConfig.SINGLE_VALUE_OF_EXTRA[0]
    value += extra_value
    # 打印日志
    '''current_app.logger.info("预返回结果的价值：" + json.dumps(value, ensure_ascii=False) + '=' +
                            '+'.join([json.dumps(priority_value, ensure_ascii=False),
                                      json.dumps(consumer_value, ensure_ascii=False),
                                      json.dumps(outstock_value, ensure_ascii=False),
                                      json.dumps(outstock_code_value, ensure_ascii=False),
                                      json.dumps(storage_outstock_code_value, ensure_ascii=False),
                                      json.dumps(factory_value, ensure_ascii=False),
                                      json.dumps(weight_value, ensure_ascii=False),
                                      json.dumps(order_value, ensure_ascii=False),
                                      json.dumps(extra_value, ensure_ascii=False)
                                      ])
                            )'''
    return value


def get_factory_set(outstock_code_set):
    """
    根据出库仓库找出厂区
    :param outstock_code_set:
    :return:
    """
    # 厂区集合
    factory_set = set()
    for outstock_code in outstock_code_set:
        if outstock_code in ModelConfig.RG_WAREHOUSE_GROUP[0]:
            factory_set.add('宝华')
        elif outstock_code in ModelConfig.RG_WAREHOUSE_GROUP[1]:
            factory_set.add('厂内')
        elif outstock_code in ModelConfig.RG_WAREHOUSE_GROUP[2]:
            factory_set.add('岚北港')
        # else:
        #     factory_set.add('未知厂区')
    return factory_set


def check_deliware(temp_stock: Stock, filter_list: List[Stock]):
    """

    :param temp_stock:
    :param filter_list:
    :return:
    """
    # 如果入库仓库为U289-绿色通道库，只能一个客户配载
    if temp_stock.deliware == ModelConfig.RG_U289:
        filter_list = [stock for stock in filter_list if stock.consumer == temp_stock.consumer]
    return filter_list


# def calculate_value(load_task_item_list: List[LoadTaskItem], max_weight):
#     """
#     计算价值
#     :param max_weight:
#     :param load_task_item_list:
#     :return:
#     """
#     # 初始化0
#     value = 0
#     '''优先级'''
#     priority_list = [i.priority for i in load_task_item_list]
#     priority_value = 0
#     for priority in priority_list:
#         # 优先级的价值为（10-优先等级）*10
#         priority_value += (ModelConfig.SINGLE_VALUE_OF_PRIORITY[0] - priority) * ModelConfig.SINGLE_VALUE_OF_PRIORITY[1]
#     # 对于优先级需要做一个归一化，例如优先级相同的2车货物，一个中1条记录，一个中2条记录
#     value += priority_value / len(priority_list)
#     '''卸点客户'''
#     consumer_set = set([i.consumer for i in load_task_item_list])
#     # 1个客户价值函数+2
#     if len(consumer_set) == 1:
#         value += ModelConfig.SINGLE_VALUE_OF_CONSUMER[0]
#     # 2个客户价值函数-2
#     elif len(consumer_set) == 2:
#         value += ModelConfig.SINGLE_VALUE_OF_CONSUMER[1]
#     # 多个客户价值函数-4
#     else:
#         value += ModelConfig.SINGLE_VALUE_OF_CONSUMER[2]
#     '''装点仓库'''
#     outstock_code_set = set([i.outstock_code for i in load_task_item_list])
#     # 1个仓库价值函数+1
#     if len(outstock_code_set) == 1:
#         value += ModelConfig.SINGLE_VALUE_OF_DELIWARE[0]
#     # 2个仓库价值函数-1
#     elif len(outstock_code_set) == 2:
#         value += ModelConfig.SINGLE_VALUE_OF_DELIWARE[1]
#     # 多个仓库价值函数-2
#     else:
#         value += ModelConfig.SINGLE_VALUE_OF_DELIWARE[2]
#     '''仓库作业效率'''   '''联储仓库'''
#     # 仓库作业效率价值
#     outstock_code_value = 0
#     # 联储仓库价值
#     storage_outstock_code_value = 0
#     for outstock_code in outstock_code_set:
#         # 各仓库一般车辆容纳数
#         normal_num = ModelConfig.SINGLE_WAREHOUSE_WAIT_DICT.get(outstock_code,
#                                                                 ModelConfig.SINGLE_VALUE_OF_DELIWARE_EFFICIENCY[0])
#         # 各仓库当前查询到的车辆数
#         now_num = ModelConfig.SINGLE_NOW_WAREHOUSE_DICT.get(outstock_code, 0)
#         outstock_code_value += (float(normal_num - now_num) / normal_num *
#                                 ModelConfig.SINGLE_VALUE_OF_DELIWARE_EFFICIENCY[1])
#         # 联储仓库
#         if outstock_code in ModelConfig.SINGLE_STORAGE_DELIWARE:
#             storage_outstock_code_value += float(ModelConfig.SINGLE_VALUE_OF_DELIWARE_EFFICIENCY[2])
#     value += outstock_code_value / len(outstock_code_set)
#     value += storage_outstock_code_value / len(outstock_code_set)
#     '''装点厂区'''
#     factory_set = get_factory_set(outstock_code_set)
#     # 1个厂区价值函数+2
#     if len(factory_set) == 1:
#         value += ModelConfig.SINGLE_VALUE_OF_FACTORY[0]
#     # 2个厂区价值函数-2
#     elif len(factory_set) == 2:
#         value += ModelConfig.SINGLE_VALUE_OF_FACTORY[1]
#     # 多个厂区价值函数-4
#     else:
#         value += ModelConfig.SINGLE_VALUE_OF_FACTORY[2]
#     '''重量'''
#     # 计算总重量
#     total_weight = sum([i.weight for i in load_task_item_list])
#     # 以max_weight为标准，每多一吨价值函数+2，每少一吨价值函数-2
#     value += (math.floor(total_weight) -
#               max_weight / ModelConfig.SINGLE_VALUE_OF_WEIGHT[0]) * ModelConfig.SINGLE_VALUE_OF_WEIGHT[1]
#     '''订单'''
#     value += len(load_task_item_list) * ModelConfig.SINGLE_VALUE_OF_ORDER_NUM[0]
#     '''如果有件重大于ModelConfig.SINGLE_BIG_PIECE_WEIGHT / 1000的货物，并且不是单独一件'''
#     if max([i.weight / i.count for i in load_task_item_list]) > ModelConfig.SINGLE_BIG_PIECE_WEIGHT / 1000 and sum(
#             [i.count for i in load_task_item_list]) != 1:
#         value += ModelConfig.SINGLE_VALUE_OF_EXTRA[0]
#     return value
#     '''
#         # 单车分货中优先级的价值
#         SINGLE_VALUE_OF_PRIORITY = [10, 10]
#         # 单车分货中卸点客户的价值
#         SINGLE_VALUE_OF_CONSUMER = [2, -2, -4]
#         # 单车分货中装点仓库的价值
#         SINGLE_VALUE_OF_DELIWARE = [1, -1, -2]
#         # 单车分货中装点仓库效率的价值:各仓库默认一般车辆容纳数、仓库作业效率放大的比例、联储仓库被扣减的价值
#         SINGLE_VALUE_OF_DELIWARE_EFFICIENCY = [20, 5, -2]
#         # 单车分货中装点厂区的价值
#         SINGLE_VALUE_OF_FACTORY = [2, -2, -4]
#         # 单车分货中载重的价值
#         SINGLE_VALUE_OF_WEIGHT = [1000, 2]
#         # 单车分货中订单的价值
#         SINGLE_VALUE_OF_ORDER_NUM = [-0.5]
#         # 件重大于此值的优先排到前面配货
#         SINGLE_BIG_PIECE_WEIGHT = 17500
#         # 单车分货中额外添加的价值
#         SINGLE_VALUE_OF_EXTRA = [80]
#     '''


#
# """
# 对于上面拼货尾货的优化，使当前货物先和重量小的货物拼凑，但是可能存在拼货失败的情况
# """
# import copy
# import pandas as pd
# from app.main.steel_factory.entity.load_task import LoadTask
# from app.main.steel_factory.entity.load_task_item import LoadTaskItem
#
#
# def layer_filter1(stock_list: List, stock_dict: Dict, truck: Truck):
#     max_weight = truck.load_weight
#     load_task_list: List[LoadTask] = []
#     tail_list = stock_dict['tail']
#     tail_list.sort(key=lambda x: x.actual_weight, reverse=False)  #
#     function_list = [first_deal_general_stock1, second_deal_general_stock, fourth_deal_general_stock]
#     for i in stock_list:
#         if truck.big_commodity_name and i.big_commodity_name != truck.big_commodity_name:
#             continue
#         if i.actual_weight > (max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT):
#             continue
#         for function in function_list:
#             load_task = function(tail_list, i, DispatchType.SECOND, max_weight)
#             if load_task:
#                 load_task_list.append(merge_result(load_task))
#     # 将load_task_list导出为excel
#     df = pd.DataFrame()
#     if load_task_list:
#         tid = 0
#         truck_id = []
#         total_weight = []
#         load_task_type = []
#         priority_grade = []
#         big_commodity = []
#         commodity = []
#         city = []
#         consumer = []
#         weight = []
#         count = []
#         priority = []
#         latest_order_time = []
#         out_stock_code = []
#         for load_task in load_task_list:
#             tid = tid + 1
#             load_task_item: LoadTaskItem
#             for load_task_item in load_task.items:
#                 truck_id.append(tid)
#                 total_weight.append(load_task.total_weight)
#                 load_task_type.append(load_task.load_task_type)
#                 priority_grade.append(load_task.priority_grade)
#                 big_commodity.append(load_task_item.big_commodity)
#                 commodity.append(load_task_item.commodity)
#                 city.append(load_task_item.city)
#                 consumer.append(load_task_item.consumer)
#                 weight.append(load_task_item.weight)
#                 count.append(load_task_item.count)
#                 priority.append(load_task_item.priority)
#                 latest_order_time.append(load_task_item.latest_order_time)
#                 out_stock_code.append(load_task_item.outstock_code)
#         df.insert(0, 'commodity', commodity)
#         df.insert(0, 'big_commodity', big_commodity)
#         df.insert(0, 'out_stock_code', out_stock_code)
#         df.insert(0, 'consumer', consumer)
#         df.insert(0, 'city', city)
#         df.insert(0, 'priority', priority)
#         df.insert(0, 'load_task_type', load_task_type)
#         df.insert(0, 'priority_grade', priority_grade)
#         df.insert(0, 'latest_order_time', latest_order_time)
#         df.insert(0, 'count', count)
#         df.insert(0, 'weight', weight)
#         df.insert(0, 'total_weight', total_weight)
#         df.insert(0, 'truck_id', truck_id)
#     df.to_excel('result.xls')
#     if load_task_list:
#         return load_task_list[0]
#     else:
#         return None
#
#
# def first_deal_general_stock1(stock_list, temp_stock, dispatch_type, max_weight):
#     # 拆散的情况下，最大重量等于车辆最大载重，下浮1000
#     if dispatch_type is DispatchType.THIRD:
#         surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT
#         new_min_weight = surplus_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT
#     # 如果拉标载
#     elif get_lower_limit(temp_stock.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
#         surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
#         new_min_weight = get_lower_limit(temp_stock.big_commodity_name) - temp_stock.actual_weight
#     # 不拉标载，最小重量等于车辆最大载重扣除目标货物的重量，下浮2000
#     else:
#         surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
#         new_min_weight = max_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT - temp_stock.actual_weight
#     # 得到待匹配列表
#     filter_list = [stock for stock in stock_list if stock is not temp_stock
#                    and stock.deliware_house == temp_stock.deliware_house
#                    and stock.standard_address == temp_stock.standard_address
#                    and stock.piece_weight <= surplus_weight
#                    and stock.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.big_commodity_name,
#                                                                                       [temp_stock.big_commodity_name])]
#     # 如果卷重小于24或者大于29，则不拼线材
#     if temp_stock.big_commodity_name == '老区-卷板' and (
#             temp_stock.actual_weight >= ModelConfig.RG_J_MIN_WEIGHT or
#             temp_stock.actual_weight < ModelConfig.RG_SECOND_MIN_WEIGHT):
#         filter_list = [stock_j for stock_j in filter_list if stock_j.big_commodity_name == '老区-卷板']
#     if filter_list:
#         temp_max_weight: int = 0  # 目标拼货组合重量
#         target_compose_list: List[Stock] = list()  # 目标拼货组合库存列表
#         if temp_stock.big_commodity_name == '老区-型钢':  # 型钢最多只能拼两个规格（包括自身的规格）
#             temp_set: set = set([i.specs for i in filter_list])
#             for i in temp_set:
#                 # 筛选出满足规格要求的货物
#                 temp_list = [v for v in filter_list if v.specs == i or v.specs == temp_stock.specs]
#                 compose_list, compose_weight = get_optimal_compose(temp_list, surplus_weight)
#                 if compose_weight > temp_max_weight:
#                     temp_max_weight = compose_weight
#                     target_compose_list = compose_list
#         else:  # 非型钢
#             target_compose_list, temp_max_weight = get_optimal_compose(filter_list, surplus_weight)
#         if temp_max_weight >= new_min_weight:  # 满足重量下限要求
#             temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
#             if temp_stock:
#                 target_compose_list.append(temp_stock)
#             return create_load_task(target_compose_list, None, LoadTaskType.TYPE_1.value)
#     # 一单在达标重量之上并且无货可拼的情况生成车次
#     elif new_min_weight <= 0:
#         return create_load_task([temp_stock], None, LoadTaskType.TYPE_1.value)
#     elif (temp_stock.big_commodity_name in ModelConfig.RG_J_GROUP
#           and temp_stock.actual_number == 1
#           and temp_stock.actual_weight >= ModelConfig.RG_J_PIECE_MIN_WEIGHT):
#         return create_load_task([temp_stock], None, LoadTaskType.TYPE_1.value)
#     else:
#         return None
#
#
# def get_optimal_compose(filter_list: List[Stock], surplus_weight):
#     compose_weight: int = 0  # 目标拼货组合重量
#     compose_list: List[Stock] = list()  # 目标拼货组合库存列表
#     for stock in filter_list:
#         if compose_weight + stock.actual_weight <= surplus_weight:  # 直接添加整条库存
#             compose_weight += stock.actual_weight
#             compose_list.append(stock)
#         elif compose_weight + stock.piece_weight <= surplus_weight:  # 添加库存中的某几件
#             count = 1
#             for count in range(1, stock.actual_number + 1):  # 找出当前货物中有几件可以添加进目标组合
#                 if compose_weight + count * stock.piece_weight > surplus_weight:
#                     break
#             copy_stock = copy.deepcopy(stock)
#             copy_stock.actual_number = count - 1
#             copy_stock.actual_weight = copy_stock.actual_number * stock.piece_weight
#             compose_weight += copy_stock.actual_weight
#             compose_list.append(copy_stock)
#     return compose_list, compose_weight
def split_filter(stock_list, truck):
    load_task = None
    for stock in stock_list:
        # 如果没有当前车指定的品种，并且品种不等于全部,跳过
        if (truck.big_commodity_name and stock.big_commodity_name != truck.big_commodity_name
                and truck.big_commodity_name != '全部'):
            continue
        # 件数为1，跳过
        if stock.actual_number == 1:
            continue
        # 比车辆报道重量小的货，跳过
        if stock.actual_weight < truck.load_weight:
            continue
        # 如果单件重量大于车辆载重，跳过
        if stock.piece_weight > truck.load_weight + ModelConfig.RG_SINGLE_UP_WEIGHT:
            continue
        # 切分
        result_list = split([stock])
        target_result = []
        current_weight = 0
        for piece_stock in result_list:
            # 最大载重-当前载重>=一件货物重量，可继续放，否则结束放货
            if (truck.load_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - current_weight) >= piece_stock.actual_weight:
                target_result.append(piece_stock)
                current_weight += piece_stock.actual_weight
            else:
                break
        # 如果有结果并且此方案载重不低于车辆报道重量2吨，则选择，否则将继续寻找
        if (target_result and len(
                target_result) * stock.piece_weight + ModelConfig.RG_SINGLE_LOWER_WEIGHT >= truck.load_weight):
            load_task = merge_result(create_load_task(target_result, None, LoadTaskType.TYPE_1.value))
            break
    return load_task
