# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12
import pandas as pd
from app.main.steel_factory.entity.stock import Stock
from app.util.get_static_path import get_path


def get_stock():
    """
    获取库存
    :param vehicle:
    :return: 库存
    """
    """
    步骤：
    1 读取Excel，省内1  0点库存明细和省内2、3及连云港库存两个sheet页
    2 数据合并
    """
    data_path = get_path("sheet1.xls")
    df_stock1 = pd.read_excel(data_path)
    return df_stock1


def generate_stock_list(json_data):
    stock_list_json = json_data
    stock_list = []
    for stock_item_json in stock_list_json:
        stock_item = Stock(stock_item_json)
        # stock_item.notice_num = stock_item_json.get('notice_num', None)
        # stock_item.oritem_num = stock_item_json.get('oritem_num', None)
        # stock_item.priority = int(stock_item_json.get('priority', None))
        # stock_item.consumer = stock_item_json.get('consumer', None)
        # stock_item.commodity_name = stock_item_json.get('commodity_name', None)
        # stock_item.big_commodity_name = stock_item_json.get('big_commodity_name', None)
        # stock_item.specs = stock_item_json.get('specs', None)
        # stock_item.deliware_house = stock_item_json.get('deliware_house', None)
        # stock_item.deliware_house_name = stock_item_json.get('deliware_house_name', None)
        # stock_item.province = stock_item_json.get('province', None)
        # stock_item.city = stock_item_json.get('city', None)
        # stock_item.dlv_spot_name_end = stock_item_json.get('dlv_spot_name_end', None)
        # stock_item.detail_address = stock_item_json.get('detail_address', None)
        # stock_item.latest_order_time = stock_item_json.get('latest_order_time', None)
        # stock_item.devperiod = stock_item_json.get('deveriod', None)
        # stock_item.actual_weight = int(stock_item_json.get('actual_weight', None))
        # stock_item.actual_number = int(stock_item_json.get('actual_number', None))
        # stock_item.piece_weight = int(stock_item_json.get('piece_weight', None))
        # stock_item.standard_address = stock_item_json.get('standard_address', None)
        # stock_item.parent_stock_id = stock_item_json.get('parent_stock_id', None)
        # stock_item.actual_end_point = stock_item_json.get('actual_end_point', None)
        # stock_item.waint_fordel_number = int(stock_item_json.get('waint_fordel_number', None))
        # stock_item.waint_fordel_weight = int(stock_item_json.get('waint_fordel_weight', None))
        # stock_item.wait_product_weight = int(stock_item_json.get('wait_product_weight', None))
        # stock_item.flow_confirm_person = stock_item_json.get('flow_confirm_person', None)
        # stock_item.load_task_count = int(stock_item_json.get('load_task_count', None))
        # stock_item.contract_no = stock_item_json.get('contract_no', None)

        stock_list.append(stock_item)

    return stock_list


def generate_stock_dict(json_data):
    stock_dict = Stock()
    stock_dict_json = json_data

    return stock_dict
