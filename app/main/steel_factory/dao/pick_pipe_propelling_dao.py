# -*- coding: utf-8 -*-
# Description:
# Created: luchengkai 2021/03/26 14:43

from app.main.steel_factory.entity.pick_propelling import PickPropelling
from app.main.steel_factory.entity.pick_propelling_driver import PickPropellingDriver
from app.util.base.base_dao import BaseDao
from app.util.base.base_dao_2 import BaseDao2


class PickPipePropellingDao(BaseDao):

    def select_wait_pick_list(self):
        """
        查询当日摘单计划列表
        :return:
        """
        sql = """
        SELECT
            tmp.pickup_no,
            tmp.prod_name,
            tmp.start_point,
            tmp.end_point,
            tmp.city_name,
            tmp.district_name,
            tmp.total_truck_num total_truck_num,
            tmp.remain_truck_num remain_truck_num,
            tmp.total_weight,
            tmp.remain_total_weight,
            tmp.driver_type,
            tmp.pickup_start_time,
            tmp.create_date
        FROM
            (
        SELECT
            distinct pickup_no,
            start_point,
            end_point,
            city_name,
            district_name,
            total_truck_num,
            remain_truck_num,
            total_weight,
            remain_total_weight,
            prod_name,
            driver_type,
            pickup_start_time,
            create_date
        FROM
            db_ads.zd_pickup_order_driver 
        WHERE 
            pickup_status IN ('PUST20', 'PUST30') 
            AND driver_type IN ('SJLY10','SJLY20')
            ) tmp 
        WHERE
            pickup_start_time < SUBDATE( NOW( ), INTERVAL 5 MINUTE ) 
        GROUP BY
            tmp.pickup_no,
            tmp.start_point,
            tmp.end_point,
            tmp.prod_name
        
        """
        data = self.select_all(sql)
        return [PickPropelling(i) for i in data]

    def select_wait_driver_list(self):
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
        WHERE
            pickup_status IN ('PUST20', 'PUST30') 
            AND driver_type IN ('SJLY10','SJLY20')
            AND pickup_start_time < SUBDATE( NOW( ), INTERVAL 5 MINUTE )
        """
        data = self.select_all(sql)
        return [PickPropellingDriver(i) for i in data]

    def get_assign_drivers(self, consignee_company_id):
        """
        查询客户指定司机池
        :return:
        """
        sql = """
        SELECT
        pdpd.driver_id,
        pdpd.driver_name,
        pdpd.driver_mobile driver_phone,
        pdpd.vehicle_no
        FROM
        db_ods.db_tender_t_pickup_driver_pool pdp
        LEFT JOIN db_ods.db_tender_t_pickup_driver_pool_driver pdpd ON pdp.driver_pool_id = pdpd.driver_pool_id
        LEFT JOIN db_ods.db_tender_t_pickup_driver_pool_customer pdpc ON pdp.driver_pool_id = pdpc.driver_pool_id
        WHERE 1 = 1
        AND pdpc.customer_id = '{}'
        AND pdpd.`status` = '10'
        AND pdp.`status` = '10'
        AND IFNULL(pdpd.driver_id, '') != ''
        AND IFNULL(pdpd.driver_name, '') != ''
        AND IFNULL(pdpd.driver_mobile, '') != ''
        """
        sql = sql.format(consignee_company_id)
        data = self.select_all(sql)
        return [PickPropellingDriver(i) for i in data]

    def select_no_work_in_time_driver_id(self):
        """
        获取刚结束任务一小时内的司机id
        :return:
        """
        sql = """
        SELECT
         p.plan_no ,
         pd.vehicle_no ,
         pd.driver_id ,
         p.carrier_company_id,
         pd.plan_weight,
         p.plan_status ,
         p.business_moduleid,
         p.create_date,
         p.update_date,
         p.out_factory_time
        FROM
         db_ods.db_trans_t_plan p
        INNER JOIN db_ods.db_trans_t_plan_driver pd ON
         p.plan_no = pd.plan_no
        WHERE 1 = 1
         AND business_moduleId = '001'
         AND p.plan_status > 'DDZT80'
         AND IFNULL(pd.driver_id, '') != ''
         AND IFNULL(p.out_factory_time, '') != ''
         AND p.out_factory_time >= date_sub(now() , INTERVAL 1 HOUR)
         GROUP BY pd.driver_id
        """
        data = self.select_all(sql)
        return [item['driver_id'] for item in data]

    def have_work_drivers(self):
        """
        查询有任务的司机
        """
        sql = """
        SELECT
         pd.driver_id
        FROM
         db_ods.db_trans_t_plan p
        INNER JOIN db_ods.db_trans_t_plan_driver pd ON
         p.plan_no = pd.plan_no
        WHERE 1 = 1
         AND p.business_moduleId = '001'
         AND p.plan_status NOT IN ('DDZT10','DDZT30','DDZT40','DDZT41','DDZT35','DDZT42','DDZT45','DDZT83','DDZT85','DDZT88','DDZT80')
         AND IFNULL(pd.driver_id, '') != ''
         AND p.create_date > DATE_SUB(NOW(), INTERVAL 2 DAY)
--          AND IFNULL(p.out_factory_time, '') != ''
--          AND p.out_factory_time >= date_sub(now() , INTERVAL 1 HOUR)
         GROUP BY pd.driver_id
-- 				 ORDER BY 8 DESC
        """
        data = self.select_all(sql)
        return [item['driver_id'] for item in data]


pick_pipe_propelling_dao = PickPipePropellingDao()

