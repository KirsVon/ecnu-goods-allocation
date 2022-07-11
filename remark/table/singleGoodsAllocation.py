# -*- coding: utf-8 -*-
# Description: 推荐开单项目
# Created: jjunf 2021/5/8 11:02


class TableRemark:
    """
    数据表说明
    """

    # 项目名称
    project_name = '推荐开单项目'
    # 项目接口
    interface_name = '/singleGoodsAllocation'
    # 对表的说明
    table_remark_dict = {
        'db_ads.kc_rg_product_can_be_send_amount': '可发库存表',
        'db_model.city_truck_load_weight_reference': '城市车辆推荐参考载重表',
        'db_model.attribute_simplify': '属性的简写对应表（对调度填写的备注进行匹配）',
        'db_ads.kc_rg_valid_loading_detail': '日钢有效的装车清单表',
        'db_cdm.dws_dis_warehouse_trucks': '各仓库车辆动态跟踪查询表',
        'db_model.model_config': '模型参数配置表，interface_name=singleGoodsAllocation',
        'db_model.t_load_task': '日志表：推荐装车明细主表，company_id=C000000882',
        'db_model.t_load_task_item': '日志表：推荐装车明细子表，company_id=C000000882',
        'db_ods.priority': '录入的优先发运表',
        'db_ods.plan': '录入的排产计划表'
    }


