# -*- coding: utf-8 -*-
# Description: 成都管厂摘单分货服务入口
# Created: jjunf 2021/3/29 16:19
from threading import Thread
from typing import List, Dict
import config
from app.main.pipe_factory.dao.pick_save_log_dao import save_pick_log
import json
from datetime import datetime

from app.main.pipe_factory.entity.pick_task import PickTask
from app.main.pipe_factory.entity.order_wt import OrderWt
from app.main.pipe_factory.rule.pick_create_pick_task_rule import create_pick_task_rule
from app.main.pipe_factory.service.pick_order_wt_service import get_order_wt
from app.util.date_util import get_now_date
from app.util.enum_util import CdpzjhLoadTaskType
from app.util.rest_template import RestTemplate
from app.util.result import Result
from model_config import ModelConfig


def pick_cdpzjh_dispatch_service(json_data):
    """
    成都管厂摘单分货服务入口
    :return:
    """
    # 获取自提、非自提、指定司机的委托订单
    self_pick_order_wt_list, non_self_pick_order_wt_list, special_consumer_order_wt_list = get_order_wt(
        json_data["data"])
    # 将非自提的按照省市区合并为一条摘单计划
    non_self_pick_list = create_pick_task_rule(non_self_pick_order_wt_list, ['province', 'city'])
    # 将自提的每单是一条摘单计划
    self_pick_list = create_pick_task_rule(self_pick_order_wt_list, ['order_no'])
    # 将客户指定司机的委托订单合并为一条摘单计划(绑定的客户合并在一起)
    special_consumer_pick_list = create_pick_task_rule(special_consumer_order_wt_list,
                                                       ['province', 'city', 'driver_pool_id'])
    # 将结果保存到数据库
    Thread(target=save_result, args=(non_self_pick_list, self_pick_list, special_consumer_pick_list,)).start()
    # 格式转换：非自提、客户指定司机
    non_self_and_special_consumer_pick_result_list = data_format_non_self(non_self_pick_list,
                                                                          special_consumer_pick_list)
    # 格式转换：自提
    self_pick_result_list = data_format_self(self_pick_list)
    # 结果
    result_dic = {"non_self_and_special_consumer_pick": non_self_and_special_consumer_pick_result_list,
                  "self_pick": self_pick_result_list}
    # 后台交互
    interaction_with_java(result_dic, json_data)
    return Result.success(data=result_dic)


def interaction_with_java(result_dic: Dict, json_data):
    """
    后台交互
    :param result_dic:
    :param json_data:
    :return:
    """
    non_self_and_special_consumer_pick_result_list = result_dic.get("non_self_and_special_consumer_pick", [])
    self_pick_result_list = result_dic.get("self_pick", [])
    # 打印日志
    if json_data["data"] == ModelConfig.CDPZJH_REQUEST_FLAG:
        from celery.utils.log import get_task_logger
        # 获取celery执行器的日志记录器
        logger = get_task_logger('celery_worker')
        # 打印日志
        logger.info('参数：' + json.dumps(result_dic, ensure_ascii=False))
    else:
        from flask import current_app
        # 打印日志
        current_app.logger.info('参数：' + json.dumps(result_dic, ensure_ascii=False))
    # 自提后台交互
    if self_pick_result_list:
        try:
            self_pick_url = config.get_active_config().COMMISSION_URL + '/order/selfExtractionToOrderPlan'
            res3 = RestTemplate.do_post(self_pick_url, self_pick_result_list)
        except Exception as e:
            from flask import current_app
            # 打印日志
            current_app.logger.error('commission_error(自提)：' + str(e))
    # 非自提、客户指定司机后台交互
    if non_self_and_special_consumer_pick_result_list:
        try:
            non_self_pick_url = config.get_active_config().TENDER_URL + '/pickUpOrder/insertPickOrderAuto'
            res1 = RestTemplate.do_post(non_self_pick_url, non_self_and_special_consumer_pick_result_list)
        except Exception as e:
            from flask import current_app
            # 打印日志
            current_app.logger.error('tender_error(非自提、客户指定司机)：' + str(e))
        # 定时不调用自动下发接口
        if json_data["data"] == ModelConfig.CDPZJH_REQUEST_FLAG:
            pass
        # 手动调用摘单分货按钮时调用自动下发接口(该接口耗时可能比较长)
        else:
            t1 = datetime.now()
            try:
                non_self_pick_issue_url = (config.get_active_config().TENDER_URL +
                                           '/pickUpPushLine/autoPushPickupOrderAll')
                res2 = RestTemplate.do_post(non_self_pick_issue_url, {"companyId": json_data["company_id"]})
            except Exception as e:
                from flask import current_app
                # 打印日志
                current_app.logger.error('tender_error(自动下发)：' + str(e))
            t2 = datetime.now()
            from flask import current_app
            # 打印日志
            current_app.logger.info('tender自动下发接口耗时：' + str(int((t2 - t1).total_seconds() * 1000)))


