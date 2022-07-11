
from datetime import datetime
from app.main.steel_factory.dao.load_task_dao import load_task_dao
from app.main.steel_factory.dao.load_task_item_dao import load_task_item_dao
from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule import single_dispatch_filter
from app.main.steel_factory.service import redis_service
from app.util.aspect.distribute_lock import distribute_lock
from app.util.generate_id import HashKey
from app.util.result import Result
from model_config import set_singleGoodsAllocation_model_config, ModelConfig
from app.main.steel_factory.service import single_stock_service
from app.main.steel_factory.rule.single_layer_rule import merge_result, first_deal_general_stock,second_deal_general_stock
import math
from typing import List, Dict
import json

import redis
from flask import current_app
from app.util.redis.redis_pool import redis_pool

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.goods_filter_rule import goods_filter
from app.main.steel_factory.rule.split_rule import split
from app.util.enum_util import DispatchType, LoadTaskType
from app.util.get_weight_limit import get_lower_limit
from model_config import ModelConfig

alternative_stock_list_key = "alternative_stock"
m = 5

def foreign_dispatch(truck: Truck):
    """
    进行外贸单车配载
    """
    # 参数配置
    set_singleGoodsAllocation_model_config()
    # 获取指定库存
    all_stock_list = single_stock_service.get_stock(truck)
    # 库存根据总重量排序
    sorted_stock_list = sorted(all_stock_list, key=lambda all_stock_list: all_stock_list['actual_weight'], reverse=True)
    # 如果载重大于35吨，则配大于17.5吨的卷
    if truck.load_weight > 35:
        # 获取指定库存
        all_stock_list = single_stock_service.get_stock(truck)
        heavy_stock_list = [i for i in all_stock_list if i.get('weight') > 17.5]
        load_task = foreign_layer_filter(heavy_stock_list, truck)
        return load_task
    # 如果标载，
    else:
        # 从redis中获取备选列表
        alternative_stock_list = get_alternative_stock_list()
        # 如果redis中没记录
        if not alternative_stock_list:
            # 取库存前9个作为备选列表
            alternative_stock_list = [i.update({'truck_num': 0,'last_update_time': datetime.now()}) for i in sorted_stock_list[:9]]
            # 备选列表存入redis
            set_alternative_stock_list(alternative_stock_list)
        # 否则，检查alternative_stock_list中的发货通知单号没有货物可发时，移除
        else:
            for i in range(9):
                if alternative_stock_list[i].get('actual_number') < 2:
                    del alternative_stock_list[i]
                    # 从库存中选取一个补到redis列表最后
                    for k in sorted_stock_list:
                        if k.get('notice_num') not in [i.get('notice_num') for i in alternative_stock_list]:
                            alternative_stock_list[8] = k.update({'truck_num': 0, 'last_update_time': datetime.now()})
                            break
        # 第一组车次数最小值
        one_min = min(i.get('truck_num') for i in alternative_stock_list[:3])
        # 第二、三组车次数最小值
        two_min = min(i.get('truck_num') for i in alternative_stock_list[3:9])
        # 如果第一组车次数都大于2且（第一组车次数最小值-第二、三组车次数最小值）> m/2，则从第2，3组选取车次最小的发货
        if all(i.get('truck_num') for i in alternative_stock_list[:3] > 2) and (two_min-one_min) > m/2:
            for i in range(3, 9):
                if alternative_stock_list[i].get('truck_num') == two_min:
                    # send_stock为本次发货的货物
                    send_stock = alternative_stock_list[i]
                    alternative_stock_list[i]['truck_num'] += 1
                    alternative_stock_list[i]['last_update_time'] = datetime.now()
                    # 当本次发货通知单号不在第一组，且其中一个记录的车次数小于5，且最后更新时间超过2小时，将记录踢出redis
                    for j in range(3):
                        if alternative_stock_list[j].get('truck_num') < 5 and (datetime.now()-alternative_stock_list[j].get('last_update_time')).hours > 2:
                            alternative_stock_list[j] = alternative_stock_list[i]
                            del alternative_stock_list[i]
                            # 从库存中选取一个补到redis列表最后
                            for k in sorted_stock_list:
                                if k.get('notice_num') not in [i.get('notice_num') for i in alternative_stock_list]:
                                    alternative_stock_list[8] = k.update({'truck_num': 0,'last_update_time': datetime.now()})
                                    break
                            break
        # 从第一组发货
        else:
            for i in range(3):
                if alternative_stock_list[i] == one_min:
                    # send_stock为本次发货的货物
                    send_stock = alternative_stock_list[i]
                    alternative_stock_list[i]['truck_num'] += 1
                    alternative_stock_list[i]['last_update_time'] = datetime.now()
                    break




        load_task = foreign_layer_filter(all_stock_list, truck)
        return load_task


def foreign_layer_filter(stock_list: List, truck: Truck):
    """
    按层次分货
    第一层：一装一卸
    第二层：同库两装一卸
    第三层：异库两装一卸
    第四层：一装两卸
    第五层：同库两装两卸
    """
    max_weight = truck.load_weight
    function_list = [first_deal_general_stock, second_deal_general_stock]
    for i in stock_list:
        # 如果没有当前车指定的品种，并且品种不等于全部
        if (truck.big_commodity_name and i.big_commodity_name != truck.big_commodity_name
                and truck.big_commodity_name != '全部'):
            continue
        # 超过车辆载重
        if i.actual_weight > (max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT):
            continue
        for function in function_list:
            load_task = function(stock_list, i, DispatchType.SECOND, max_weight)
            if load_task:
                return merge_result(load_task)

def set_alternative_stock_list(alternative_stock_list):
    """
    更新货物列表
    """
    redis_conn = None
    try:
        redis_conn = redis.Redis(connection_pool=redis_pool)
        if not alternative_stock_list:
            return False

        json_data = json.dumps(alternative_stock_list)
        redis_conn.set(alternative_stock_list_key, json_data)
        # 设置每天结束时过期
        expire_date = datetime.datetime.combine(datetime.date.today(),
                                                datetime.time(23, 59, 59))
        redis_conn.expireat(alternative_stock_list, expire_date)
        return True
    except Exception as e:
        current_app.logger.info("set alternative stock list error")
        current_app.logger.exception(e)
    finally:
        if redis_conn:
            redis_conn.close()


def get_alternative_stock_list():
    """
    获取货物列表
    """
    redis_conn = None
    try:
        redis_conn = redis.Redis(connection_pool=redis_pool)
        json_list = redis_conn.get(alternative_stock_list_key)
        if json_list:
            alternative_stock_list = json.loads(json_list)
            return alternative_stock_list
        else:
            return []
    except Exception as e:
        current_app.logger.info("get alternative stock list error")
        current_app.logger.exception(e)
    finally:
        if redis_conn:
            redis_conn.close()

