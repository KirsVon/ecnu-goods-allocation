# -*- coding: utf-8 -*-
# Description: 查询需要委托的订单
# Created: jjunf 2021/3/29 16:55
from app.main.pipe_factory.entity.order_wt import OrderWt
from app.util.base.base_dao import BaseDao
from app.util.base.base_dao_2 import BaseDao2


class OrderWtDao(BaseDao):

    def select_order_wt(self):
        """
        查询需要委托的订单
        :return:
        """
        sql = """
                SELECT
                    w.company_id,
                    w.business_moduleid as business_module_id,
                    w.start_point,
                    w.order_no,
                    w.pick_no,
                    w.consignor_company_id,
                    w.carrier_company_id,
                    w.consignee_company_id as consumer,
                    cb.company_name consumer_name,
                    w.total_weight,
                    w.business_nature,
                    w.STATUS,
                    w.remark,
                    w.r_vehicle,
                    w.recommend_mobie as recommend_mobile,
                    w.recommend_driver,
                    w.bind_no,
                    w.end_point,
                    w.province_name as province,
                    w.city_name as city,
                    w.district_name as district,
                    w.town_name as town,
                    w.update_date
                FROM
                    db_ads.`zd_cd_order_wt` w 
                LEFT JOIN db_ods.db_sys_t_company_base cb ON w.consignee_company_id = cb.company_id
                ORDER BY
                    province_name,
                    city_name,
                    district_name,
                    update_date
        """
        data = self.select_all(sql)
        order_wt_list = [OrderWt(order_wt) for order_wt in data]
        return order_wt_list

    def get_company_name(self, id_list):
        sql = """
        SELECT
        company_id,
        company_name
        FROM
        db_ods.db_sys_t_company_base
        WHERE 1 = 1
        AND company_id IN ({})
        """
        values = "'"
        values += "','".join([i for i in id_list])
        values += "'"
        sql = sql.format(values)
        data = self.select_all(sql)
        return {item['company_id']: item['company_name'] for item in data}


order_wt_dao = OrderWtDao()
