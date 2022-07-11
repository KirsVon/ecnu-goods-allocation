# -*- coding: utf-8 -*-
# Description:
# Created: luchengkai 2020/11/16 14:43
from collections import defaultdict

from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.main.steel_factory.entity.pick_propelling_black_list import PickBlackListDao
from app.main.steel_factory.entity.pick_propelling_driver import PickPropellingDriver
from app.util.base.base_dao import BaseDao
from app.util.base.base_dao_2 import BaseDao2
from app.util.base.base_dao_3 import BaseDao3


class PickPropellingDao(BaseDao):

    def select_wait_pick_list(self, company_id, business_model_id):
        """
        查询当日摘单计划列表
        :return:
        """
        sql = """
        SELECT
            tmp.pickup_no,
            tmp.consignee_company_id,
            tmp.consignee_company_ids,
            tmp.prod_name,
            tmp.start_point,
            tmp.end_point,
            tmp.province_name,
            tmp.city_name,
            tmp.district_name,
            tmp.total_truck_num total_truck_num,
            tmp.remain_truck_num remain_truck_num,
            tmp.total_weight,
            tmp.remain_total_weight,
            tmp.driver_type,
            tmp.pickup_start_time,
            tmp.create_date,
            tmp.price_flag is_assign_drivers
        FROM
            (
        SELECT
            DISTINCT pickup_no,
            consignee_company_id,
            consignee_company_ids,
            start_point,
            end_point,
            province_name,
            city_name,
            district_name,
            total_truck_num,
            remain_truck_num,
            total_weight,
            remain_total_weight,
            prod_name,
            driver_type,
            pickup_start_time,
            create_date,
            price_flag
        FROM
            db_ads.zd_pickup_order_driver 
        WHERE 1 = 1
            AND pickup_status IN ('PUST20', 'PUST30') 
            AND driver_type IN ('SJLY10','SJLY20')
            AND company_id = '{}'
            AND business_module_id = '{}'
            ) tmp 
        WHERE 1 = 1
            AND pickup_start_time < SUBDATE( NOW( ), INTERVAL 5 MINUTE ) 
        GROUP BY
            tmp.pickup_no,
            tmp.start_point,
            tmp.end_point,
            tmp.prod_name
        
        """
        sql = sql.format(company_id, business_model_id)
        data = self.select_all(sql)
        return [PickPropelling(i) for i in data]

    def select_wait_driver_list(self, company_id, business_model_id):
        """
        查询当日摘单计划司机列表
        :return:
        """
        sql = """
        SELECT
            pickup_no,
            driver_id,
            driver_phone,
            district_name,
            prod_name,
            be_order_confirmed as be_confirmed
        FROM
            db_ads.zd_pickup_order_driver
        WHERE 1 = 1
            AND pickup_status IN ('PUST20', 'PUST30') 
            AND driver_type IN ('SJLY10','SJLY20')
            AND company_id = '{}'
            AND business_module_id = '{}'
            AND pickup_start_time < SUBDATE( NOW( ), INTERVAL 5 MINUTE )
        """
        data = self.select_all(sql.format(company_id, business_model_id))
        return [PickPropellingDriver(i) for i in data]

    def select_black_list(self):
        """
        查询在黑名单的司机列表
        :return:
        """
        sql = """
                SELECT
                    driver_id,
                    district district_name,
                    product_name prod_name,
                    `count` ignore_count,
                    update_time 
                FROM
                    t_driver_no_interest_count 
                WHERE 1 = 1
                    AND `count` >= 3 
                    AND DATE_SUB(NOW(), INTERVAL 15 DAY) < update_time
        """
        data = self.select_all(sql)
        return [PickBlackListDao(i) for i in data]

    def select_driver_truck(self, driver_id_list):
        """
        查询司机车辆关联表
        :return:
        """
        sql = """
            SELECT
            driver_id,
            vehicle_no
            FROM
            db_cdm.dim_driver_vehicle
            WHERE 1 = 1
            AND driver_id in ({}) and vehicle_no is not null
        """
        commodity_values = "'"
        commodity_values += "','".join([i for i in driver_id_list])
        commodity_values += "'"
        sql = sql.format(commodity_values)
        data = self.select_all(sql)
        # 结果字典：driver_id：[vehicle_no1,vehicle_no2,...]
        result_dict = defaultdict(list)
        for item in data:
            result_dict[item['driver_id']].append(item['vehicle_no'])
        return result_dict

    def select_lat_and_lon_by_vehicle_no(self, vehicle_no_list):
        """
        根据车牌查询车辆
        :param vehicle_no_list:
        :return:
        """
        sql = """
            SELECT
                truck_no,
                lat,
                lon 
            FROM
                db_ads.`hhy_truck_now_location_zjxl` 
            WHERE
                truck_no IN ( {} ) 
            GROUP BY
                truck_no
        """
        vehicle_no_values = "'"
        vehicle_no_values += "','".join([i for i in vehicle_no_list])
        vehicle_no_values += "'"
        sql = sql.format(vehicle_no_values)
        data = self.select_all(sql)
        # 结果字典：truck_no：[lat,lon]
        result_dict = defaultdict(list)
        for item in data:
            result_dict[item['truck_no']].append(item['lat'])
            result_dict[item['truck_no']].append(item['lon'])
        return result_dict

    # def select_truck_zjxl_gps(self, driver_id_list):
    #     """
    #     查询中交兴路车辆位置信息
    #     :return:
    #     """
    #     sql = """
    #         SELECT
    #         tdv.driver_id,
    #         tdv.vehicle_no,
    #         tpz.lon longitude,
    #         tpz.lat latitude,
    #         tpz.insert_time gps_create_date
    #         -- tpz.vno,
    #         -- tpz.city,
    #         -- tpz.province
    #
    #         FROM
    #         db_ods.db_sys_t_driver_vehicle tdv
    #         LEFT JOIN db_ods.rg_travel_path_zjxl tpz ON tdv.vehicle_no = tpz.vno
    #         WHERE 1 = 1
    #         AND tpz.province = "山东省"
    #         AND tdv.driver_id in ({})
    #         AND tpz.insert_time > DATE_SUB( NOW( ), INTERVAL 20 MINUTE )
    #         GROUP BY
    #         tdv.vehicle_no,
    #         tpz.lon,
    #         tpz.lat
    #     """
    #     commodity_values = "'"
    #     commodity_values += "','".join([i for i in driver_id_list])
    #     commodity_values += "'"
    #     sql = sql.format(commodity_values)
    #     data = self.select_all(sql)
    #     return [PickPropellingDriver(i) for i in data]

    def select_driver_weight(self):
        """
        查询司机已接单重量
        :return:
        """
        sql = """
            SELECT 
            driver_id,
            plan_weight
            FROM
            db_ads.zd_plan_deduct_driver
            GROUP BY driver_id
        """
        data = self.select_all(sql)
        # 结果字典：{driver_id：plan_weight}
        result_dict = {}
        for item in data:
            result_dict[item['driver_id']] = float(item['plan_weight'])
        return result_dict


pick_propelling_dao = PickPropellingDao()