class TableSql:
    """
    数据表生成的sql语句
    """

    # 可发库存表
    kc_rg_product_can_be_send_amount = """
        SELECT
            id ,
            NOTICENUM,
            PURCHUNIT,
            ORITEMNUM,
            DEVPERIOD,
            DELIWAREHOUSE,
            COMMODITYNAME,
            t2.prod_kind_price_out as BIG_COMMODITYNAME,
            PACK,
            QUALITY,
            MATERIAL,
            STANDARD,
            DELIWARE,
            PORTNUM,
            DETAILADDRESS,
            t1.PROVINCE,
            t1.CITY,
            t1.CREATTIME,
            t1.ALTERTIME,
            t1.WAINTFORDELNUMBER,
            t1.WAINTFORDELWEIGHT,
            t1.CANSENDNUMBER,
            t1.CANSENDWEIGHT,
            t1.CONTRACT_NO,
            t1.DLV_SPOT_NAME_END,
            t1.PACK_NUMBER,
            t1.NEED_LADING_NUM,
            t1.NEED_LADING_WT,
            t1.OVER_FLOW_WT,
            t1.LOGISTICS_COMPANY_TYPE,
            t1.LATEST_ORDER_TIME,
            t1.PORT_NAME_END,
            t1.IF_OF_BOUND,
            t1.BILL_PLAN_WT,
            t1.ORDER_WT,
            t1.CONTRACT_NOT_DELI_WT ,
            t1.ods_update_time ,
            ifnull(ts.priority , ' ') priority ,
            (
                SELECT 
                    max(latitude) 
                from 
                    db_dw.ods_db_sys_t_point 
                where 
                    address = t1.DETAILADDRESS 
            ) latitude ,
            (
                SELECT 
                    max(longitude) 
                from 
                    db_dw.ods_db_sys_t_point 
                where 
                    address = t1.DETAILADDRESS 
            ) longitude
        FROM
            db_dw.ods_db_inter_bclp_can_be_send_amount t1
            INNER JOIN (
                            SELECT
                                prod_kind,
                                CASE
                                    WHEN locate('型钢', prod_kind_price_out)>0 THEN '型钢'
                                    when locate('螺纹', prod_kind_price_out)>0 then '螺纹'
                                ELSE prod_kind_price_out END as prod_kind_price_out
                            FROM
                                db_dw.ods_db_sys_t_prod_spections ps
                            WHERE
                                ps.company_id = 'C000000882'
                                AND is_use = 'SYBJ10'
                                and prod_kind_price_out is not null
                                AND prod_kind_price_out != ''
                            GROUP BY 
                                prod_kind 
                        ) t2 
            ON  t1.COMMODITYNAME = t2.prod_kind
                AND t1.`STATUS` != 'D'
                AND DELIWARE IN ( ' -', 'U123-连云港东泰码头(外库)', 'U124-连云港东联码头(外库)', 'U210-董家口库', 'U220-赣榆库', 'U288-岚北港口库2' )
                AND PURCHUNIT NOT IN ( '日照钢铁供应有限公司', '日照京华管业有限公司' )
                AND (t1.LOGISTICS_COMPANY_TYPE != '厂内自用' or t1.ORDER_TYPE_CODE != '领用订单')
                AND (t1.CANSENDNUMBER > 0 OR t1.NEED_LADING_NUM > 0)
            LEFT JOIN db_ods.db_dispatch_center_t_transport_stockinfo ts 
            ON  t1.ORITEMNUM = ts.order_number
                AND t1.NOTICENUM = ts .shipping_order
                AND t1.DELIWAREHOUSE = ts.outbound_warehouse
    """

    # 日钢有效的装车清单表
    kc_rg_valid_loading_detail = """
        SELECT
            CONCAT('lms',id) id,
            notice_num ,
            oritem_num ,
            concat( outstock_code , '-' , outstock_name ) outstock_name,
            weight ,
            count,
            schedule_no
        FROM
            db_dw.ods_db_inter_lms_bclp_loading_detail
        WHERE
            create_date >= (
                                SELECT
                                    IF(MAX(CREATTIME) > MAX(ALTERTIME), MAX(CREATTIME) , MAX(ALTERTIME)) max_time
                                FROM
                                    db_ads.kc_rg_product_can_be_send_amount
                            )
            AND commodity_name NOT IN ('水渣', '水泥', '矿渣粉')  
        UNION ALL 
        select
            concat('plan' , rowid ) id ,
            ''  notice_num ,
            '' oritem_num ,
            '' outstock_name,
            '' weight ,
            '' count,
            concat(company_id,';',plan_no) as schedule_no
        from
            db_ods.db_trans_t_plan
        where 
            business_moduleid = '020' 
            and plan_status ='DDZT50'
            and billing_mode <= 'KDFS20'
    """
    # 模型参数配置表
    model_config = """
        Create Table `model_config` (
         `id` bigint NOT NULL AUTO_INCREMENT COMMENT '关于此表的说明：https://docs.qq.com/doc/DRExZZ0VqZlNHT1Zi',
         `interface_name` varchar COMMENT '项目接口名称',
         `config_name` varchar COMMENT '模型配置参数名称',
         `str_1` varchar COMMENT '字符1',
         `str_2` varchar COMMENT '字符2',
         `str_3` varchar COMMENT '字符3',
         `str_4` varchar COMMENT '字符4',
         `int_1` int COMMENT '整型1',
         `int_2` int COMMENT '整型2',
         `int_3` int COMMENT '整型3',
         `int_4` int COMMENT '整型4',
         `decimal_1` decimal(8, 3) COMMENT '小数1',
         `decimal_2` decimal(8, 3) COMMENT '小数2',
         `decimal_3` decimal(8, 3) COMMENT '小数3',
         `decimal_4` decimal(8, 3) COMMENT '小数4',
         primary key (`id`)
        ) DISTRIBUTE BY HASH(`id`) INDEX_ALL='Y' COMMENT='摘单模型参数配置表';
        
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, `int_1`, 
        `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'B2', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'E1', NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'E2', NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'E3', NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'E4', NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'F1', NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'F10', NULL, NULL, NULL, 25, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'F2', NULL, NULL, NULL, 30, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'F20', NULL, NULL, NULL, 25, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'H1', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'P5', NULL, NULL, NULL, 25, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'P6', NULL, NULL, NULL, 25, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'P7', NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'P8', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'T1', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'X1', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'X2', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'Z1', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'Z2', NULL, NULL, NULL, 20, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'Z4', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'Z5', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'Z8', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'ZA', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
        INSERT INTO `model_config`(`interface_name`, `config_name`, `str_1`, `str_2`, `str_3`, `str_4`, 
        `int_1`, `int_2`, `int_3`, `int_4`, `decimal_1`, `decimal_2`, `decimal_3`, `decimal_4`) VALUES (
        'singleGoodsAllocation', 'WAREHOUSE_WAIT_DICT', 'ZC', NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL, NULL, 
        NULL, NULL); 
    """
    # 属性的简写对应表
    attribute_simplify = """
        Create Table `attribute_simplify` (
         `id` bigint NOT NULL AUTO_INCREMENT COMMENT '属性的简写对应表id',
         `company_id` varchar COMMENT '公司id',
         `business_module_id` varchar COMMENT '业务板块',
         `province` varchar COMMENT '省份',
         `city` varchar COMMENT '城市',
         `district` varchar COMMENT '区县',
         `attribute` varchar COMMENT '哪个属性',
         `short_attribute` varchar COMMENT '属性的简写',
         `detail_attribute` varchar COMMENT '属性的详细描述',
         `create_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
         primary key (`id`)
        ) DISTRIBUTE BY HASH(`id`) INDEX_ALL='Y';
    """
