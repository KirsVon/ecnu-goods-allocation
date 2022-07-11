# -*- coding: utf-8 -*-
# Description: 用户模块
# Created: shaoluyu 2019/10/29
# Modified: shaoluyu 2019/10/29; shaoluyu 2019/06/20

from flask import Blueprint
from flask import jsonify
from flask_restful import Api
from app.main.routes.ecnu_single_goods_allocation_route import EcnuSingleGoodsAllocationRoute
from app.main.routes.jc_single_goods_allocation_route import JCSingleGoodsAllocationRoute

blueprint = Blueprint('main', __name__)
api = Api(blueprint)

# 华师大单车配货请求
api.add_resource(EcnuSingleGoodsAllocationRoute, '/ecnuSingleGoodsAllocation')
api.add_resource(JCSingleGoodsAllocationRoute, '/jcSingleGoodsAllocation')


@blueprint.route('/demo', methods=['GET'])
def demo():
    return jsonify({"name": "gc goods allocation"})
