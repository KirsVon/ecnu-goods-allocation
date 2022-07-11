# -*- coding: utf-8 -*-
# Description: 摘单时判断剩余车次数数据访问层
# Created: jjunf 2021/3/18 10:56
from app.main.steel_factory.entity.plan import Plan
from app.main.steel_factory.entity.remain_check import RemainCheck
from app.util.base.base_dao import BaseDao


class PickRemainCheckDao(BaseDao):

    def save_remain_check(self, remain_check: RemainCheck):
        """
        保存判断结果
        :param remain_check:
        :return:
        """
        sql = """
                insert into 
                    db_model.t_pick_remain_check_log(
                                                        driver_id,
                                                        pickup_no,
                                                        total_weight,
                                                        total_truck_num,
                                                        
                                                        remain_truck_num,
                                                        city,
                                                        district,
                                                        big_commodity_name,
                                                        
                                                        plan_quantity,
                                                        remark,
                                                        result
                                                    )
                value(  %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                """
        item_tuple = (remain_check.driver_id, remain_check.pickup_no, remain_check.total_weight,
                      remain_check.total_truck_num, remain_check.remain_truck_num, remain_check.city,
                      remain_check.district, remain_check.big_commodity_name, remain_check.plan_quantity,
                      remain_check.remark, str(remain_check.result))
        values = [item_tuple]
        self.executemany(sql, values)

    # def select_plan(self, city, district):
    #     """
    #     查询已调度的车次情况
    #     :return:
    #     """
    #     sql = """
    #             SELECT
    #                 c.city_name AS city,
    #                 c.district_name AS district,
    #                 b.prodname AS big_commodity_name,
    #                 b.plan_quantity,
    #                 a.trains_no
    #             FROM
    #                 db_ods.db_trans_t_plan a
    #                 INNER JOIN db_ods.db_trans_t_plan_item b ON a.plan_no = b.plan_no
    #                 LEFT JOIN db_ods.db_sys_t_point c ON b.end_point = c.location_id
    #             WHERE
    #                 a.business_moduleId = '020'
    #                 AND a.carrier_company_id = 'C000062070'
    #                 AND (
    #                     a.plan_status = 'DDZT20'
    #                     AND a.create_date >= date_sub( now( ), INTERVAL 24 HOUR )
    #                     OR a.plan_status = 'DDZT50'
    #                     OR a.plan_status >= 'DDZT55'
    #                     AND a.open_order_time >= date_sub( now( ), INTERVAL 90 MINUTE )
    #                 )
    #                 AND c.city_name = '{}'
    #                 AND c.district_name = '{}'
    #             ORDER BY
    #                 a.trains_no
    #         """
    #     sql = sql.format(city, district)
    #     data = self.select_all(sql)
    #     plan_list = [Plan(i) for i in data]
    #     return plan_list


pick_remain_check_dao = PickRemainCheckDao()

# if __name__=='__main__':
#     a = pick_remain_check_dao.select_plan('青岛市','胶州市')
#     print(a)
