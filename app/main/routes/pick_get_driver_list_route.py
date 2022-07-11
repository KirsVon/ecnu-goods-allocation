# # -*- coding: utf-8 -*-
# # Description: 司机集获取
# # Created: luck 2021/01/06
# import json
# import flask_restful
# from flask import request
# from flask_restful import Resource, reqparse
# from app.main.steel_factory.service.pick_get_driver_service import get_driver
# from app.util.my_abort import MyAbort
# from app.util.my_flask_verify import MyFlaskVerify
# from app.util.result import Result
#
# flask_restful.abort = MyAbort.my_abort
#
#
# class PickGetDriverList(Resource):
#
#     @staticmethod
#     def post():
#         """
#         输入json摘单信息，返回司机集列表
#         """
#         json_data = json.loads(request.get_data().decode("utf-8"))
#         if not json_data:
#             return Result.error('参数为空！')
#         parser = reqparse.RequestParser(trim=True)
#         parser.add_argument('city', type=MyFlaskVerify.str_type, help='城市必须为非空字符串！', required=True, nullable=False,
#                             location=['json'])
#         parser.add_argument('district', type=MyFlaskVerify.str_type, help='区县必须为非空字符串！', required=True, nullable=False,
#                             location=['json'])
#         parser.add_argument('prodName', type=MyFlaskVerify.str_type, help='品名必须为非空字符串！', required=True, nullable=False,
#                             location=['json'])
#         # parser.add_argument('driverType', type=MyFlaskVerify.str_type, help='司机传入方式必须为非空字符串！', required=True,
#         #                     nullable=False,
#         #                     location=['json'])
#         if not json_data.get('pickupNo', ''):
#             parser.add_argument('totalTruckNum', type=MyFlaskVerify.number_type_positive, help='总车次数必须为大于0的数字！',
#                                 required=True,
#                                 nullable=False,
#                                 location=['json'])
#             parser.add_argument('remainTruckNum', type=MyFlaskVerify.number_type, help='剩余车次数必须数值类型！', required=True,
#                                 nullable=False,
#                                 location=['json'])
#             parser.add_argument('totalWeight', type=MyFlaskVerify.str_type, help='总重量必须为非空字符串！', required=True,
#                                 nullable=False,
#                                 location=['json'])
#             parser.add_argument('remainTotalWeight', type=MyFlaskVerify.str_type, help='剩余重量必须为非空字符串！', required=True,
#                                 nullable=False,
#                                 location=['json'])
#
#         parser.parse_args()
#         result = get_driver(json_data)
#         return Result.success_response(result)
