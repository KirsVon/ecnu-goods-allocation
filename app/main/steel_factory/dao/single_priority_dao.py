# -*- coding: utf-8 -*-
# Description: 查询优先发运
# Created: jjunf 2021/5/8 11:29
from collections import defaultdict

from app.util.base.base_dao import BaseDao
from app.util.date_util import get_now_str


class PriorityDao(BaseDao):

    def select_priority(self):
        """
        查询优先发运
        :return:
        """
        sql = """
            SELECT
                notice_no as notice_num,
                order_no as oritem_num, 
                priority as priority_grade,
                priority_weight
            FROM
                db_ods.db_dispatch_center_t_shipping_priority
            WHERE 
                shipping_date RLIKE '{}'
                and company_id = 'C000000882'
                and status = '10'
                and (priority = '1' or priority = '2')
        """
        now_str = get_now_str()
        date = now_str.split(' ')[0]
        sql = sql.format(date)
        data = self.select_all(sql)
        # 优先级字典列表：键为发货通知单号+','+订单号；值为[优先等级(1或者2)，优先发运量]
        priority_dict = defaultdict(list)
        if data:
            for item in data:
                priority_dict[item['notice_num'] + ',' + item['oritem_num']].append(int(item['priority_grade']))
                priority_dict[item['notice_num'] + ',' + item['oritem_num']].append(int(item['priority_weight'] * 1000))
        return priority_dict


priority_dao = PriorityDao()
