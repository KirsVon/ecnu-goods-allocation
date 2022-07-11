# -*- coding: utf-8 -*-
# Description: 参数配置dao
# Created: jjunf 2021/01/15
from app.main.steel_factory.entity.pick_param import PickParam
from app.util.base.base_dao import BaseDao


class PickParamDao(BaseDao):
    """
    参数配置dao
    """

    def select_pick_param(self):
        """
        读取参数配置
        :return:
        """
        sql = """
            SELECT
                commodity,
                match_commodity,
                unload_province,
                unload_city,
                unload_district,
                match_unload_province,
                match_unload_city,
                match_unload_district,
                keep_goods_city,
                keep_goods_district,
                keep_goods_commodity,
                keep_goods_customer,
                weight_city,
                weight_commodity,
                weight_lower,
                weight_upper,
                type_flag 
            FROM
                db_ods.db_tender_t_pick_param_config 
            ORDER BY
                type_flag
        """
        data = self.select_all(sql)
        return [PickParam(i) for i in data]

    # def modify_param(self):
    #     """
    #     参数配置（增删改）
    #     :return:
    #     """
    #     pass
    #
    # def select_param(self, type_flag):
    #     """
    #     读取参数配置
    #     :return:
    #     """
    #     sql = """
    #         SELECT
    #             commodity,
    #             match_commodity,
    #             unload_province,
    #             unload_city,
    #             unload_district,
    #             match_unload_province,
    #             match_unload_city,
    #             match_unload_district,
    #             keep_goods_city,
    #             keep_goods_district,
    #             keep_goods_commodity,
    #             keep_goods_customer,
    #             weight_city,
    #             weight_commodity,
    #             weight_lower,
    #             weight_upper
    #         FROM
    #             t_pick_param_config
    #         WHERE
    #             type_flag = {}
    #     """
    #     data = self.select_all(sql.format(type_flag))
    #     return [PickParam(i) for i in data]


pick_param_dao = PickParamDao()
