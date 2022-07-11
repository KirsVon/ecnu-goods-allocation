# -*- coding: utf-8 -*-
# Description: 查询指定司机的客户
# Created: jjunf 2021/3/31 18:37
from app.main.pipe_factory.entity.special_consumer import SpecialConsumer
from app.util.base.base_dao import BaseDao
from app.util.base.base_dao_2 import BaseDao2


class PickSpecialConsumer(BaseDao):
    """
    查询指定司机的客户dao
    """

    def select_special_consumer_list(self):
        """
        查询指定司机的客户
        :return:
        """
        sql = """
            SELECT
                pc.driver_pool_id,
                pc.customer_id as consumer_id,
                p.company_id,
                p.driver_pool_name,
                pd.driver_id,
                pd.driver_name,
                pd.driver_mobile,
                pd.vehicle_no,
                pd.reference_load 
            FROM
                db_ods.`db_tender_t_pickup_driver_pool_customer` pc
                LEFT JOIN db_ods.db_tender_t_pickup_driver_pool p ON pc.driver_pool_id = p.driver_pool_id
                LEFT JOIN ( 
                            SELECT 
                                driver_pool_id,
                                driver_id, 
                                driver_name, 
                                driver_mobile, 
                                vehicle_no, 
                                reference_load 
                            FROM 
                                db_ods.db_tender_t_pickup_driver_pool_driver 
                            WHERE 
                                `status` = '10' 
                        ) pd ON pc.driver_pool_id = pd.driver_pool_id 
            WHERE
                pc.`status` = '10' 
                AND p.`status` = '10' 
                AND p.company_id = 'C000000888'
            ORDER BY
                pc.driver_pool_id,
                pc.customer_id
        """
        data = self.select_all(sql)
        special_consumer_list = [SpecialConsumer(i) for i in data]
        return special_consumer_list


pick_special_consumer_dao = PickSpecialConsumer()


if __name__ == '__main__':
    a = pick_special_consumer_dao.select_special_consumer_list()
    print(a)
