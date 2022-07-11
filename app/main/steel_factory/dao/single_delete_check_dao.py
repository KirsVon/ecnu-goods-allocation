# -*- coding: utf-8 -*-
# Description: 日钢西门推荐开单，删单子检测
# Created: jjunf 2021/6/11 15:27
from app.main.steel_factory.entity.order import Order
from app.util.base.base_dao import BaseDao


class SingleDeleteCheckDao(BaseDao):

    def select_recommend_and_open(self, lock_hour):
        """
        查询推荐开单的单子和实际开单的单子
        :return:
        """
        sql = """
            SELECT 
                lti.schedule_no,
                '推荐开单' style,
                lti.notice_num,
                lti.oritem_num,
                -- lti.outstock_code,
                SUBSTRING_INDEX(lti.outstock_code,'-',1) as outstock_code,
                lti.create_date
            FROM 
                db_model.t_load_task_item lti
            WHERE
                date_sub( NOW(), INTERVAL {} HOUR ) <= lti.create_date 
                AND lti.create_date < NOW()
                -- DATE(lti.create_date) = DATE(NOW())
                AND lti.company_id = 'C000000882'
                AND lti.schedule_no NOT RLIKE '测试' 
                AND lti.schedule_no NOT RLIKE 'test'
            UNION ALL
            SELECT
                schedule_no,
                '实际开单' style,
                notice_num,
                CONCAT_WS('-',LEFT(oritem_num,12),RIGHT(oritem_num,3)) as oritem_num,
                -- CONCAT_WS('-',outstock_code,outstock_name),
                outstock_code,
                create_date
            FROM 
                db_ods.db_inter_lms_bclp_loading_detail
            WHERE 
                schedule_no IN (
                    SELECT 
                        CONCAT_WS(';',p.company_id,p.plan_no) as schedule_no
                    FROM	
                        db_ods.`db_trans_t_plan` p
                    WHERE
                        p.billing_mode = 'KDFS20'
                        AND date_sub( NOW(), INTERVAL {} HOUR ) <= p.open_order_time 
                        AND p.open_order_time < NOW()
                        -- AND DATE(p.open_order_time) = DATE(NOW())
                        AND p.consignor_company_id = 'C000000882' 
                        AND p.business_moduleId = '020' 
                        AND p.plan_status not in ('DDZT42','DDZT45')
                )
            ORDER BY 
                schedule_no DESC,style DESC
        """
        data = self.select_all(sql.format(lock_hour, lock_hour))
        order_list = [Order(i) for i in data]
        return order_list


single_delete_check_dao = SingleDeleteCheckDao()
