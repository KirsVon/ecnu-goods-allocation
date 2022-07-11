# -*- coding: utf-8 -*-
# Description: 各城市车辆历史载重分析
# Created: jjunf 2021/5/8 14:44
import json

import flask_restful
from flask import request
from flask_restful import Resource

from app.main.steel_factory.service.city_truck_load_weight_service import city_truck_load_weight_service
from app.util.my_abort import MyAbort
from app.util.result import Result

flask_restful.abort = MyAbort.my_abort


class CityTruckLoadWeight(Resource):

    @staticmethod
    def post():
        """
        各城市车辆历史载重分析服务
        """
        json_data = json.loads(request.get_data().decode("utf-8"))
        # 未传入公司id、业务板块
        if json_data.get("company_id", None) is None or json_data.get("business_module_id", None) is None:
            result = Result.error('请传入公司id(company_id)和业务模块(business_module_id)！')
        else:
            result = city_truck_load_weight_service(json_data)
        return Result.success_response(result)
