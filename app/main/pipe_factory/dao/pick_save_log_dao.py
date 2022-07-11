# -*- coding: utf-8 -*-
# Description: 
# Created: jjunf 2021/3/31 11:15
from app.util.base.base_dao import BaseDao


class SavePickLog(BaseDao):

    def save_pick_log(self, values):
        """
        保存摘单分货的记录
        :param values:
        :return:
        """
        sql = """
                insert into 
                db_model.t_pick_log(
                                    pick_id,
                                    company_id,
                                    business_module_id,
                                    pick_total_weight,
                                    pick_truck_num,
                                    remark,
                                    
                                    load_task_id,
                                    load_task_type,  
                                    total_weight,
                                    weight,
                                    province,
                                    city, 
                                    end_point, 
                                    town,
                                    
                                    consumer,
                                    r_vehicle,
                                    recommend_driver,
                                    recommend_mobile,
                                    
                                    
                                    bind_no,
                                    notice_num, 
                                    oritem_num,
                                    priority,
                                    pool_id,
                                    create_date
                                  )
                value( %s, %s, %s, %s, %s, 
                       %s, %s, %s, %s, %s, 
                       %s, %s, %s, %s, %s, 
                       %s, %s, %s, %s, %s, 
                       %s, %s, %s, %s
                      )
                """
        self.executemany(sql, values)


save_pick_log = SavePickLog()
