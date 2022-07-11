#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/10 13:40
# @Author  : \pingyu
# @File    : ecnu_single_goods_allocation_route.py
# @Software: PyCharm
import json
from flask import request
from flask_restful import Resource

from app.main.steel_factory.service.single_dispatch_service import dispatch
from app.main.steel_factory.service.stock_service import generate_stock_list, generate_stock_dict
from app.main.steel_factory.service.truck_service import generate_truck
from app.util.result import Result


class EcnuSingleGoodsAllocationRoute(Resource):

    @staticmethod
    def post():
        """
        输入车辆信息，返回开单结果
        """
        json_data = json.loads(request.get_data().decode("utf-8"))
        stock_list = generate_stock_list(json_data['stock_list'])
        stock_dict = generate_stock_dict(json_data['stock_dic'])
        truck = generate_truck(json_data['truck'])
        result = dispatch(stock_list, stock_dict, truck)
        return Result.success_response(result)
