# -*- coding: utf-8 -*-
# Description:
# Created: shaoluyu 2020/9/29 9:14
from collections import defaultdict
from typing import List

from app.main.steel_factory.entity.pick_order_stock import PickOrderStock
from app.util.base.base_dao import BaseDao
from app.util.base.base_dao_2 import BaseDao2
from app.util.base.base_dao_3 import BaseDao3


class PickTimingIssueDao(BaseDao):
    def get_batch_info(self, now_time):
        """
        判断是否到达委托单状态修改时间
        :return:
        """
        sql = """
        SELECT
        batch_no
        FROM
        db_ods.db_tender_t_pickup_order_setting
        WHERE 1 = 1
        AND company_id = 'C000000888'
        AND batch_start_time = '{}'
        AND `status` = 'PCZT01'         
        """
        sql = sql.format(now_time)
        data = self.select_all(sql)
        if data:
            return True
        return False

    def get_batch_line(self):
        """
        查询接受智能下发的线路
        :return:
        """
        sql = """
        SELECT 
        city
        FROM db_ods.db_tender_t_pickup_line
        WHERE 1 = 1
        AND `status` = 'LXZT10'
        -- AND company_id = 'C000062070'
        AND company_id = 'C000000888'
        AND IFNULL(city, '') != ''     
        """
        data = self.select_all(sql)
        result_list = []
        for item in data:
            result_list.append(item.get('city', ''))
        return result_list

    def get_issue_info(self):
        """
        查询智能下发的时间
        :return:
        """
        sql = """
        SELECT
        push_time
        FROM
        db_ods.db_tender_t_pickup_push_line
        WHERE 1 = 1
        AND company_id = 'C000000888'
        AND IFNULL(push_time, '') != ''
        """
        data = self.select_all(sql)
        return data

    def get_consignee_no_list(self):
        sql = """
        SELECT pc.customer_id
        FROM db_ods.db_tender_t_pickup_driver_pool p
        LEFT JOIN db_ods.db_tender_t_pickup_driver_pool_customer pc ON p.driver_pool_id = pc.driver_pool_id
        WHERE 1 = 1
        AND p.`status` = '10'
        AND pc.`status` = '10'
        AND IFNULL(pc.customer_id, '') != ''
        -- GROUP BY pc.customer_id 
        """
        data = self.select_all(sql)
        return [item['customer_id'] for item in data]

    def get_current_wt_info(self, line_list):
        """
        查询符合下发条件的委托单
        :return:
        """
        sql = """
        SELECT
        w.order_no,
        w.city_code,
        w.pick_no,
        -- w.product_name,
        w.spec_desc,
        w.spec_desc_name,
        w.business_nature,
        w.warehouse_out_no,
        -- w.intelligent_dispatch_status,
--         sum( w.total_sheet ) AS wait_compare_total_sheet,
        IFNULL(sum( w.order_zg00 ), 0.0) AS wait_compare_total_sheet,
        w.consignee_company_id,
        IFNULL(w.total_weight, 0.0) total_weight,
        IFNULL(w.bind_no, '') bind_no
        FROM
        (
        SELECT
            w.order_no,
            w.pick_no,
            p.city_code,
            i.product_name,
            i.spec_desc,
            k.itemid spec_desc_name,
            k.order_zg00,
            i.warehouse_out_no,
            w.intelligent_dispatch_status,
            w.consignee_company_id,
            w.total_weight,
            w.business_nature,
            w.bind_no
        FROM
            db_ods.db_trans_t_order_wt_item i
            LEFT JOIN db_ods.db_trans_t_order_wt w ON w.order_no = i.order_no
            LEFT JOIN db_ods.db_inter_t_keeperln k ON k.docuno = i.pick_no AND k.itemname = i.spec_desc
            LEFT JOIN db_ods.db_sys_t_point p ON i.end_point = p.location_id
        WHERE 1 = 1
        AND w.company_id = 'C000000888' 
        AND w.`status` = 'ETST10'
        AND IFNULL(w.order_no, '') != ''
        AND IFNULL(i.spec_desc, '') != ''
        AND IFNULL(i.warehouse_out_no, '') != ''
        -- AND i.spec_desc IN ('165*4.0*6000', '140*2.75*6000')
        AND w.consignee_company_id NOT IN ( 'C000000888', 'C000000878' ) -- 剔除采购
        AND w.business_nature IN ('YWXZ10', 'YWXZ50')
        AND w.intelligent_dispatch_status NOT IN ('IDS40', 'IDS70') -- 非 摘单中、就绪中
        AND w.carrier_company_id = 'C000000888' -- 剔除下发到成都管厂物流的
        AND p.city_code IN ({})
        ) w 
    WHERE 1 = 1
    AND IFNULL(w.warehouse_out_no, '') != ''
    AND IFNULL(w.spec_desc, '') != ''
    GROUP BY
        w.order_no,
        w.spec_desc,
        w.city_code,
        w.spec_desc_name,
        w.warehouse_out_no,
        w.order_zg00
        """
        values = "'"
        values += "','".join([i for i in line_list])
        values += "'"
        sql = sql.format(values)
        data = self.select_all(sql)
        tmp_list = [PickOrderStock(i) for i in data]
        # 根据捆绑单号校验单车重量，剔除总重量小于30t的委托单
        bind_dict = {}      # 捆绑单号重量
        for item in tmp_list:
            if not item.bind_no:
                continue
            if item.bind_no not in bind_dict.keys():
                bind_dict[item.bind_no] = item.total_weight
            else:
                bind_dict[item.bind_no] += item.total_weight
        result_list = [item for item in tmp_list if
                       (not item.bind_no and item.total_weight > 30) or
                       (item.bind_no and bind_dict[item.bind_no] > 30)]
        return result_list

    def get_current_stock_info(self, current_wt_list: List[PickOrderStock]):
        """
        查询当前库存信息
        :return:
        """
        sql = """
        -- 当前库存
        SELECT
        s.ws_name,
        SUBSTRING_INDEX( ws_location_id, '-', 1 ) AS warehouse_out_no,
        s.spec spec_desc,
        s.product_name,
--         sum( s.weight ) AS weight,
--         sum( s.package_num ) AS package_num,
--         IFNULL(sum( s.total_branch_num ), 0.0) AS current_stock_total_sheet
        -- count( 1 ) AS cnt_ws_location_id 
        -- ,s.update_date,s.ws_location_id,s.ws_location
        -- ,s.*
        tmp.weight,
        tmp.package_num,
        tmp.current_stock_total_sheet 
        FROM
        db_ods.db_data_chengdu_t_stock_info s 
        LEFT JOIN (
            SELECT
            s.ws_name,
            SUBSTRING_INDEX( ws_location_id, '-', 1 ) AS warehouse_out_no,
            s.spec spec_desc,
            s.product_name,
            sum( s.weight ) AS weight,
            sum( s.package_num ) AS package_num,
            IFNULL(sum( s.total_branch_num ), 0.0) AS current_stock_total_sheet
            -- count( 1 ) AS cnt_ws_location_id 
            -- ,s.update_date,s.ws_location_id,s.ws_location
            -- ,s.*
            FROM
            db_ods.db_data_chengdu_t_stock_info s 
            WHERE 1 = 1 
            -- AND s.spec IN ('165*4.0*6000','165X4.0X6000')
            AND IFNULL(SUBSTRING_INDEX( ws_location_id, '-', 1 ), '') != ''
            AND IFNULL(s.spec, '') != ''
            AND IFNULL(s.product_name, '') != ''
            AND company_id = 'HL' -- and spec='219X5.0X6000'
            GROUP BY
            s.ws_name,
            SUBSTRING_INDEX( ws_location_id, '-', 1 ),
            product_name
        ) tmp ON tmp.warehouse_out_no = SUBSTRING_INDEX( ws_location_id, '-', 1 ) AND tmp.product_name = s.product_name
        WHERE 1 = 1 
        -- AND s.spec IN ('165*4.0*6000','165X4.0X6000')
        AND IFNULL(SUBSTRING_INDEX( ws_location_id, '-', 1 ), '') != ''
        AND IFNULL(s.spec, '') != ''
        AND IFNULL(s.product_name, '') != ''
        AND company_id = 'HL' -- and spec='219X5.0X6000'
        GROUP BY
        s.ws_name,
        SUBSTRING_INDEX( ws_location_id, '-', 1 ),
        s.product_name,
        s.spec	
        """
        data = self.select_all(sql)
        for current_wt in current_wt_list:
            for item in data:
                warehouse = item.get('warehouse_out_no', '')
                spec = item.get('spec_desc', '')
                spec_desc_name = item.get('product_name', '')
                # 同一个”规格“可能存在多个”规格名“
                if (current_wt.warehouse_out_no == warehouse and
                        current_wt.spec_desc == spec and current_wt.spec_desc_name == spec_desc_name):
                    current_wt.current_stock_total_sheet = float(item.get('current_stock_total_sheet', 0.0))
                    # 库存扣除
                    item['current_stock_total_sheet'] = (float(item.get('current_stock_total_sheet', 0.0))
                                                         - current_wt.wait_compare_total_sheet)
                    break
        return current_wt_list

    def get_have_push_stock_info(self, current_wt_list: List[PickOrderStock]):
        """
        查询已派单的规格信息
        :return:
        """
        sql = """
        -- 已派单
        SELECT 
        r.spec_desc,
        r.warehouse_out_no,
        IFNULL(SUM(r.total_sheet), 0.0) have_push_total_sheet
        FROM(
        SELECT
-- 				d.order_no,
        d.prodspections spec_desc,
        w.pick_no,
        w.total_sheet,
        w.warehouse_out_no 
        FROM
        (
        SELECT
            d.plan_no,
            d.order_no,
            d.create_date,
            d.plan_status,
            d.prodspections,
            d.prodname,
            sum( d.plan_weight ) AS plan_weight 
        FROM
        (
        SELECT
            d.plan_no,
            i.order_no,
            d.create_date,
        CASE
            d.plan_status 
            WHEN 'DDZT10' THEN '待接单' 
            WHEN 'DDZT35' THEN '超时未接单' 
            WHEN 'DDZT30' THEN '调度完成' 
            WHEN 'DDZT40' THEN '已拒单' 
            WHEN 'DDZT20' THEN '已接单' 
            WHEN 'DDZT42' THEN '任务作废' 
            WHEN 'DDZT45' THEN '任务关闭' 
            WHEN 'DDZT50' THEN '已签到' 
            WHEN 'DDZT55' THEN '已开单' 
            WHEN 'DDZT62' THEN '进厂叫号' 
            WHEN 'DDZT58' THEN '已取号' 
            WHEN 'DDZT68' THEN '已进厂' 
            WHEN 'DDZT72' THEN '出库确认' 
            WHEN 'DDZT80' THEN '开始运输' 
            WHEN 'DDZT88' THEN '全部完成' ELSE d.plan_status 
            END AS plan_status, 
            -- ti.warehouse_out_no
            i.prodspections,
            i.prodname,
            -- ti.warehouse_out_name,
            i.plan_weight 
        FROM
            db_ods.db_trans_t_plan d
            LEFT JOIN db_ods.db_trans_t_plan_item i ON i.plan_no = d.plan_no 
        WHERE 1 = 1
            AND d.business_moduleId = '001' 
            AND d.company_id = 'C000000888' 
            AND d.plan_status NOT IN ( 'DDZT35', 'DDZT40', 'DDZT45', 'DDZT80', 'DDZT88', 'DDZT42', 'DDZT30' ) 
            -- 剔除超时未接单、任务关闭、任务作废、已拒单、开始运输、全部完成、调度完成
            AND d.create_date >= '2021-01-01' 
        ORDER BY
            d.create_date DESC 
        ) d 
    GROUP BY
        d.plan_no,
        d.order_no,
        d.prodspections,
        d.prodname 
    ) d
    LEFT JOIN (
    SELECT
        w.order_no,
        w.pick_no,
        w.product_name,
        w.spec_desc,
        w.warehouse_out_no,
        sum( w.order_zg00 ) AS total_sheet 
    FROM
        (
        SELECT
            w.order_no,
            w.pick_no,
            i.product_name,
            i.spec_desc,
--             i.total_sheet,
            k.order_zg00,
            i.warehouse_out_no 
        FROM
            db_ods.db_trans_t_order_wt_item i
            LEFT JOIN db_ods.db_trans_t_order_wt w ON w.order_no = i.order_no 
            LEFT JOIN db_ods.db_inter_t_keeperln k ON k.docuno = i.pick_no AND k.itemname = i.spec_desc
        WHERE 1 = 1
            AND i.create_date >= '2021-01-01'
            AND IFNULL(w.order_no, '') != ''
            AND IFNULL(w.pick_no, '') != ''
            AND IFNULL(i.warehouse_out_no, '') != ''
            AND IFNULL(i.spec_desc, '') != ''
            AND k.order_zg00 > 0
            AND w.company_id = 'C000000888' 
            AND w.consignee_company_id NOT IN ( 'C000000888', 'C000000878' ) -- 剔除采购
            AND w.carrier_company_id <> 'C000000888' -- 剔除下发到成都管厂物流的
        -- and w.order_no='WT210427001512'
        ) w 
    GROUP BY
        w.order_no,
        w.warehouse_out_no,
        w.spec_desc,
--         w.total_sheet 
        w.order_zg00 
    ) w ON w.order_no = d.order_no 
    AND w.product_name = d.prodname 
    AND w.spec_desc = d.prodspections 
AND IFNULL(w.warehouse_out_no, '') != ''
AND IFNULL(w.spec_desc, '') != ''
    -- where d.prodspections='219X5.0X6000'
    WHERE 1 = 1
-- 		AND w.spec_desc = '1020X10.0X12000'
) r
WHERE 1 = 1
AND IFNULL(r.warehouse_out_no, '') != ''
AND IFNULL(r.spec_desc, '') != ''
GROUP BY 
r.spec_desc,
r.warehouse_out_no
        """
        data = self.select_all(sql)
        for current_wt in current_wt_list:
            for item in data:
                warehouse = item.get('warehouse_out_no', '')
                spec = item.get('spec_desc', '')
                if current_wt.warehouse_out_no == warehouse and current_wt.spec_desc == spec:
                    current_wt.have_push_total_sheet = float(item.get('have_push_total_sheet', 0.0))
                    break
        return current_wt_list

    def get_ready_push_stock_info(self, current_wt_list: List[PickOrderStock]):
        """
        查询就绪中、摘单中的规格信息
        :return:
        """
        sql = """
        SELECT
        w.order_no,
        w.pick_no,
        w.product_name,
        w.spec_desc,
        w.warehouse_out_no,
        w.intelligent_dispatch_status,
        -- sum( w.total_sheet ) AS ready_push_total_sheet,
        IFNULL(sum( w.order_zg00 ), 0.0) AS ready_push_total_sheet 
        FROM
        (
        SELECT
            w.order_no,
            w.pick_no,
            i.product_name,
            i.spec_desc,
            i.total_sheet,
            k.order_zg00,
            i.warehouse_out_no,
            w.intelligent_dispatch_status
        FROM
            db_ods.db_trans_t_order_wt_item i
            LEFT JOIN db_ods.db_trans_t_order_wt w ON w.order_no = i.order_no 
            LEFT JOIN db_ods.db_inter_t_keeperln k ON k.docuno = i.pick_no AND k.itemname = i.spec_desc
        WHERE 1 = 1
            AND i.create_date >= '2021-01-01' 
            AND w.company_id = 'C000000888' 
            AND w.consignee_company_id NOT IN ( 'C000000888', 'C000000878' ) -- 剔除采购
            AND w.intelligent_dispatch_status IN ('IDS40', 'IDS70') -- 摘单中库存、就绪中库存
            AND w.carrier_company_id = 'C000000888' -- 剔除下发到成都管厂物流的
            -- and w.order_no='WT210427001512'
        ) w 
        WHERE 1 = 1
        AND IFNULL(w.warehouse_out_no, '') != ''
        AND IFNULL(w.spec_desc, '') != ''
        GROUP BY
        -- w.order_no,
        w.spec_desc,
        -- w.total_sheet,
        w.warehouse_out_no
        """
        data = self.select_all(sql)
        for current_wt in current_wt_list:
            for item in data:
                warehouse = item.get('warehouse_out_no', '')
                spec = item.get('spec_desc', '')
                if current_wt.warehouse_out_no == warehouse and current_wt.spec_desc == spec:
                    current_wt.ready_push_total_sheet = float(item.get('ready_push_total_sheet', 0.0))
                    break
        return current_wt_list

    # def get_wait_push_wt_info(self):
    #     """
    #     查询需要下发的委托单
    #     :return:
    #     """
    #     sql = """
    #     SELECT
    #         w.order_no
    #         -- w.pick_no,
    #         -- i.product_name,
    #         -- i.spec_desc,
    #         -- i.total_sheet,
    #         -- i.warehouse_out_no,
    #         -- w.intelligent_dispatch_status
    #     FROM
    #         db_ods.db_trans_t_order_wt_item i
    #         LEFT JOIN db_ods.db_trans_t_order_wt w ON w.order_no = i.order_no
    #     WHERE 1 = 1
    #         AND i.create_date >= '2021-01-01'
    #         AND w.company_id = 'C000000888'
    #         AND w.consignee_company_id NOT IN ( 'C000000888', 'C000000878' ) -- 剔除采购
    #         AND w.intelligent_dispatch_status = 'IDS70' -- 摘单中库存、就绪中库存
    #         AND w.carrier_company_id = 'C000000888' -- 剔除下发到成都管厂物流的
    #         -- and w.order_no='WT210427001512'
    #     """
    #     data = self.select_all(sql)
    #     return [PickOrderStock(i) for i in data]


pick_timing_issue_dao = PickTimingIssueDao()
