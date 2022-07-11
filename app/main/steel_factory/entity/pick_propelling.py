# -*- coding: utf-8 -*-
# @Time    : 2020/11/16
# @Author  : luchengkai
from app.util.base.base_entity import BaseEntity
from model_config import ModelConfig


class PickPropelling(BaseEntity):
    """待推送摘单计划表"""

    def __init__(self, item=None):
        self.pickup_no = ''  # 摘单号
        self.company_id = ''    # 业务公司
        self.business_module_id = ''  # 业务板块
        self.is_assign_drivers = 0      # 是否客户指定司机

        self.prod_name = "未知品种"  # 摘单品种
        self.consignee_company_id = "未知客户"    # 客户id
        self.consignee_company_ids = "未知客户们"    # 客户id们
        self.start_point = None  # 装货地
        self.end_point = None  # 卸货地
        self.province_name = None    # 卸货省份
        self.city_name = None  # 卸货城市
        self.district_name = None  # 卸货区县

        self.total_truck_num = 0  # 总车次
        self.remain_truck_num = 1  # 剩余车次
        self.total_weight = 0  # 总重量
        self.remain_total_weight = 0  # 剩余总重量
        self.single_weight = 0  # 单车重量

        self.driver_type = None  # 司机传入方式
        self.pickup_start_time = None  # 摘单开始时间
        self.create_date = None  # 下发时间

        self.drivers = []  # 司机列表
        self.exist_driver_list = []  # 已收到摘单推送的司机列表
        self.exist_driver_id_list = []  # 已收到摘单推送的司机id列表
        self.dist_type = ModelConfig.PICK_RESULT_TYPE.get("DEFAULT")
        self.wait_driver_count = 0  # 司机上限
        if item:
            self.set_attr(item)
