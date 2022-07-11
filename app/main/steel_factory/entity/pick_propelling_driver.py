# -*- coding: utf-8 -*-
# @Time    : 2020/11/17 11:01
# @Author  : luchengkai
from app.util.base.base_entity import BaseEntity


class PickPropellingDriver(BaseEntity):
    """待推送司机"""

    def __init__(self, item=None):
        self.pickup_no = ''  # 摘单号
        self.pickup_prod_name = None  # 摘单品种
        self.prod_name = None  # 司机常运品种
        self.driver_id = None  # 司机id
        self.driver_name = None  # 司机姓名
        self.driver_phone = None  # 司机电话
        self.province_name = None  # 省份信息
        self.city_name = "未知城市"  # 城市信息
        self.district_name = "未知区县"  # 区县信息
        self.be_confirmed = 0  # 是否摘单
        self.pickup_start_time = None  # 摘单开始时间
        self.label_type = None  # 标签类型
        self.is_in_distance = 0  # 是否在推送范围内
        self.redis_date_time = None  # 存入redis的时间
        self.vehicle_no_list = []  # 车牌号列表
        self.vehicle_no = None  # 车牌号
        self.app_latitude = None  # APP纬度
        self.app_longitude = None  # APP经度
        self.app_dist = 9999  # APP的距离
        self.truck_latitude = None  # TRUCK纬度(车牌号列表中距离最近的)
        self.truck_longitude = None  # TRUCK经度(车牌号列表中距离最近的)
        self.truck_dist = 9999  # TRUCK的距离
        self.latitude = None  # 纬度(APP纬度、TRUCK纬度中最近的一个)
        self.longitude = None  # 经度(APP纬度、TRUCK纬度中最近的一个)
        self.dist = 9999  # 距离
        self.location_flag = None
        self.gps_create_date = None  # gps时间
        self.plan_weight = 0  # 司机当前已接调度单的总重量

        # 活跃司机字段
        self.waybill_count = 0  # 司机三个月的运单数

        self.estimate_arrive_time = None    # 预计到厂时间

        self.response_probability = 0.0     # 司机响应概率

        if item:
            self.set_attr(item)

    def __lt__(self, other):
        return self.dist < other.dist
