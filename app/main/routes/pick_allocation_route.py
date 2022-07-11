# -*- coding: utf-8 -*-
# Description: 
# Created: jjunf 2021/3/31 15:56
import json
import flask_restful
from flask import request
from flask_restful import Resource

from app.main.pipe_factory.service.pick_dispatch_service import pick_cdpzjh_dispatch_service
from app.util.my_abort import MyAbort
from app.util.result import Result

flask_restful.abort = MyAbort.my_abort


class PickAllocation(Resource):

    @staticmethod
    def post():
        """
        输入json库存信息，根据公司id、业务板块调用不同的方法，返回分好的摘单记录
        """
        json_data = json.loads(request.get_data().decode("utf-8"))
        # 未传入公司id、业务板块
        if json_data.get("company_id", None) is None or json_data.get("business_module_id", None) is None:
            result = Result.error('请传入请求公司id(company_id)和业务模块(business_module_id)！')
        # 成都管厂摘单分货
        elif json_data["company_id"] == "C000000888" and json_data["business_module_id"] == "001":
            if json_data["data"]:
                result = pick_cdpzjh_dispatch_service(json_data)
            else:
                result = Result.error('请传入可分配的货物！')
        # 不支持的公司/业务板块
        else:
            result = Result.error(
                '不支持的公司(' + json_data["company_id"] + ')/业务模块(' + json_data["business_module_id"] + ')！')
        return Result.success_response(result)
