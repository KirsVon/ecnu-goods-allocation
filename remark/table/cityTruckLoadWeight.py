# -*- coding: utf-8 -*-
# Description: 各城市车辆历史载重分析
# Created: jjunf 2021/5/10 17:15


class TableRemark:
    """
    各城市车辆历史载重分析
    """

    # 项目名称
    project_name = '各城市车辆历史载重分析'
    # 项目接口
    interface_name = '/cityTruckLoadWeight'
    # 对表的说明
    table_remark_dict = {
        'db_model.city_truck_load_weight_reference': '结果表',
        'db_dw.`ods_db_trans_t_waybill`': '运单表',
        'db_dw.ods_db_sys_t_point': '地点表',
        'db_dw.ods_db_inter_lms_bclp_loading_detail': 'lms开单明细表'
    }


class TableSql:
    """
    数据表生成的sql语句
    """

    # 结果表
    city_truck_load_weight_reference = """
        Create Table `city_truck_load_weight_reference` (
        `row_id` bigint NOT NULL AUTO_INCREMENT COMMENT '城市车辆推荐参考载重表 id',
        `company_id` varchar COMMENT '公司id',
        `business_module_id` varchar COMMENT '业务模块',
        `province` varchar COMMENT '省',
        `city` varchar COMMENT '市',
        `truck_no` varchar COMMENT '车牌',
        `reference_weight` decimal(8, 3) COMMENT '推荐参考载重',
        `min_weight` decimal(8, 3) COMMENT '最低开单重量',
        `max_weight` decimal(8, 3) COMMENT '最高开单重量',
        `create_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        primary key (`row_id`)
        ) DISTRIBUTE BY HASH(`row_id`) INDEX_ALL='Y' COMMENT='城市车辆推荐参考载重表';
    """