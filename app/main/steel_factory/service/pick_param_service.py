# -*- coding: utf-8 -*-
# Description: 摘单参数服务
# Created: jjunf 2021/01/15
from collections import defaultdict
from typing import List, Dict

from flask import current_app, json

from app.main.steel_factory.dao.pick_param_dao import pick_param_dao
from app.main.steel_factory.entity.pick_param import PickParam
from app.util.split_group_util import split_group_util


def get_param_service():
    """
    获取参数配置
    :return:
    """
    # 所有的参数配置
    param_config = {}
    # 查询参数
    param_list: List[PickParam] = pick_param_dao.select_pick_param()
    # 参数日志
    # current_app.logger.info('参数配置：' + json.dumps([i.as_dict() for i in param_list], ensure_ascii=False))
    # 按参数配置类型（配置类型：1品种搭配；2关联路线；3留货；4载重）分组
    param_dict = split_group_util(param_list, ['type_flag'])
    '''品种搭配：'老区-卷板': ['新产品-白卷', '老区-卷板', '新产品-卷板']'''
    commodity_dict = defaultdict(list)
    commodity_list: List[PickParam] = param_dict.get('1', [])
    if commodity_list:
        for commodity_param in commodity_list:
            commodity_dict[commodity_param.commodity].append(commodity_param.match_commodity)
            # 把品种自己添加进去
            if commodity_param.commodity not in commodity_dict[commodity_param.commodity]:
                commodity_dict[commodity_param.commodity].append(commodity_param.commodity)
    param_config['RG_COMMODITY_COMPOSE'] = commodity_dict
    '''关联路线：'1': ['山东省,济南市,天桥区', '山东省,济南市,历城区']'''
    route_dict = defaultdict(list)
    route_list: List[PickParam] = param_dict.get('2', [])
    if route_list:
        i = 0
        for route_param in route_list:
            i += 1
            # 卸点
            route_dict[str(i)].append(route_param.unload_province + ',' +
                                      route_param.unload_city + ',' + route_param.unload_district)
            # 关联卸点
            route_dict[str(i)].append(route_param.match_unload_province + ',' +
                                      route_param.match_unload_city + ',' + route_param.match_unload_district)
    param_config['ACROSS_DISTRICT_DICT'] = route_dict
    '''留货：
    ①客户留货 'special_consumer': ['济南市,长清区,老区-线材,苏美达国际技术贸易有限公司']；
    ②品种留货 'special_commodity': ['滨州市,长清区,新产品-冷板', '滨州市,全部,新产品-窄带']
    '''
    deduct_stock_dict = defaultdict(list)
    deduct_stock_dict['special_consumer'] = []
    deduct_stock_dict['special_commodity'] = []
    deduct_stock_list: List[PickParam] = param_dict.get('3', [])
    if deduct_stock_list:
        for deduct_stock_param in deduct_stock_list:
            # 如果客户不为空，则表示该客户留货
            if deduct_stock_param.keep_goods_customer:
                deduct_stock_dict['special_consumer'].append(
                    deduct_stock_param.keep_goods_city + ',' + deduct_stock_param.keep_goods_district + ',' +
                    deduct_stock_param.keep_goods_commodity + ',' + deduct_stock_param.keep_goods_customer)
            # 如果客户为空，则表示该品种都留货
            else:
                deduct_stock_dict['special_commodity'].append(
                    deduct_stock_param.keep_goods_city + ',' + deduct_stock_param.keep_goods_district + ',' +
                    deduct_stock_param.keep_goods_commodity)
    param_config['RG_DEDUCT_STOCK'] = deduct_stock_dict
    '''载重：'济南市,全部': [31000, 35000](济南市默认载重) '济南市,老区-卷板': [29000, 35000]'''  # 吨转换为kg
    weight_dict = defaultdict(list)
    weight_list: List[PickParam] = param_dict.get('4', [])
    if weight_list:
        for weight_param in weight_list:
            # 下限(吨转换为kg)
            weight_dict[weight_param.weight_city + ',' + weight_param.weight_commodity].append(
                int(weight_param.weight_lower * 1000))
            # 上限(吨转换为kg)
            weight_dict[weight_param.weight_city + ',' + weight_param.weight_commodity].append(
                int(weight_param.weight_upper * 1000))
    param_config['RG_COMMODITY_WEIGHT'] = weight_dict
    # 打印参数配置日志
    current_app.logger.info('参数配置：' + json.dumps(param_config, ensure_ascii=False))
    return param_config

# def param_interface_service(json_data: Dict):
#     """
#     与前端的参数交互接口
#     :param json_data:
#     :return:
#     """
#     # 1品种搭配
#     if json_data['type_flag'] == 1:
#         pass
#     # 2关联路线
#     elif json_data['type_flag'] == 2:
#         pass
#     # 3留货
#     elif json_data['type_flag'] == 3:
#         pass
#     # 4载重
#     elif json_data['type_flag'] == 4:
#         # insert、delete、update、select
#         for key in json_data.keys():
#             if key == 'type_flag':
#                 continue
#             # select
#             elif key == 'select':
#                 pick_param_list = pick_param_dao.select_param(json_data['type_flag'])
#             # insert、delete、update
#             else:
#                 param_list: List[PickParam] = [PickParam(obj) for obj in json_data[key]]
