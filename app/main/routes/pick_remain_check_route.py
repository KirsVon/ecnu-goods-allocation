# -*- coding: utf-8 -*-
# Description: 摘单时判断剩余车次数
# Created: jjunf 2021/3/17 17:27
import json
import flask_restful
from flask import request
from flask_restful import Resource
from app.main.steel_factory.service.pick_remain_check_service import check
from app.util.my_abort import MyAbort
from app.util.result import Result

flask_restful.abort = MyAbort.my_abort


class PickRemainCheck(Resource):

    @staticmethod
    def post():
        """
        输入当前摘单相关信息；返回True：当前摘单还有剩余，可摘单；False：当前摘单没有剩余，不可摘单
        """
        json_data = json.loads(request.get_data().decode("utf-8"))
        result = check(json_data)
        return Result.success_response(result)
