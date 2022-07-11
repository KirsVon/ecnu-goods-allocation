# -*- coding: utf-8 -*-
# Description: 从数据表中获取模型参数配置
# Created: jjunf 2021/3/22 10:41
from app.main.steel_factory.entity.pick_model_config import PickModelConfig
from app.util.base.base_dao import BaseDao


class PickModelConfigDao(BaseDao):
    """
    参数配置dao
    """

    def select_pick_model_config(self):
        """
        读取参数配置
        :return:
        """
        sql = """
            SELECT
                config_name,
                str_1,
                str_2,
                str_3,
                str_4,
                int_1,
                int_2,
                int_3,
                int_4,
                decimal_1,
                decimal_2,
                decimal_3,
                decimal_4
            FROM
                db_model.t_pick_model_config 
            ORDER BY
                config_name
        """
        data = self.select_all(sql)
        model_config_list = [PickModelConfig(i) for i in data]
        return model_config_list


pick_model_config_dao = PickModelConfigDao()
