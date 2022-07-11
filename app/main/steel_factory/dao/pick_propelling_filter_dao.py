# -*- coding: utf-8 -*-
# Description:
# Created: luchengkai 2021/01/06 14:43
from collections import defaultdict

from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.main.steel_factory.entity.pick_propelling_driver import PickPropellingDriver
from app.util.base.base_dao import BaseDao
from app.util.base.base_dao_2 import BaseDao2


class PickPropellingFilterDao(BaseDao):

    def select_active_driver(self):
        """
        查询活跃司机
        :return:
        """
        sql = """
        SELECT
        driver_id,
        driver_name,
        driver_phone,
        city_name,
        district_name,
        waybill_count	
        FROM
        db_cdm.dim_active_driver
        WHERE 1 = 1
        AND IFNULL(district_name, "") != ""
        ORDER BY
        waybill_count DESC
        """
        data = self.select_all(sql)
        return [PickPropellingDriver(i) for i in data]

    def select_pick_truck_count(self, pickup_no):
        """
        根据pickup_no查询摘单计划
        :return:
        """
        sql = """
        SELECT
            tmp.pickup_no,
            tmp.start_point,
            tmp.city_name,
            tmp.district_name,
            tmp.consignee_company_id,
            tmp.consignee_company_ids,
            tmp.end_point,
            tmp.total_truck_num total_truck_num,
            tmp.remain_truck_num remain_truck_num,
            tmp.total_weight,
            tmp.remain_total_weight,
            tmp.driver_type,
            tmp.pickup_start_time,
            tmp.pickup_status,
            tmp.prod_name,
            tmp.company_id,
            tmp.price_flag is_assign_drivers,
            tmp.business_module_id
        FROM
            (
        SELECT
            DISTINCT pickup_no,
            start_point,
            end_point,
            city_name,
            district_name,
            consignee_company_id,
            consignee_company_ids,
            total_truck_num,
            remain_truck_num,
            total_weight,
            remain_total_weight,
            driver_type,
            prod_name,
            pickup_start_time,
            pickup_status,
            company_id,
            price_flag,
            business_module_id
        FROM
            db_ads.zd_pickup_order_driver 
            ) tmp
        WHERE tmp.pickup_status IN ('PUST00', 'PUST10') 
        AND pickup_no = '{}'
        GROUP BY
            tmp.pickup_no,
            tmp.start_point,
            tmp.end_point,
            tmp.prod_name
        """
        data = self.select_all(sql.format(pickup_no))
        return [PickPropelling(i) for i in data]

    def select_driver_location(self, driver_values):
        """
        查询司机当前位置信息
        :return:
        """
        sql = """
        SELECT
        t1.driver_id,
        t1.latitude,
        t1.longitude
        FROM
        db_ads.`zd_hhy_driver_location` t1
        JOIN ( 
        SELECT 
        driver_id, 
        max( receive_date ) AS receive_date 
        FROM db_ads.zd_hhy_driver_location 
        GROUP BY driver_id 
        ) t2 ON t1.driver_id = t2.driver_id 
        AND t1.receive_date = t2.receive_date 
        WHERE t1.driver_id in ({})
        """
        values = "'"
        values += "','".join([i for i in driver_values])
        values += "'"
        sql = sql.format(values)
        data = self.select_all(sql)
        # 结果字典：truck_no：[lat,lon]
        result_dict = defaultdict(list)
        for item in data:
            if item['driver_id'] not in result_dict.keys():
                result_dict[item['driver_id']].append(item['latitude'])
                result_dict[item['driver_id']].append(item['longitude'])
        return result_dict

    # def select_have_work_driver(self):
    #     """
    #     查询有任务的司机
    #     :return:
    #     """
    #     sql = """
    #     SELECT
    #     driver_id
    #     FROM
    #     db_ads.zd_plan_deduct_driver
    #     GROUP BY driver_id
    #     """
    #     data = self.select_all(sql)
    #     return [i.get("driver_id", "U000000000") for i in data]

    def select_driver_kind(self):
        """
        查询司机六个月内的曾运品种
        :return:
        """
        sql = """
        SELECT 
        wd.driver_id,
        ps.prod_kind_price_out
        FROM
        db_ods.db_trans_t_waybill w
        LEFT JOIN db_ods.db_trans_t_waybill_driver wd ON w.waybill_no = wd.waybill_no
        LEFT JOIN db_ods.db_sys_t_prod_spections ps ON ps.prod_kind = w.product_name
        WHERE 1 = 1
        AND wd.driver_id IS NOT NULL
        AND w.business_type = "009"
        AND ps.company_id = 'C000000882' 
        AND ps.length_start = 0 
        AND ps.length_end = 0 
        AND ps.is_use = 'SYBJ10'
        AND w.create_date > DATE_SUB(NOW(), INTERVAL 12 MONTH)
        GROUP BY wd.driver_id, ps.prod_kind_price_out
        """
        data = self.select_all(sql)
        # 结果字典：driver_id：[kind1, kind2]
        result_dict = defaultdict(list)
        for item in data:
            result_dict[item['driver_id']].append(item['prod_kind_price_out'])
        return result_dict


pick_propelling_filter_dao = PickPropellingFilterDao()
