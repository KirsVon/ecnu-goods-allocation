# -*- coding: utf-8 -*-
# Description: 可用库存表
# Created: shaoluyu 2020/06/16
from app.main.steel_factory.entity.truck import Truck
from app.util.base.base_dao import BaseDao
from model_config import ModelConfig


class StockDao(BaseDao):
    def select_stock(self, truck: Truck):
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
            PORTNUM as port_num, 
            DETAILADDRESS as detail_address, 
            PROVINCE as province, 
            CITY as city, 
            WAINTFORDELNUMBER as waint_fordel_number, 
            WAINTFORDELWEIGHT as waint_fordel_weight, 
            CANSENDNUMBER, 
            CANSENDWEIGHT, 
            DLV_SPOT_NAME_END as dlv_spot_name_end,
            FLOW_CONFIRM_PERSON as flow_confirm_person, 
            PACK_NUMBER, 
            CAST(NEED_LADING_NUM AS FLOAT) AS NEED_LADING_NUM,
            CAST(NEED_LADING_WT AS FLOAT) AS NEED_LADING_WT,
            CAST(OVER_FLOW_WT AS FLOAT) AS OVER_FLOW_WT,
            LATEST_ORDER_TIME as latest_order_time, 
            PORT_NAME_END as port_name_end,
            concat(longitude, latitude) as standard_address,
            PROD_LEVEL_CODE as prod_level_code
        FROM
            db_ads.kc_rg_product_can_be_send_amount
        WHERE 
            (CANSENDNUMBER > 0 OR NEED_LADING_NUM > 0) 
        """
        # 判断车是否拉港口货
        if truck.foreign_trade_deliware:
            deliware_sql_condition = " and DELIWARE RLIKE '{}' "
            deliware_sql_condition = deliware_sql_condition.format(truck.foreign_trade_deliware)
            sql = sql + deliware_sql_condition
        # 汽运
        else:
            city_sql_condition = " and CITY = '{}' "
            # 城市条件，不传默认为临沂市
            city_condition = truck.city if truck.city else ModelConfig.RG_DEFAULT_CITY
            city_sql_condition = city_sql_condition.format(city_condition)
            sql = sql + city_sql_condition
        # 品种条件
        if truck.big_commodity_name and truck.big_commodity_name != '全部':
            commodity_sql_condition = " and BIG_COMMODITYNAME in ({})"
            commodity_group = ModelConfig.RG_COMMODITY_GROUP_FOR_SQL.get(truck.big_commodity_name,
                                                                         [truck.big_commodity_name])
            commodity_values = "'"
            commodity_values += "','".join([i for i in commodity_group])
            commodity_values += "'"
            commodity_sql_condition = commodity_sql_condition.format(commodity_values)
            sql = sql + commodity_sql_condition
        data = self.select_all(sql)
        return data

    def select_attribute_simplify(self, company_id, business_module_id, province, city):
        """
        根据公司id、业务板块、省份、城市查询其相应属性的缩写
        :param company_id:
        :param business_module_id:
        :param province:
        :param city:
        :return:
        """
        sql = """
            SELECT
                attribute,
                short_attribute,
                detail_attribute 
            FROM
                db_model.attribute_simplify 
            WHERE
                company_id = '{}' 
                AND business_module_id = '{}' 
                AND province = '{}' 
                AND city = '{}'
        """
        sql = sql.format(company_id, business_module_id, province, city)
        data = self.select_all(sql)
        return data

    # def select_abnormal_deliware_house(self):
    #     sql = """
    #         SELECT
    #             abnormal_deliware_house_code
    #         FROM
    #             db_model. abnormal_deliware
    #
    #     """
    #     data = self.select_all(sql)
    #     return data


stock_dao = StockDao()
