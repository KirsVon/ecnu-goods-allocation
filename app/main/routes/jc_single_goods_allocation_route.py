#!/usr/bin/python
# -*- coding: utf-8 -*-
# Description: 
# Created: lei.cheng 2021/9/8
# Modified: lei.cheng 2021/9/8
import json
from flask import request
from flask_restful import Resource

from app.main.steel_factory.service.jc_single_dispatch_service import dispatch
from app.main.steel_factory.service.stock_service import generate_stock_list
from app.main.steel_factory.service.truck_service import generate_truck
from app.util.result import Result


class JCSingleGoodsAllocationRoute(Resource):

    @staticmethod
    def post():
        """
        输入车辆信息，返回开单结果
        """
        json_data = json.loads(request.get_data().decode("utf-8"))
        stock_list = generate_stock_list(json_data['stock_list'])
        truck = generate_truck(json_data['truck'])
        result = dispatch(stock_list, truck)
        return Result.success_response(result)
