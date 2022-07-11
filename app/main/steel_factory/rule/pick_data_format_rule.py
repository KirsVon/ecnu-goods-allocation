# -*- coding: utf-8 -*-
# Description: 筛选待二次推送的摘单计划
# Created: luchengkai 2021/01/06
from typing import List
from app.main.steel_factory.dao.pick_propelling_label_dao import pick_label_dao
from app.main.steel_factory.entity.pick_order_stock import PickOrderStock
from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.main.steel_factory.entity.pick_propelling_driver import PickPropellingDriver
from app.main.steel_factory.rule.pick_normal_rule import pick_cd_deal
from app.util.date_util import get_now_date
from app.util.round_util import round_util_by_digit
from model_config import ModelConfig


def to_trans_batch_service(correct_list: List[PickOrderStock]):
    """
    修改调度单状态
    :param correct_list:
    :return:
    """
    # 推送记录的格式转换
    result_list = []
    for order in correct_list:
        data = {
            'companyId': 'C000000888',
            "dateEndSuffix": "23:59:59",
            "dateStartSuffix": " 00:00:00",
            "intelligentDispatchStatus": "IDS70",
            "orderNo": order.order_no,
            "returned": 0
        }
        result_list.append(data)
    return result_list


def to_trans_push_service():
    """
    直接下发
    :return:
    """
    # 推送记录的格式转换
    data = {
        'requestCompanyId': 'C000000888',
        "requestCompanyName": "成都管厂物流",
        "requestCompanyType": "GSLX20",
        "requestUserId": "",
        "requestUserSegmentId": "001",
        "dateEndSuffix": "23:59:59",
        "dateStartSuffix": " 00:00:00",
        "returned": 0
    }
    return data


def to_capacity(propelling: PickPropelling, distance, recommend_type=None):
    """
    获取运力池司机集:调用运力服务接口
    :param propelling:
    :param distance:
    :param recommend_type:
    :return:
    """
    # 推送记录的格式转换
    data = {
            'pickup_no': propelling.pickup_no,
            'distance': distance,
            'recommend_type': recommend_type,
            'end_province': propelling.province_name,
            'end_city_name': propelling.city_name,
            'end_district_name': propelling.district_name,
            'consignee_company_id': propelling.consignee_company_ids,
            'company_id': propelling.company_id,
            'business_module_id': propelling.business_module_id,
            'prod_name': propelling.prod_name}
    return data


def from_capacity(propelling: PickPropelling, res_list):
    """
    获取运力池司机集信息：接收运力服务返回司机集
    :param propelling:
    :param res_list:
    :return:
    """
    result_list = []
    if not res_list["recommend_list"]:
        return []
    # 单个推送对象的格式转换
    for data in res_list["recommend_list"]:
        driver = PickPropellingDriver()
        driver.district_name = data.get('district_name', "未知区县")
        driver.driver_id = data.get('driver_id', "未知id")
        driver.driver_name = data.get('driver_name', "未知姓名")
        driver.driver_phone = data.get('driver_tel', "未知手机号")
        driver.vehicle_no = data.get('vehicle_no', "位置车牌")
        driver.app_latitude = data.get('app_latitude', "0.0")
        driver.app_longitude = data.get('app_longitude', "0.0")
        driver.app_dist = data.get('app_dist', 1000.0)
        driver.truck_latitude = data.get('truck_latitude', "0.0")
        driver.truck_longitude = data.get('truck_longitude', "0.0")
        driver.truck_dist = data.get('truck_dist', 1000.0)
        driver.latitude = data.get('latitude', "0.0")
        driver.longitude = data.get('longitude', "0.0")
        driver.dist = data.get('dist', 1000.0)
        driver.label_type = data.get('label_type', "未知类型")
        # driver.estimate_arrive_time = data['estimate_arrive_time']
        driver.pickup_no = propelling.pickup_no
        result_list.append(driver)
    return result_list


def data_format_to_java(propelling: PickPropelling, num):
    """
    获取运力池司机集:调用数仓接口
    :param propelling:
    :param num:
    :return:
    """
    flow_relation = []
    # 如果距离类型是50公里外，则增加运力池拓展操作
    if propelling.dist_type == ModelConfig.PICK_RESULT_TYPE.get("DEFAULT"):
        # 查询流向关联表
        flow_relation = pick_label_dao.select_flows_relation(propelling)
        # 对结果list排序并截取前3位
        flow_relation.sort()
        flow_relation = flow_relation[0:3]
    # 推送记录的格式转换
    data = {'taskTime': num}
    tmp_list = []
    tmp_dic = {"province": "山东省", "city": propelling.city_name, "district": propelling.district_name}
    tmp_list.append(tmp_dic)
    tmp_list.extend([{"province": "山东省", "city": item.related_city, "district": item.related_district}
                     for item in flow_relation])
    data['pointList'] = tmp_list
    return data


