# -*- coding: utf-8 -*-
# Description: 已开装车清单数据
# Created: shaoluyu 2020/06/16
from app.util.base.base_dao import BaseDao


class LoadingDetailDao(BaseDao):
    def select_loading_detail(self, truck):
        """
        查询人工已开单信息、预开单信息、模型推荐未确认信息
        :return:
        """

        sql = """
        SELECT
            schedule_no,
            notice_num,
            oritem_num,
            outstock_code AS outstock_name,
            weight,
            count 
        FROM
            db_ods.db_inter_lms_bclp_loading_detail 
        WHERE
            create_date >= ( SELECT DATE_SUB( DATE_FORMAT( MAX( CALCULATETIME ), '%Y-%m-%d %H:%i:%s' ), INTERVAL 20 MINUTE ) 
            FROM db_ads.kc_rg_product_can_be_send_amount ) 
            AND commodity_name NOT IN ( '水渣', '水泥', '矿渣粉' ) UNION ALL
        SELECT
            schedule_no,
            notice_num,
            oritem_num,
            SUBSTRING_INDEX( outstock_code, '-', 1 ) AS outstock_name,
            weight,
            `count` 
        FROM
            db_model.t_load_task_item 
        WHERE
            IFNULL( schedule_no, '' ) != '' 
            AND schedule_no IN (
        SELECT DISTINCT
            concat( company_id, ';', plan_no ) AS schedule_no 
        FROM
            db_ods.db_trans_t_plan 
        WHERE
            ( business_moduleid = '020' AND plan_status IN ( 'DDZT50', 'DDZT20' ) AND billing_mode <= 'KDFS20' ) 
            OR (
            business_moduleid = '020' 
            AND plan_status = 'DDZT55' 
            AND concat( company_id, ';', plan_no ) NOT IN (
        SELECT
            schedule_no 
        FROM
            db_ods.db_inter_lms_bclp_loading_detail 
        WHERE
            create_date >= ( SELECT DATE_SUB( DATE_FORMAT( MAX( CALCULATETIME ), '%Y-%m-%d %H:%i:%s' ), INTERVAL 20 MINUTE ) 
            FROM db_ads.kc_rg_product_can_be_send_amount ) 
            AND commodity_name NOT IN ( '水渣', '水泥', '矿渣粉' ) 
            ) 
            AND billing_mode <= 'KDFS20' 
            ) 
            ) 
            AND schedule_no != '{}'
        """

        data = self.select_all(sql.format(truck.schedule_no))
        return data


# 解决lms_loading_detail同步延时超发问题sql
#         sql = """
# SELECT
# 	schedule_no,
# 	notice_num,
# 	oritem_num,
# 	outstock_code AS outstock_name,
# 	weight,
# 	count
# FROM
# 	db_ods.db_inter_lms_bclp_loading_detail
# WHERE
# 	create_date >= ( SELECT DATE_SUB( DATE_FORMAT( MAX( CALCULATETIME ), '%Y-%m-%d %H:%i:%s' ), INTERVAL 30 MINUTE ) FROM db_ads.kc_rg_product_can_be_send_amount )
# 	AND commodity_name NOT IN ( '水渣', '水泥', '矿渣粉' ) UNION ALL
# SELECT
# 	schedule_no,
# 	notice_num,
# 	oritem_num,
# 	SUBSTRING_INDEX( outstock_code, '-', 1 ) AS outstock_name,
# 	weight,
# 	`count`
# FROM
# 	db_model.t_load_task_item
# WHERE
# 	IFNULL( schedule_no, '' ) != ''
# 	AND schedule_no IN (
# 	SELECT DISTINCT
# 		concat( company_id, ';', plan_no ) AS schedule_no
# 	FROM
# 		db_ods.db_trans_t_plan
# 	WHERE
# 		( business_moduleid = '020' AND plan_status IN ( 'DDZT50', 'DDZT20' ) AND billing_mode <= 'KDFS20' )
# 		OR (
# 			business_moduleid = '020'
# 			AND plan_status = 'DDZT55'
# 			AND concat( company_id, ';', plan_no ) NOT IN (
# 			SELECT
# 				schedule_no
# 			FROM
# 				db_ods.db_inter_lms_bclp_loading_detail
# 			WHERE
# 				create_date >= ( SELECT DATE_SUB( DATE_FORMAT( MAX( CALCULATETIME ), '%Y-%m-%d %H:%i:%s' ), INTERVAL 30 MINUTE ) FROM db_ads.kc_rg_product_can_be_send_amount )
# 				AND commodity_name NOT IN ( '水渣', '水泥', '矿渣粉' )
# 			)
# 			AND billing_mode <= 'KDFS20'
# 		)
# 	)
# 	AND schedule_no != '{}'
#         """

loading_detail_dao = LoadingDetailDao()
