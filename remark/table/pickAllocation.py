# -*- coding: utf-8 -*-
# Description: 摘单项目数据表说明
# Created: jjunf 2021/4/2 13:25


class TableRemark:
    """
    数据表说明
    """

    # 项目名称
    project_name = '摘单项目'
    # 项目接口
    interface_name = '/pickAllocation'
    # 对表的说明
    table_remark_dict = {
        'db_ads.zd_cd_order_wt': '成都管厂委托单',
        'db_model.t_pick_log': '日志表，company_id=C000000888，business_module_id=001',
        'db_model.cdpzjh_consumer_designated_drivers': '成都彭州京华 客户指定的司机表',
        'db_ods.db_tender_t_pickup_driver_pool_customer': '摘单司机池关联客户表',
        'db_ods.db_tender_t_pickup_driver_pool': '摘单司机池主表',
        'db_ods.db_tender_t_pickup_driver_pool_driver': '摘单司机池司机表'
    }


class TableSql:
    """
    数据表生成的sql语句
    """

    # 成都管厂委托单  intelligent_dispatch_status = 'IDS70' ：表示智能摘单状态为就绪中（人工添加的可以用来发布摘单的委托单）
    zd_cd_order_wt = """
        SELECT
            o.rowid,
            o.company_id,
            o.order_no,
            o.pick_no,
            o.consignor_company_id_root,
            o.consignor_company_id,
            o.carrier_company_id,
            o.consignee_company_id,
            o.total_price,
            o.total_weight,
            o.total_sheet,
            o.STATUS,
            o.remark,
            o.create_date,
            ifnull( o.update_date, o.create_date ) update_date,
            o.trans_weight,
            o.trans_sheet,
            o.business_nature,
            o.main_product_list_no,
            o.truck_task_id,
            o.r_vehicle,
            o.bind_no,
            per_weight,
            ca.end_point,
            tp.province_name,
            tp.city_name,
            tp.district_name,
            CASE
                WHEN tp.town_name <> '' THEN town_name 
            END town_name,
            o.recommend_mobie,
            o.recommend_driver,
            o.plan_arrival_time,
            o.business_moduleId,
            'P000003477' start_point 
        FROM
            db_ods.db_trans_t_order_wt o
            INNER JOIN db_ods.db_sys_t_common_address ca ON o.consignee_company_id = ca.customer_id 
            AND is_default = '10'
            INNER JOIN db_ods.db_sys_t_point tp ON ca.end_point = tp.location_id 
        WHERE
            o.company_id = 'C000000888' 
            AND o.STATUS = 'ETST10' 
            AND o.business_nature IN ( 'YWXZ10', 'YWXZ50' ) 
            AND o.business_moduleId = '001' 
            AND o.order_source = 'WTLY70' 
            --  and o.keeper_status = 'KP10'
            AND o.intelligent_dispatch_status = 'IDS70' 
            AND o.create_date >= date_sub( now( ), INTERVAL 7 DAY ) 
        ORDER BY
            1 DESC
    """

    # db_model.t_pick_log表添加字段pool_id(将多个客户绑定为一个客户时的id)、priority优先级
    add_column_to_t_pick_log = """
        ALTER TABLE db_model.`t_pick_log` 
        ADD COLUMN pool_id VARCHAR DEFAULT NULL COMMENT '池id';

        ALTER TABLE db_model.`t_pick_log` 
        ADD COLUMN priority VARCHAR DEFAULT NULL COMMENT '优先级：YXJ10最低，YXJ20普通，YXJ30加急';
        """