def data_format_from_java(propelling: PickPropelling, res_list):
    """
    获取运力池司机集信息：接收数仓返回司机集
    :param propelling:
    :param res_list:
    :return:
    """
    result_list = []
    if res_list:
        # 单个推送对象的格式转换
        for data in res_list:
            driver = PickPropellingDriver()
            driver.district_name = data['district']
            driver.driver_id = data['driverId']
            driver.driver_name = data['driverName']
            driver.driver_phone = data['driverTel']
            driver.label_type = ModelConfig.PICK_LABEL_TYPE['L1']
            driver.pickup_no = propelling.pickup_no
            result_list.append(driver)
    return result_list


def data_format_insert(wait_propelling_list: List[PickPropelling]):
    """
    插入司机：调用后台插入司机接口
    :param wait_propelling_list:
    :return:
    """
    # result_dic = {'requestCompanyId': "C000062070", 'requestCompanyName': "会好运单车",
    #               'requestUserId': "U000050305", 'requestCompanyType': "GSLX30", 'requestUserSegmentId': None}
    # result_dic = {}
    # 推送记录的格式转换
    data = []
    if wait_propelling_list:
        # 单个推送对象的格式转换
        for wait_propelling in wait_propelling_list:
            tmp_dic = {"pickupNo": wait_propelling.pickup_no}

            # 转换司机列表格式
            driver_list = []
            for driver in wait_propelling.drivers:
                temp_app_dist = '' if (driver.app_dist is None or driver.app_dist > 5500) else driver.app_dist
                if temp_app_dist:
                    temp_app_dist = round_util_by_digit(temp_app_dist, 2)
                temp_truck_dist = '' if (driver.truck_dist is None or driver.truck_dist > 5500) else driver.truck_dist
                if temp_truck_dist:
                    temp_truck_dist = round_util_by_digit(temp_truck_dist, 2)
                driver_dic = {
                    "driverId": driver.driver_id,
                    "driverTel": driver.driver_phone,
                    "driverName": driver.driver_name,
                    "appDist": temp_app_dist,
                    "vehicleDist": temp_truck_dist
                }
                driver_list.append(driver_dic)

            # 如果司机列表为空，不插入
            if len(driver_list) == 0:
                continue

            # 将司机列表加入对应的推送对象
            tmp_dic["driverList"] = driver_list
            data.append(tmp_dic)
    return data


def data_format_msg(wait_propelling_list: List[PickPropelling]):
    """
    格式转换：消息推送，调用后台短信推送接口
    :param wait_propelling_list:
    :return:
    """
    # result_dic = {'requestCompanyId': "C000062070", 'requestCompanyName': "会好运单车",
    #               'requestUserId': "U000050305", 'requestCompanyType': "GSLX30", 'requestUserSegmentId': None}
    # result_dic = {}
    # 推送记录的格式转换
    data = []
    if wait_propelling_list:
        # 单个推送对象的格式转换
        for wait_propelling in wait_propelling_list:
            tmp_dic = {
                "pickup_no": wait_propelling.pickup_no,
                "remainTruckNum": wait_propelling.remain_truck_num,
                "company_id": wait_propelling.company_id,
                "business_module_id": wait_propelling.business_module_id
            }
            for driver in wait_propelling.drivers:
                # 记录存入redis的时间
                driver.redis_date_time = get_now_date()
            # 筛除冷却期司机，并把本次推送消息的司机放入冷却
            wait_propelling.drivers = pick_cd_deal(wait_propelling.drivers)
            # 转换司机列表格式
            driver_list = []
            for driver in wait_propelling.drivers:
                driver_dic = {
                    "userId": driver.driver_id,
                    "phoneNumber": driver.driver_phone
                }
                driver_list.append(driver_dic)
            # 如果司机列表为空，不插入
            if len(driver_list) == 0:
                continue
            # 将司机列表加入对应的推送对象
            tmp_dic["driver_list"] = driver_list
            data.append(tmp_dic)

    return data