def save_result(non_self_pick_list, self_pick_list, special_consumer_pick_list):
    """
    保存摘单记录
    :param special_consumer_pick_list:
    :param self_pick_list:
    :param non_self_pick_list:
    :return:
    """
    if not non_self_pick_list and not self_pick_list and not special_consumer_pick_list:
        return None
    values = []
    # 非自提记录
    if non_self_pick_list:
        values.extend(get_save_values(non_self_pick_list, load_task_type=CdpzjhLoadTaskType.TYPE_1.value))
    # 自提记录
    if self_pick_list:
        values.extend(get_save_values(self_pick_list, load_task_type=CdpzjhLoadTaskType.TYPE_2.value))
    # 客户指定司机的记录
    if special_consumer_pick_list:
        values.extend(get_save_values(special_consumer_pick_list, load_task_type=CdpzjhLoadTaskType.TYPE_3.value))
    save_pick_log.save_pick_log(values)


def get_save_values(pick_list: List[PickTask], load_task_type=''):
    """
    将pick_list对象转换成存到数据库的values
    :param load_task_type:
    :param pick_list:
    :return:
    """
    values = []
    create_date = get_now_date()
    for pick in pick_list:
        pick_item = pick.items[0]
        order_wt_list = pick_item.items
        for order_wt in order_wt_list:
            for order_wt_item in order_wt.items:
                item_tuple = (pick.pick_id,
                              order_wt.company_id,
                              order_wt_item.business_module_id,
                              pick.total_weight,
                              pick.truck_num,
                              pick.remark,
                              order_wt.order_no,
                              load_task_type,
                              order_wt.total_weight,
                              order_wt_item.total_weight,
                              order_wt_item.province,
                              order_wt_item.city,
                              order_wt_item.district,
                              order_wt_item.town,
                              order_wt_item.consumer,
                              order_wt_item.r_vehicle,
                              order_wt_item.recommend_driver,
                              order_wt_item.recommend_mobile,
                              order_wt_item.bind_no,
                              order_wt_item.pick_no,
                              order_wt_item.order_no,
                              order_wt_item.delegation_priority,
                              order_wt_item.driver_pool_id,
                              create_date
                              )
                values.append(item_tuple)
    return values


def data_format_self(pick_list: List[PickTask]):
    """
    自提格式转换
    :param pick_list:
    :return:
    """
    result_list = []
    if pick_list:
        for pick_task in pick_list:
            item_dic = {"requestCompanyId": pick_task.company_id}
            t_order_model_list = []
            # 当前摘单计划的委托订单
            order_wt_list: List[OrderWt] = pick_task.items[0].items
            for order_wt in order_wt_list:
                # 拼车的多个明细以列表形式返回
                for order_wt_item in order_wt.items:
                    order_wt_item_dict = {
                        "orderNo": order_wt_item.order_no,
                        "businessModuleId": order_wt_item.business_module_id,
                        "companyId": order_wt_item.company_id,
                    }
                    t_order_model_list.append(order_wt_item_dict)
            item_dic["tOrderModelList"] = t_order_model_list
            item_dic["tTenderPriceModel"] = {
                "vehicleNo": order_wt_list[0].r_vehicle,
                "name": order_wt_list[0].recommend_driver,
                "mobile": order_wt_list[0].recommend_mobile
            }
            result_list.append(item_dic)
    return result_list


