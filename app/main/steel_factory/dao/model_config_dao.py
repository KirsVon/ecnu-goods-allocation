# -*- coding: utf-8 -*-
# Description: 
# Created: jjunf 2021/5/21 12:43
from app.main.steel_factory.entity.model_config import ModelConfig
from app.util.base.base_dao import BaseDao


class ModelConfigDao(BaseDao):
    """
    参数配置dao
    """

    def select_model_config(self, interface_name=None):
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
                db_model.model_config 
            WHERE
                interface_name = '{}'
            ORDER BY
                config_name
        """
        sql = sql.format(interface_name)
        data = self.select_all(sql)
        model_config_list = [ModelConfig(i) for i in data]
        return model_config_list

    def save_model_config(self, value_list, delete_condition_dict=None):
        """
        保存参数配置
        :param delete_condition_dict:属性及其值的键值对（'interface_name': 'singleGoodsAllocation', 'config_name': 'SINGLE_USE_OPTIMAL_CITY'）
        :param value_list:
        :return:
        """
        insert_sql = """
            INSERT INTO db_model.model_config (
                                                interface_name,
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
                                            )
            values(
                    %s, %s, 
                    %s, %s, %s, %s, 
                    %s, %s, %s, %s, 
                    %s, %s, %s, %s
                )
        """
        # 如果没有需要删除的条件
        if not delete_condition_dict:
            self.executemany(insert_sql, value_list)
        else:
            delete_sql = """
                DELETE 
                FROM 
                    db_model.model_config
                WHERE 
                    1=1
                    -- interface_name = 'singleGoodsAllocation' 
                    -- AND config_name = 'SINGLE_LOCK_ORDER'
            """
            if delete_condition_dict:
                for condition_key in delete_condition_dict.keys():
                    delete_sql += """AND {} = '{}' """.format(condition_key, delete_condition_dict[condition_key])
            self.execute_many_sql([delete_sql, insert_sql], value_list)


model_config_dao = ModelConfigDao()

if __name__ == '__main__':
    model_config_dao.save_model_config([],
                                       {'interface_name': 'singleGoodsAllocation',
                                        'config_name': 'SINGLE_LOCK_ORDER'})
