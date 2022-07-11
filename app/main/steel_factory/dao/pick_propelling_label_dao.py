# -*- coding: utf-8 -*-
# Description:
# Created: luchengkai 2020/11/24 14:43
from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.main.steel_factory.entity.pick_propelling_driver import PickPropellingDriver
from app.main.steel_factory.entity.pick_propelling_flow_relation import PickPropellingFlowRelation
from app.util.base.base_dao_2 import BaseDao2
from app.util.base.base_dao import BaseDao
import pandas as pd


class PickLabelDao(BaseDao):
    def select_new_driver(self):
        """
        查询新司机信息
        :return:
        """
        sql = """
        SELECT 
        mobile driver_phone,
        `name` driver_name,
        driver_id,
        city city_name
        FROM 
        db_cdm.zd_new_driver_message"""
        read_data = self.select_all(sql)
        return [PickPropellingDriver(i) for i in read_data]

    def select_user_common_flow(self):
        """
        查询司机常运流向列表
        :return:
        """
        sql = """
        SELECT
            ucf.driver_id,
            ubi.`name` driver_name,
            ubi.`mobile` driver_phone,
            ucf.end_province_name province_name,
            ucf.end_city_name city_name,
            ucf.end_district_name district_name
        FROM
            db_portrayal.user_common_flow ucf
        LEFT JOIN db_portrayal.user_base_info ubi ON ucf.driver_id = ubi.user_id 
        LEFT JOIN db_portrayal.user_behavior_collect ubc ON ubc.user_id = ubi.user_id
        WHERE
            ucf.end_province_name = '山东省' 
        AND ubi.`name` != ''
        AND ubi.`mobile` != ''
        AND ubc.is_several_carrier = '单车队'
        AND ubc.carrier_company_name = '会好运单车'
        """
        data = self.select_all(sql)
        return [PickPropellingDriver(i) for i in data]

    def select_user_common_kind(self, values):
        """
        查询司机常运品种列表
        :return:
        """
        sql = """
        SELECT
        uck.driver_id,
        uck.kind_name prod_name,
        uck.total_weight,
        ubi.NAME driver_name,
        ubi.mobile driver_phone 
        FROM
        ( 
            SELECT 
                driver_id, 
                MAX( total_weight ) total_weight 
            FROM db_portrayal.user_common_kind 
            WHERE total_weight > 100 
            GROUP BY driver_id 
        ) tmp
        JOIN db_portrayal.user_common_kind uck 
        ON uck.driver_id = tmp.driver_id 
        AND uck.total_weight = tmp.total_weight
        AND uck.kind_name in ({})
        JOIN db_portrayal.user_base_info ubi 
        ON uck.driver_id = ubi.user_id
        JOIN db_portrayal.user_behavior_collect ubc 
        ON ubc.user_id = ubi.user_id 
        AND ubc.is_several_carrier = '单车队' 
        AND ubc.carrier_company_name = '会好运单车' 
        """
        commodity_values = "'"
        commodity_values += "','".join(values)
        commodity_values += "'"
        data = self.select_all(sql.format(commodity_values))
        return [PickPropellingDriver(i) for i in data]

    def select_flows_relation(self, propelling: PickPropelling):
        """
        查询流向关联表
        :return:
        """
        sql = """
        SELECT *
        FROM
        t_flows_relation
        where main_city = '{}' and main_district = '{}'
        """
        data = self.select_all(sql.format(propelling.city_name, propelling.district_name))
        return [PickPropellingFlowRelation(i) for i in data]

    def select_truck_driver(self, truck_no_list):
        """
        查询车牌对应司机信息
        :return:
        """
        sql = """
        SELECT
        dv.driver_id,
        dv.vehicle_no,
        u.mobile driver_phone,
        u.`name` driver_name
        FROM db_ods.db_sys_t_driver_vehicle dv
        LEFT JOIN db_ods.db_sys_t_user u ON dv.driver_id = u.user_id
        WHERE 1 = 1
        AND dv.default_vehicle_no = '1'
        AND IFNULL(u.mobile, '') != ''
        AND IFNULL(u.`name`, '') != ''
        AND IFNULL(dv.driver_id, '') != ''
        AND dv.vehicle_no IN ({})
        """
        truck_no_values = "'"
        truck_no_values += "','".join(truck_no_list)
        truck_no_values += "'"
        sql = sql.format(truck_no_values)
        data = self.select_all(sql)
        return [PickPropellingDriver(i) for i in data]


pick_label_dao = PickLabelDao()