def data_format_non_self(non_self_pick_list: List[PickTask], special_consumer_pick_list: List[PickTask]):
    """
    非自提、客户指定司机格式转换
    :param special_consumer_pick_list:
    :param non_self_pick_list:
    :return:
    """
    # 摘单记录的格式转换
    p_list = []
    # 非自提
    if non_self_pick_list:
        for pick_task in non_self_pick_list:
            p_dic = {
                "sourceName": "流向:" + pick_task.province + pick_task.city + " " + pick_task.order_no,
                "consignorCompanyId": pick_task.company_id,
                "companyId": pick_task.company_id,
                "businessModuleId": pick_task.business_module_id,
                "startPoint": pick_task.start_point,
                "orderNo": pick_task.order_no,
                "totalWeight": float(pick_task.total_weight),
                "truckNum": pick_task.truck_num,
                "bigCommodity": "钢管",
                "province": pick_task.province,
                "city": pick_task.city,
                "endPoint": pick_task.district,
                "town": pick_task.town,
                "remark": pick_task.remark,
                "consumerId": None,
                "pickConsumerId": ','.join([str(consumer) for consumer in pick_task.consumer]),
                "priceFlag": False,
                "items": [{
                    "consignorCompanyId": item.company_id,
                    "companyId": item.company_id,
                    "businessModuleId": pick_task.business_module_id,
                    "orderNo": item.order_no,
                    "totalWeight": float(item.total_weight),
                    "truckNum": item.truck_num,
                    "bigCommodity": "钢管",
                    "province": pick_task.province,
                    "city": item.city,
                    "endPoint": item.district,
                    "town": item.town,
                    "remark": item.remark,
                    "consumerId": None,
                    "pickConsumerId": ','.join([str(consumer) for consumer in pick_task.consumer]),
                    "priceFlag": False
                } for item in pick_task.items]
            }
            p_list.append(p_dic)
    # 客户指定司机
    if special_consumer_pick_list:
        for pick_task in special_consumer_pick_list:
            p_dic = {
                "sourceName": "司机池:" + pick_task.driver_pool_name + " " + pick_task.order_no,
                "consignorCompanyId": pick_task.company_id,
                "companyId": pick_task.company_id,
                "businessModuleId": pick_task.business_module_id,
                "startPoint": pick_task.start_point,
                "orderNo": pick_task.order_no,
                "totalWeight": float(pick_task.total_weight),
                "truckNum": pick_task.truck_num,
                "bigCommodity": "钢管",
                "province": pick_task.province,
                "city": pick_task.city,
                "endPoint": pick_task.district,
                "town": pick_task.town,
                "remark": pick_task.remark,
                "consumerId": pick_task.driver_pool_id,
                "pickConsumerId": ','.join([str(consumer) for consumer in pick_task.consumer]),
                "priceFlag": True,
                "items": [{
                    "consignorCompanyId": item.company_id,
                    "companyId": item.company_id,
                    "businessModuleId": pick_task.business_module_id,
                    "orderNo": item.order_no,
                    "totalWeight": float(item.total_weight),
                    "truckNum": item.truck_num,
                    "bigCommodity": "钢管",
                    "province": pick_task.province,
                    "city": item.city,
                    "endPoint": item.district,
                    "town": item.town,
                    "remark": item.remark,
                    "consumerId": item.driver_pool_id,
                    "pickConsumerId": ','.join([str(consumer) for consumer in pick_task.consumer]),
                    "priceFlag": True
                } for item in pick_task.items]
            }
            p_list.append(p_dic)
    return p_list


if __name__ == '__main__':
    pick_cdpzjh_dispatch_service({
        "company_id": "C000000888",
        "data": [
            {"order_no": "WT210610000723",
             "company_id": "C000000888",
             "consignor_company_id": "C000000878",
             "city": "成都市",
             "end_point": "P000003481",
             "business_module_id": "001",
             "carrier_company_id": "C000000888",
             "remark": "欠款",
             "business_nature": "YWXZ10",
             "total_weight": 35.785,
             "update_date": "2021-06-10 22:18:21",
             "rowid": 1850184,
             "pick_no": "t0-86330",
             "total_sheet": 0.0,
             "province": "四川省",
             "trans_weight": 0.0,
             "main_product_list_no": "t0-86330",
             "start_point": "P000003477",
             "district": "金牛区",
             "consignor_company_id_root": "C000000888",
             "trans_sheet": 0.0,
             "create_date": "2021-06-10 22:17:24",
             "consumer": "C000006055",
             "status": "ETST10"
             }],
        "business_module_id": "001"})
