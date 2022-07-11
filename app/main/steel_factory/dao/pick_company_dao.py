# -*- coding: utf-8 -*-
# Description: 根据公司名称查询公司id
# Created: jjunf 2021/3/23 14:28
from app.util.base.base_dao import BaseDao


class PickCompanyDao(BaseDao):
    """
    根据公司名称查询公司id
    """
    def select_company_id(self, consumer_name_list):
        """
        根据客户名称查询客户id
        :return:
        """
        sql = """
            SELECT
                company_id,
                company_name 
            FROM
                db_cdm.`dim_company_base` 
            WHERE
                company_type = 'GSBJ10'
                AND company_name IN ({})
        """
        # 对客户名称进行处理
        consumer_values = "'"
        consumer_values += "','".join(consumer_name_list)
        consumer_values += "'"
        sql = sql.format(consumer_values)
        data = self.select_all(sql)
        # 查询的客户id列表
        select_consumer_id_list = []
        # 查询的客户名称列表
        select_consumer_name_list = []
        if data:
            for item in data:
                select_consumer_id_list.append(item['company_id'])
                select_consumer_name_list.append(item['company_name'])
        result = ','.join(select_consumer_id_list)
        # 如果存在客户的名称没有查询到id的，则直接把客户名称拼接在后面
        if len(consumer_name_list) > len(select_consumer_name_list):
            for consumer in consumer_name_list:
                if consumer not in select_consumer_name_list:
                    if result:
                        result += ',' + consumer
                    # 如果result为空
                    else:
                        result += consumer
        return result


pick_company_dao = PickCompanyDao()


if __name__=='__main__':
    pick_company_dao.select_company_id(['11'])
