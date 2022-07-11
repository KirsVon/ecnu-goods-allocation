# -*- coding: utf-8 -*-
# Description: 动态参数配置
# Created: jjunf 2021/01/06
from app.main.steel_factory.service.pick_param_service import get_param_service
from model_config import ModelConfig


class ParamConfig:
    """
    参数配置
    """
    # 标记：1表示使用ParamConfig的动态参数配置；0表示使用ModelConfig的静态参数配置
    FLAG = 1
    # 品种搭配
    RG_COMMODITY_COMPOSE = ModelConfig.RG_COMMODITY_GROUP
    # 跨区县卸货配置
    ACROSS_DISTRICT_DICT = ModelConfig.ACROSS_DISTRICT_DICT
    # 留货
    RG_DEDUCT_STOCK = {'special_commodity': ['滨州市,全部,新产品-冷板', '滨州市,全部,新产品-窄带'], 'special_consumer': []}
    # 载重
    RG_COMMODITY_WEIGHT = {}


def set_param_config():
    """
    获取最新的参数配置
    :return:
    """
    # 获取参数配置字典
    param_config = get_param_service()
    # 品种搭配
    ParamConfig.RG_COMMODITY_COMPOSE = param_config.get('RG_COMMODITY_COMPOSE', ModelConfig.RG_COMMODITY_GROUP)
    # 跨区县卸货配置
    ParamConfig.ACROSS_DISTRICT_DICT = param_config.get('ACROSS_DISTRICT_DICT', {})
    # 留货
    ParamConfig.RG_DEDUCT_STOCK = param_config.get('RG_DEDUCT_STOCK', ParamConfig.RG_DEDUCT_STOCK)
    # 载重
    ParamConfig.RG_COMMODITY_WEIGHT = param_config.get('RG_COMMODITY_WEIGHT', {})

#
#     '''1.按城市、品种配置载重'''
#     # 字典：键为城市,品种；值为列表，包含两个元素，第一个为下限，第二个为上限
#     # 如果维护了城市、品种的载重，则使用此维护的载重，否则使用维护的该城市的默认载重(城市，全部)，否则提示用户维护载重信息
#     RG_COMMODITY_WEIGHT = {
#         '济南市,全部': [31000, 35000],  # 济南市默认载重
#         '济南市,老区-卷板': [29000, 35000],
#         '济南市,新产品-卷板': [29000, 35000],
#         '济南市,新产品-白卷': [29000, 35000],
#         '济南市,老区-型钢': [31000, 35000],
#         '济南市,老区-线材': [31000, 35000]
#     }
#     # 特殊情况：
#     # 如果一个区县所有货物的总重量<=40吨时，需要一个上限40400和下限31000
#     # 需要判断某区县某客户某品种总量是否大于200吨
#     # 西区、岚北港的卷类 件重24-31t的先内部组合
#     '''2.品种搭配配置'''
#     # 注：在查完表后，需要把这个品种自己和自己拼的情况加进去，在表中不保留自己和自己的记录
#     # 字典：键为品种；值为列表，表示键品种可拼的品种
#     RG_COMMODITY_COMPOSE = {
#         '老区-型钢': ['老区-型钢'],
#         '老区-线材': ['老区-线材'],
#         '老区-螺纹': ['老区-螺纹'],
#         '老区-开平板': ['老区-开平板'],
#         '老区-卷板': ['新产品-白卷', '老区-卷板', '新产品-卷板'],
#         '新产品-白卷': ['新产品-窄带', '新产品-冷板', '新产品-白卷', '老区-卷板', '新产品-卷板'],
#         '新产品-卷板': ['新产品-窄带', '新产品-冷板', '新产品-白卷', '老区-卷板', '新产品-卷板'],
#         '新产品-窄带': ['新产品-窄带', '新产品-冷板', '新产品-白卷', '新产品-卷板'],
#         '新产品-冷板': ['新产品-窄带', '新产品-冷板', '新产品-白卷', '新产品-卷板']
#     }
#     '''3.仓库配置'''
#     # 一个列表中包含3个列表，分别表示西区、老区、岚北港的仓库，先后顺序不能变
#     RG_WAREHOUSE_GROUP = [
#         ["P5", "P6", "P7", "P8"],
#         ["B1", "B2", "E1", "E2", "E3", "E4", "F1", "F2", "H1", "T1", "X1", "X2", "Z1", "Z2", "Z4", "Z5", "Z8", "ZA",
#          "ZC"],
#         ["F10", "F20"]
#     ]
#     '''4.特殊库存扣除配置（某城市某品种不使用模型分货、某城市某区县某客户某品种不接货等情况）'''
#     # (城市+','+品种)、(城市+','+区县+','+品种+','+客户)
#     RG_DEDUCT_STOCK = {
#         'special_commodity': ['滨州市,新产品-冷板', '滨州市,新产品-窄带'],
#         'special_consumer': ['济南市,长清区,老区-线材,苏美达国际技术贸易有限公司']
#     }
#     '''5.客户统一配置'''
#     # 字典：键为当前客户名称；值为当前客户统一之后的客户名称
#     RG_SAME_CONSUMER_DICT = {
#         '山东省博兴县拓鑫钢铁贸易有限公司': '山东鹏禾新材料有限公司',
#         '山东省拓鑫钢铁贸易有限公司': '山东鹏禾新材料有限公司'
#     }
#     '''6.跨区县卸货配置'''
#     # 字典：键为优先级，值为可跨区县拼货的区县（要求已经按照优先级从高到低排好序）
#     ACROSS_DISTRICT_DICT = {
#         '1': ['天桥区', '历城区'],
#         '2': ['天桥区', '槐荫区'],
#         '3': ['天桥区', '市中区'],
#         '4': ['历城区', '槐荫区'],
#         '5': ['槐荫区', '市中区']
#     }
#
#
# if __name__ == '__main__':
#     for i in range(10):
#         print(i, ':  ', ParamConfig.RG_COMMODITY_WEIGHT)
