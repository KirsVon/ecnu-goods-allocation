# -*- coding: utf-8 -*-
# Description:
# Created: luchengkai 2021/03/25 14:43
from app.util.base.base_dao import BaseDao


class PickPropellingLogDao(BaseDao):

    def save_pick_log(self, values):
        """
        保存摘单计划推送的记录
        :param values:
        :return:
        """
        sql = """
            INSERT INTO 
                t_propelling_log(
                    pickup_no,
                    prod_name,
                    start_point,
                    end_point,
                    city_name,
                    district_name,
                    total_truck_num,
                    remain_truck_num,

                    driver_id,
                    driver_phone,  
                    driver_district,
                    label_type,
                    create_date,
                    driver_type,
                    location_flag,

                    app_latitude,
                    app_longitude,
                    app_dist,
                    truck_latitude,
                    truck_longitude,
                    truck_dist,
                    company_id,
                    business_module_id,
                    is_assign,
                    response_probability
                )
            VALUES( 
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            """
        self.executemany(sql, values)

    def save_msg_log(self, values):
        """
        保存摘单计划短信推送的记录
        :param values:
        :return:
        """
        sql = """
            INSERT INTO 
                t_msg_log(
                    pickup_no,
                    driver_id,
                    company_id,
                    business_module_id,
                    create_date
                )
            VALUES( 
                %s, %s, %s, %s, %s
            )
            """
        self.executemany(sql, values)

    def save_batch_wt_log(self, values):
        """
        保存摘单计划短信推送的记录
        :param values:
        :return:
        """
        sql = """
            INSERT INTO 
                t_batch_wt_log(
                    spec_desc,
                    spec_desc_name,
                    warehouse_out_no,
                    city_code,

                    order_no,
                    pick_no,

                    wait_compare_total_sheet,
                    current_stock_total_sheet,
                    have_push_total_sheet,
                    ready_push_total_sheet,
                    create_date
                )
            VALUES( 
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s
            )
            """
        self.executemany(sql, values)

    def save_send_email_log(self, values):
        """
        保存摘单计划短信推送的记录
        :param values:
        :return:
        """
        sql = """
            INSERT INTO 
                t_send_email_log(
                    plan_no,
                    vehicle_no,
                    driver_id,
                    driver_name,
                    driver_phone,
                    in_factory_time,
                    stay_time,
                    create_date
                )
            VALUES( 
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
            """
        self.executemany(sql, values)


pick_propelling_log_dao = PickPropellingLogDao()
