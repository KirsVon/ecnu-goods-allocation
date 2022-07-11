# -*- coding: utf-8 -*-
# Description: 各城市车辆历史载重分析dao
# Created: jjunf 2021/5/8 15:51
import pandas as pd

from app.main.steel_factory.entity.city_truck_load_weight import CityTruckLoadWeight
from app.util.base.base_dao import BaseDao


class CityTruckLoadWeightDao(BaseDao):
    """
    各城市车辆历史载重分析dao
    """

    def select_history_waybill(self, company_id='C000000882', business_module_id='009', total_day=10):
        """
        查询历史运单
        :return:
        """
        sql = """
                SELECT
                    wb.company_id,
                    wb.business_type as business_module_id,
                    CONCAT_WS(';',wb.plan_company_id,wb.plan_no) AS schedule_no,
                    wb.travel_no as truck_no,
                    SUM( wb.pre_total_weight ) AS total_weight,
                    c.province_name as province,
                    c.city_name as city
                FROM
                    db_ods.db_trans_t_waybill wb,
                    db_ods.db_sys_t_point c 
                WHERE
                    wb.company_id = '{}'
                    AND wb.business_type = '{}'
                    AND wb.create_date BETWEEN DATE_SUB( NOW(), INTERVAL {} DAY ) AND NOW() 
                    AND wb.end_point = c.location_id 
                GROUP BY
                    wb.plan_no 
                ORDER BY
                    travel_no,
                    plan_no
        """
        data = self.select_all(sql.format(company_id, business_module_id, total_day))
        return pd.DataFrame(data)

    def select_loading_detail(self, total_day=10):
        """
        查询开单详情
        :return:
        """
        sql = """
                SELECT
                    ld.schedule_no,
                    ld.carmark as truck_no,
                    CAST(SUM(ld.weight) as DECIMAL(8,3)) as open_weight
                FROM
                    db_ods.db_inter_lms_bclp_loading_detail ld 
                WHERE
                    ld.create_date BETWEEN DATE_SUB( NOW(), INTERVAL {} DAY ) 
                    AND NOW() 
                    AND ld.commodity_name NOT IN ('水泥','矿渣粉','水渣')
                    AND ld.instock_code NOT IN ('F10','F20','F2') 
                    AND ld.carmark NOT RLIKE '日钢'
                GROUP BY
                    schedule_no
                ORDER BY
                    carmark,
                    schedule_no
        """
        data = self.select_all(sql.format(total_day))
        return pd.DataFrame(data)

    def select_city_truck_load_weight_reference(self, sql_condition_list):
        """
        查找数据表中已有的数据
        :param sql_condition_list:
        :return:
        """
        sql = """
                SELECT
                    company_id,
                    business_module_id,
                    province,
                    city,
                    truck_no,
                    reference_weight,
                    min_weight,
                    max_weight 
                FROM
                    db_model.`city_truck_load_weight_reference` 
                WHERE
                    CONCAT_WS(',',company_id,business_module_id,city,truck_no) IN ({})
        """
        # 查询条件
        values = "'"
        values += "','".join(sql_condition_list)
        values += "'"
        sql = sql.format(values)
        data = self.select_all(sql)
        exist_reference_list = [CityTruckLoadWeight(i) for i in data]
        return exist_reference_list

    def save_city_truck_load_weight_reference(self, delete_values, insert_values):
        """
        查找数据表中已有的数据
        :param insert_values:
        :param delete_values:
        :return:
        """
        sql_list = []
        # 删除操作
        delete_sql = """
                DELETE
                FROM
                    db_model.`city_truck_load_weight_reference` 
                WHERE
                    CONCAT_WS(',',company_id,business_module_id,city,truck_no) IN ({})
        """
        # 删除条件
        delete_values_condition = "'"
        delete_values_condition += "','".join(delete_values)
        delete_values_condition += "'"
        sql_list.append(delete_sql.format(delete_values_condition))
        # 插入操作
        insert_sql = """
                insert into 
                db_model.city_truck_load_weight_reference(
                                                            company_id,
                                                            business_module_id,
                                                            province,
                                                            city,
                                                            truck_no, 
                                                            
                                                            reference_weight,
                                                            min_weight,
                                                            max_weight,
                                                            create_date
                                                          )
                value( %s, %s, %s, %s, %s, 
                       %s, %s, %s, %s 
                      )
        """
        sql_list.append(insert_sql)
        self.execute_many_sql(sql_list, insert_values)

    def select_single_city_truck_load_weight_reference(self, company_id, business_module_id, city, truck_no):
        """
        查找数据表中已有的数据
        :param company_id:
        :param business_module_id:
        :param truck_no:
        :param city:
        :return:
        """
        sql = """
                SELECT
                    reference_weight
                FROM
                    db_model.`city_truck_load_weight_reference` 
                WHERE
                    company_id = '{}'
                    and business_module_id = '{}'
                    and city = '{}'
                    and truck_no = '{}'
        """
        sql = sql.format(company_id, business_module_id, city, truck_no)
        data = self.select_one(sql)
        if data:
            return int(float(data['reference_weight']) * 1000)
        return None


