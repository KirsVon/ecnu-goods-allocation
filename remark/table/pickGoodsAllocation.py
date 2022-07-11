# -*- coding: utf-8 -*-
# Description: 摘单分货项目数据表说明
# Created: jjunf 2021/01/12


class TableRemark:
    """
    数据表说明
    """

    # 项目名称
    project_name = '摘单分货项目'
    # 项目接口
    interface_name = '/pickGoodsAllocation'
    # 对表的说明
    table_remark_dict = {
        'db_ads.zd_plan_open_no': '摘单未开单调度单表，在最后返回摘单计划时需要扣除此表中的车次，只查询其中flag=I的数据',
        'db_model.t_pick_log': '摘单分货日志表',
        'db_model.t_pick_deduct_log': '摘单分货需要扣除的车次记录表',
        'db_ods.db_tender_t_pick_param_config': '摘单参数配置表',
        'db_model.t_pick_model_config': '摘单项目模型参数配置表，方便项目上线后，可以随时调节配置的参数，而不需要再次发布，'
                                        '相关说明：https://docs.qq.com/doc/DRExZZ0VqZlNHT1Zi',
        'db_cdm.dim_company_base': '公司基础信息纬度表，筛选company_type=GSBJ10的数据'
    }


class TableSql:
    """
    数据表生成的sql语句
    """

    # 摘单未开单调度单表
    zd_plan_open_no = """
        SELECT
            b.rowid,
            a.driver,
            a.plan_no,
            a.trains_no,
            a.plan_source,
            a.remark,
            b.prodname,
            b.plan_weight,
            b.plan_quantity,
            c.city_name,
            c.district_name,
            'I' flag 
        FROM
            (
                SELECT
                    t2.driver,
                    t2.plan_no,
                    t2.trains_no,
                    t2.plan_source,
                    t2.remark,
                    t2.end_point 
                FROM
                    (
                        SELECT DISTINCT
                            trains_no 
                        FROM
                            db_ods.db_trans_t_plan 
                        WHERE
                            business_moduleId = '020' 
                            AND carrier_company_id = 'C000062070' 
                            AND 
                            (
                                plan_status = 'DDZT20' 
                                AND create_date >= date_sub( now( ), INTERVAL 2 HOUR ) 
                                OR plan_status = 'DDZT50' 
                                OR plan_status >= 'DDZT55' 
                                AND open_order_time >= date_sub( now( ), INTERVAL 90 MINUTE ) 
                            ) 
                    ) t1
                    JOIN db_ods.db_trans_t_plan t2 ON t1.trains_no = t2.trains_no 
            ) a
            LEFT JOIN db_ods.db_trans_t_plan_item b ON a.plan_no = b.plan_no
            LEFT JOIN db_ods.db_sys_t_point c ON b.end_point = c.location_id 
        WHERE
            c.city_name IN ( 
                                SELECT 
                                    city_name 
                                FROM  
                                    db_ods.`db_tender_t_pickup_line` 
                                WHERE  
                                    company_id='C000062070' 
                                    AND`status` = 'LXZT10' 
                            )
    """

    # 摘单参数配置表
    t_pick_param_config = """
        Create Table `t_pick_param_config` (
        `id` bigint NOT NULL AUTO_INCREMENT,
        `commodity` varchar(255) COMMENT '品种名称',
        `match_commodity` varchar(255) COMMENT '关联品种名称',
        `unload_province` varchar(255) COMMENT '卸点省份',
        `unload_city` varchar(255) COMMENT '卸点城市',
        `unload_district` varchar(255) COMMENT '卸点区县',
        `match_unload_province` varchar(255) COMMENT '关联省份',
        `match_unload_city` varchar(255) COMMENT '关联城市',
        `match_unload_district` varchar(255) COMMENT '关联区县',
        `keep_goods_city` varchar(255) COMMENT '留货城市',
        `keep_goods_district` varchar(255) COMMENT '留货区县',
        `keep_goods_commodity` varchar(255) COMMENT '留货品种',
        `keep_goods_customer` varchar(255) COMMENT '留货客户',
        `weight_city` varchar(255) COMMENT '载重配置城市',
        `weight_commodity` varchar(255) COMMENT '载重配置品种',
        `weight_lower` decimal(20, 4) COMMENT '载重下限',
        `weight_upper` decimal(20, 4) COMMENT '载重上限',
        `type_flag` int COMMENT '配置类型：1品种搭配；2关联路线；3留货；4载重',
        `update_id` varchar COMMENT '更新人id',
        `update_time` datetime COMMENT '更新时间',
        primary key (`id`)
        ) DISTRIBUTE BY HASH(`id`) INDEX_ALL='Y' COMMENT='摘单参数配置表';
    """

    # 摘单参数配置表默认参数
    t_pick_param_config_default = """
        INSERT INTO `t_pick_param_config` (
            `commodity`,
            `match_commodity`,
            `unload_province`,
            `unload_city`,
            `unload_district`,
            `match_unload_province`,
            `match_unload_city`,
            `match_unload_district`,
            `keep_goods_city`,
            `keep_goods_district`,
            `keep_goods_commodity`,
            `keep_goods_customer`,
            `weight_city`,
            `weight_commodity`,
            `weight_lower`,
            `weight_upper`,
            `type_flag`,
            `update_id`,
            `update_time` 
        )
        VALUES
            ('老区-卷板', '新产品-卷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('老区-卷板', '新产品-白卷', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-冷板', '新产品-白卷', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-冷板', '新产品-卷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-冷板', '新产品-窄带', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-窄带', '新产品-白卷', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-窄带', '新产品-卷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-窄带', '新产品-冷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-白卷', '新产品-冷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-白卷', '新产品-窄带', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-白卷', '新产品-卷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-白卷', '老区-卷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-卷板', '老区-卷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-卷板', '新产品-冷板', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-卷板', '新产品-窄带', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            ('新产品-卷板', '新产品-白卷', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                                                    NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
            
            (NULL, NULL, '山东省', '济南市', '天桥区', '山东省', '济南市', '历城区', NULL, NULL, NULL, NULL, NULL, 
                                                                                    NULL, NULL, NULL, 2, NULL, NULL),
            (NULL, NULL, '山东省', '济南市', '天桥区', '山东省', '济南市', '槐荫区', NULL, NULL, NULL, NULL, NULL, 
                                                                                    NULL, NULL, NULL, 2, NULL, NULL),
            (NULL, NULL, '山东省', '济南市', '历城区', '山东省', '济南市', '槐荫区', NULL, NULL, NULL, NULL, NULL, 
                                                                                    NULL, NULL, NULL, 2, NULL, NULL),
            
            
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '滨州市', '全部', '新产品-窄带', NULL, NULL, NULL, 
                                                                                    NULL, NULL, 3, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '滨州市', '全部', '新产品-冷板', NULL, NULL, NULL, 
                                                                                    NULL, NULL, 3, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '滨州市', '博兴县', '老区-卷板', 
                '京创智汇(上海)物流科技有限公司', NULL, NULL, NULL, NULL, 3, NULL, NULL),
            
            
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '济南市', '全部', 31.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '济南市', '新产品-卷板', 29.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '济南市', '新产品-白卷', 29.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '济南市', '老区-卷板', 29.0000, 35.0000, 4, NULL, NULL),
            
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '菏泽市', '全部', 31.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '菏泽市', '新产品-卷板', 29.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '菏泽市', '新产品-白卷', 29.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '菏泽市', '老区-卷板', 29.0000, 35.0000, 4, NULL, NULL),
            
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '淄博市', '全部', 31.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '淄博市', '新产品-卷板', 29.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '淄博市', '新产品-白卷', 29.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '淄博市', '老区-卷板', 29.0000, 35.0000, 4, NULL, NULL),
            
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '滨州市', '全部', 31.0000, 35.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '滨州市', '新产品-卷板', 31.0000, 39.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '滨州市', '新产品-白卷', 31.0000, 39.0000, 4, NULL, NULL),
            (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                            '滨州市', '老区-卷板', 31.0000, 39.0000, 4, NULL, NULL)
    """
