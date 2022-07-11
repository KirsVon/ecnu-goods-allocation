# -*- coding: utf-8 -*-
# Description: 车次明细表
# Created: shaoluyu 2020/06/16
from app.main.steel_factory.entity.load_task import LoadTask
from app.util.base.base_dao import BaseDao
from model_config import ModelConfig
from app.util.date_util import get_now_str


class LoadTaskItemDao(BaseDao):
    """
    LoadTaskItem相关数据库操作
    """

    def insert_load_task_item(self, values, load_task: LoadTask):
        """增
        Args:
        Returns:
        Raise:
        """
        sql_list = []
        # 重复报道时，清除历史记录
        delete_sql = """
                        delete 
                        from 
                            db_model.t_load_task_item 
                        where 
                            schedule_no = '{}'
                    """
        sql_list.append(delete_sql.format(load_task.schedule_no))
        # 1公司id 2报道号 3车次号 4优先级 5重量 6件数 7市 8终点 9港口批号 10大品名 11小品名 12发货通知单号
        # 13订单号 14收货用户 15规格 16材质 17出库仓库 18入库仓库 19收货地址 20最新挂单时间 21创建人id 22创建时间
        insert_sql = """
                        insert into db_model.t_load_task_item(
                                            company_id,
                                            schedule_no,
                                            load_task_id,
                                            priority,
                                            weight,
                                            `count`,
                                            city,
                                            end_point,
                                            port_num,
                                            big_commodity,
                                            commodity,
                                            notice_num,
                                            oritem_num,
                                            consumer,
                                            standard,
                                            sgsign,
                                            outstock_code,
                                            instock_code,
                                            receive_address,
                                            latest_order_time,
                                            create_id,
                                            `create_date`
                                    )
                        value(%s, %s, %s, %s, %s, 
                               %s, %s, %s, %s, %s, 
                               %s, %s, %s, %s, %s, 
                               %s, %s, %s, %s, %s,
                               %s,%s)
                    """
        sql_list.append(insert_sql)
        self.execute_many_sql(sql_list, values)

    def select_priority_send_weight(self, notice_oritem_list, schedule_no):
        """
        查询已经优先发运的货物的量
        :param schedule_no:
        :param notice_oritem_list:
        :return:
        """
        sql = """
            SELECT
                CONCAT_WS(',',notice_num,oritem_num) as notice_oritem,
                SUM(weight) as weight
            FROM
                db_model.`t_load_task_item`
            WHERE
                CONCAT_WS(',',notice_num,oritem_num) IN ({})
                AND priority IN ({})
                AND create_date RLIKE '{}'
                AND schedule_no != '{}'
        """
        # 发货通知单、订单号条件
        notice_oritem_values = "'"
        notice_oritem_values += "','".join(notice_oritem_list)
        notice_oritem_values += "'"
        # 优先级条件
        priority_values = ("'" + ModelConfig.RG_PRIORITY_GRADE.get(1, "A") + "','" +
                           ModelConfig.RG_PRIORITY_GRADE.get(2, "B") + "'")
        # 当天日期条件
        now_str = get_now_str()
        date = now_str.split(' ')[0]
        sql = sql.format(notice_oritem_values, priority_values, date, schedule_no)
        data = self.select_all(sql)
        # 已经优先发运的字典
        priority_send_weight_dict = {}
        if data:
            for item in data:
                # sql中使用了聚集函数sum，没有记录也会查出来一条空的None
                if not item["weight"]:
                    break
                priority_send_weight_dict[item["notice_oritem"]] = int(item["weight"] * 1000)
        return priority_send_weight_dict


load_task_item_dao = LoadTaskItemDao()

if __name__ == "__main__":
    weight_dict = load_task_item_dao.select_priority_send_weight(['F2105120032,DG2105110002-001'],
                                                                 'C000062070;DD210509002213')
    print(weight_dict)