city_truck_load_weight_dao = CityTruckLoadWeightDao()

# 查询历史运单
"""
        SELECT
            wb.company_id,
            wb.business_type,
            CONCAT_WS(';',wb.plan_company_id,wb.plan_no) AS schedule_no,
            wb.travel_no as truck_no,
            SUM( wb.pre_total_weight ) AS total_weight,
            c.province_name as province,
            c.city_name as city
        FROM
            db_dw.`ods_db_trans_t_waybill` wb,
            db_dw.ods_db_sys_t_point c 
        WHERE
            wb.create_date BETWEEN DATE_SUB( NOW(), INTERVAL 10 DAY ) 
            AND NOW() 
            AND wb.company_id = 'C000000882'
            AND wb.business_type = '009' 
            AND wb.end_point = c.location_id 
        GROUP BY
            wb.plan_no  
        ORDER BY
            travel_no,
            plan_no
"""
# 查询开单详情
"""
        SELECT
            ld.schedule_no,
            ld.carmark as truck_no,
            CAST(SUM(ld.weight) as DECIMAL(8,3)) as total_weight
        FROM
            db_dw.ods_db_inter_lms_bclp_loading_detail ld 
        WHERE
            ld.create_date BETWEEN DATE_SUB( NOW(), INTERVAL 10 DAY ) 
            AND NOW() 
            AND ld.commodity_name NOT IN ('水泥','矿渣粉','水渣')
            AND ld.instock_code NOT IN ('F10','F20','F2') 
            AND ld.carmark NOT RLIKE '日钢'
        GROUP BY
            schedule_no
        ORDER BY
            carmark,
            schedule_no
"""
# 关联查询
"""
SELECT
    wb.company_id,
    wb.plan_company_id,
    wb.plan_no,
    wb.travel_no,
    wb.carrier_company_id,
    wb.end_point,
    wb.product_name,
    wb.pre_total_weight,
    wb.total_weight,
    wb.business_type,
    wb.group_driver_name,
    ld.schedule_no,
    ld.carmark,
    ld.commodity_name,
    ld.weight,
    ld.count,
    ld.outstock_code,
    ld.outstock_name,
    ld.instock_code,
    ld.instock_name,
    ld.trans_group_name,
    c.province_name,
    c.city_name,
    c.district_name 
FROM
    db_dw.`ods_db_trans_t_waybill` wb,
    db_dw.ods_db_inter_lms_bclp_loading_detail ld,
    db_dw.ods_db_sys_t_point c 
WHERE
    wb.create_date BETWEEN DATE_SUB( NOW(), INTERVAL 10 DAY ) 
    AND NOW() 
    AND wb.business_type = '009' 
    AND CONCAT_WS( ';', wb.plan_company_id, wb.plan_no ) = ld.schedule_no 
AND wb.end_point = c.location_id 
ORDER BY
    wb.travel_no,
    ld.schedule_no
"""
