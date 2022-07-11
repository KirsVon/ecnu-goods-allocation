# -*- coding: utf-8 -*-
# Description: 
# Created: shaoluyu 2020/9/29 9:14
from collections import defaultdict

from app.util.base.base_dao import BaseDao
from app.util.round_util import round_util
from model_config import ModelConfig


class PickStockDao(BaseDao):
    """
    摘单数据访问层
    """

    def select_pick_stock(self):
        """
        查询库存
        :return:
        """
        sql = """
            SELECT
                NOTICENUM as notice_num,
                PURCHUNIT as consumer,
                ORITEMNUM as oritem_num, 
                DEVPERIOD as devperiod, 
                SUBSTRING_INDEX(DELIWAREHOUSE,'-',1) as deliware_house,
                DELIWAREHOUSE as deliware_house_name,
                COMMODITYNAME as commodity_name,
                BIG_COMMODITYNAME as big_commodity_name,
                PACK as pack,  
                MATERIAL as mark, 
                STANDARD as specs, 
                DELIWARE as deliware, 
                CONTRACT_NO as contract_no,
                PORTNUM, 
                DETAILADDRESS as detail_address, 
                PROVINCE as province, 
                CITY as city, 
                WAINTFORDELNUMBER as waint_fordel_number, 
                WAINTFORDELWEIGHT as waint_fordel_weight, 
                CANSENDNUMBER as can_send_number, 
                CANSENDWEIGHT as can_send_weight, 
                DLV_SPOT_NAME_END as dlv_spot_name_end, 
                PACK_NUMBER as pack_number, 
                NEED_LADING_NUM as need_lading_num, 
                NEED_LADING_WT as need_lading_wt, 
                OVER_FLOW_WT as over_flow_wt, 
                LATEST_ORDER_TIME as latest_order_time, 
                PORT_NAME_END as port_name_end,
                priority,
                concat(longitude, latitude) as standard_address
            FROM
                db_ads.kc_rg_product_can_be_send_amount
            WHERE 
                CITY in ('滨州市','淄博市','济南市','菏泽市')
                and (CANSENDNUMBER > 0 OR NEED_LADING_NUM > 0) 
                and LATEST_ORDER_TIME is not null 
            """
        # # 品种条件
        # if truck.big_commodity_name:
        #     commodity_sql_condition = " and BIG_COMMODITYNAME in ({})"
        #     commodity_group = ModelConfig.RG_COMMODITY_GROUP_FOR_SQL.get(truck.big_commodity_name, ['未知品种'])
        #     commodity_values = "'"
        #     commodity_values += "','".join([i for i in commodity_group])
        #     commodity_values += "'"
        #     commodity_sql_condition = commodity_sql_condition.format(commodity_values)
        #     sql = sql + commodity_sql_condition
        data = self.select_all(sql)
        return data

    def select_pick_deduct_stock(self):
        """
        查询需要扣除的库存数据
        :return:
        """
        sql = """
                SELECT
                    a.trains_no,
                    ld.notice_num,
                    ld.oritem_num,
                    ld.outstock_name as deliware_house_name,
                    b.prodname as big_commodity_name,
                    ld.count as actual_number,
                    ld.weight as actual_weight,
                    c.city_name AS city,
                    c.district_name AS district,
                    a.open_order_time,
                    -- 	a.checkIn_time,
                    -- 	a.plan_no,
                    a.plan_status,
                    -- 	a.create_date,
                    -- 	b.plan_weight,
                    b.plan_quantity
                FROM
                    (
                        SELECT
                            checkIn_time,
                            open_order_time,
                            plan_no,
                            trains_no,
                            plan_source,
                            plan_status,
                            remark,
                            carrier_company_name,
                            create_id,
                            create_date 
                        FROM
                            db_ods.db_trans_t_plan 
                        WHERE
                            business_moduleId = '020' 
                            AND plan_source IN ( 'DDLY40', 'DDLY50' ) 
                            AND carrier_company_name = '会好运单车' 
                            AND 
                            (
                                plan_status >= 'DDZT55'
                                AND open_order_time BETWEEN date_sub( now( ), INTERVAL 1 DAY ) AND NOW( )
                                -- 		date( create_date ) = date( now( ) ) 
                                -- 		create_date LIKE '2021-01-26%'
                                OR plan_status IN ( 'DDZT20', 'DDZT50' )	
                                AND create_date BETWEEN date_sub( now( ), INTERVAL 3 DAY ) AND NOW( )
                            )
                    ) a
                    LEFT JOIN 
                    ( 
                        SELECT 
                            schedule_no, 
                            notice_num, 
                            oritem_num, 
                            outstock_name,
                            weight,
                            count
                        FROM 
                            db_ods.db_inter_lms_bclp_loading_detail 
                        WHERE 
                            create_date BETWEEN date_sub( now( ), INTERVAL 1 DAY ) AND NOW( )
                            -- 	  date( create_date ) = date( now( ) ) 
                            -- 		create_date LIKE '2021-01-26%'
                    ) ld ON ld.schedule_no RLIKE a.plan_no,
                    (
                        SELECT
                            end_point,
                            order_no,
                            plan_weight,
                            plan_quantity,
                            plan_no,
                            prodname 
                        FROM
                            db_ods.db_trans_t_plan_item 
                        WHERE
                            create_date BETWEEN date_sub( now( ), INTERVAL 3 DAY ) AND NOW( )
                            -- 		date( create_date ) = date( now( ) ) 
                            -- 		create_date LIKE '2021-01-26%'
                    ) b,
                    db_ods.db_sys_t_point c 
                WHERE
                    a.plan_no = b.plan_no 
                    AND b.end_point = c.location_id 
                    AND c.city_name IN (
                                        SELECT 
                                            city_name 
                                        FROM 
                                            db_ods.`db_tender_t_pickup_line`
                                        WHERE 
                                            company_id='C000062070'
                                            AND`status` = 'LXZT10'
                                        )
                ORDER BY
                    trains_no DESC
                    -- 	city,
                    -- 	district,
                    -- 	plan_status,
                    -- 	a.create_date
        """
        # 可能存在摘单过了1-2天才来拉货开单的情况，所以上面查询了3天之内的数据
        data = self.select_all(sql)
        return data

    def select_send_weight_all_city(self):
        """
        查询各城市当天有效的派单、摘单重量
        :return:
        """
        # 注：这里必须要关联b表，虽然a中也有end_point，但是a中的end_point可能为空
        sql = """
                SELECT
                    c.city_name,
                    a.plan_source,
                    SUM( a.plan_weight ) AS total_weight 
                FROM
                    db_ods.db_trans_t_plan a
                    INNER JOIN db_ods.db_trans_t_plan_item b ON a.plan_no = b.plan_no
                    LEFT JOIN db_ods.db_sys_t_point c ON b.end_point = c.location_id 
                WHERE
                    a.business_moduleId = '020' 
                    AND a.carrier_company_id = 'C000062070' 
                    AND a.plan_status NOT IN ( 'DDZT42', 'DDZT45' ) 
                    AND date( a.create_date ) = date( NOW( ) ) 
                    AND c.city_name IN 
                                        (
                                            SELECT 
                                                city_name 
                                            FROM 
                                                db_ods.`db_tender_t_pickup_line`
                                            WHERE 
                                                company_id='C000062070'
                                                AND`status` = 'LXZT10'
                                        )
                GROUP BY 
                    c.city_name,
                    a.plan_source
                ORDER BY 
                    c.city_name
        """
        data = self.select_all(sql)
        # # data为None的情况
        # if not data:
        #     return None
        data_dict = {}
        if data:
            for item in data:
                data_dict[item['city_name'] + ',' + item['plan_source']] = item['total_weight']
        # 查询各城市当天有效的派单、摘单重量：字典：{城市：[派单重量,摘单和派单的总重量]}（单位：吨）
        send_weight_dict = defaultdict(list)
        for city in ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT.keys():
            # 该城市派单的总重量
            dispatch_weight = float(data_dict.get(city + ',' + 'DDLY40', 0))
            send_weight_dict[city].append(dispatch_weight)
            # 该城市摘单的总重量
            pick_weight = float(data_dict.get(city + ',' + 'DDLY50', 0))
            # 摘单和派单的总重量
            send_weight_dict[city].append(pick_weight + dispatch_weight)
        return send_weight_dict


pick_stock_dao = PickStockDao()

if __name__ == '__main__':
    pick_stock_dao.select_send_weight_all_city()