def data_format_district(json_data):
    """
    模型生成十公里内司机集：数仓传入摘单计划信息，转换成PickPropelling格式
    :param json_data:
    :return:
    """
    # json_data格式转换
    # for wait_propelling in json_data:
    pick_propelling_list = []
    pick_propelling = PickPropelling()
    pick_propelling.province_name = json_data.get('province', '未知')
    pick_propelling.city_name = json_data.get('city', '未知')
    pick_propelling.pickup_no = json_data.get('pickupNo', '')
    pick_propelling.district_name = json_data.get('district', '未知')
    pick_propelling.prod_name = json_data.get('prodName', '未知')
    pick_propelling.total_truck_num = json_data.get('totalTruckNum', 0)
    pick_propelling.remain_truck_num = json_data.get('remainTruckNum', 1)
    pick_propelling.total_weight = json_data.get('totalWeight', '')
    pick_propelling.remain_total_weight = json_data.get('remainTotalWeight', '')
    pick_propelling.driver_type = json_data.get('driverType', '')
    pick_propelling.consignee_company_id = json_data.get('ConsumerId', '未知客户')
    pick_propelling.consignee_company_ids = json_data.get('pickConsumerId', '未知客户')
    pick_propelling.company_id = json_data.get('requestCompanyId', 'C000062070')
    pick_propelling.business_module_id = json_data.get('requestUserSegmentId', '020')
    pick_propelling.is_assign_drivers = json_data.get('priceFlag', '0')
    pick_propelling_list.append(pick_propelling)
    return pick_propelling_list


def data_format_driver(propelling_driver_list, total_count, current_count):
    """
    模型生成十公里内司机集：转换司机集格式，传给数仓
    :param propelling_driver_list:
    :param total_count:
    :param current_count:
    :return:
    """
    # result_dic = {'requestCompanyId': "C000062070", 'requestCompanyName': "会好运单车",
    #               'requestUserId': "U000050305", 'requestCompanyType': "GSLX30", 'requestUserSegmentId': None}
    # result_dic = {}
    # json_data格式转换
    # 推送记录的格式转换
    tmp_dic = {
        "currentCount": current_count,
        "totalCount": total_count
    }

    # 转换司机列表格式
    driver_list = []
    if propelling_driver_list:
        for propelling in propelling_driver_list:
            for driver in propelling.drivers:
                temp_app_dist = '' if (driver.app_dist is None or driver.app_dist > 5500) else driver.app_dist
                if temp_app_dist:
                    temp_app_dist = round_util_by_digit(temp_app_dist, 2)
                temp_truck_dist = '' if (driver.truck_dist is None or driver.truck_dist > 5500) else driver.truck_dist
                if temp_truck_dist:
                    temp_truck_dist = round_util_by_digit(temp_truck_dist, 2)
                driver_dic = {
                    "driverId": driver.driver_id,
                    "driverName": driver.driver_name,
                    "driverTel": driver.driver_phone,
                    # "district": driver.district_name,
                    "appDist": temp_app_dist,
                    "vehicleDist": temp_truck_dist
                }
                driver_list.append(driver_dic)
        # 将司机列表加入对应的推送对象
    tmp_dic["driverList"] = driver_list
    return tmp_dic


def data_format_truck(str_truck):
    """
    获取车辆位置信息：转换车辆集格式，调用中交兴路数据获取接口
    :param str_truck:
    :return:
    """
    # result_dic = {'requestCompanyId': "C000062070", 'requestCompanyName': "会好运单车",
    #               'requestUserId': "U000050305", 'requestCompanyType': "GSLX30", 'requestUserSegmentId': None}
    # result_dic = {}
    # json_data格式转换
    # 推送记录的格式转换
    tmp_dic = {"vclNs": str_truck}
    return tmp_dic


def data_format_truck_result(json_data):
    """
    获取车辆位置信息：中交兴路车辆位置信息，转换成PickPropellingDriver格式
    :param json_data:
    :return:
    """
    # result_dic = {'requestCompanyId': "C000062070", 'requestCompanyName': "会好运单车",
    #               'requestUserId': "U000050305", 'requestCompanyType': "GSLX30", 'requestUserSegmentId': None}
    # result_dic = {}
    # json_data格式转换
    if json_data and json_data['data']:
        # json_data格式转换
        # for wait_propelling in json_data:
        pick_propelling_list = []
        for data in json_data['data']:
            if not data["lon"] or not data["lat"]:
                continue
            pick_propelling = PickPropellingDriver()
            pick_propelling.vehicle_no = data["vno"]
            pick_propelling.longitude = data["lon"]
            pick_propelling.latitude = data["lat"]
            pick_propelling_list.append(pick_propelling)
        return pick_propelling_list

    return []
