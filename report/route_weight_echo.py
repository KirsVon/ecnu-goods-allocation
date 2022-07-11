import time

from model_config import ModelConfig
from report.utils.db import pd_sel,sel_one
import pandas as pd

from report.utils.mail import mail

from geopy import distance

pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)


def get_plan(rount):
    sql = '''
        SELECT
            a.create_date AS '调度时间'
            -- ,a.checkIn_time as '报道时间'
            ,case when a.checkIn_time is null then null else TIMESTAMPDIFF(HOUR, a.create_date, a.checkIn_time) end as '报告时长（hour）'
            ,r.driver_id
            ,e.company_name AS '车队'
            ,b.prodname as '品种'
            ,case a.plan_source when 'DDLY10' then '定向' when 'DDLY20' then '抢单' 
                when 'DDLY40' then '手工调度' when 'DDLY50' then '摘单' else a.plan_source end as '调度方式'
            ,CASE a.plan_status WHEN 'DDZT20' THEN '已接单' WHEN 'DDZT42' THEN '任务作废' 
                 WHEN 'DDZT45' THEN '任务关闭' WHEN 'DDZT50' THEN '已签到' 
                 WHEN 'DDZT55' THEN '已开单' WHEN 'DDZT68' THEN '已进厂' 
                 WHEN 'DDZT72' THEN '出库确认' WHEN 'DDZT80' THEN '开始运输' 
                 WHEN 'DDZT88' THEN '全部完成' ELSE a.plan_status END AS '状态' 
            ,b.plan_weight as '重量'
            ,a.remark as '备注'
            ,r.vehicle_no as '车牌'
            -- ,du.login_name as '司机手机'
            -- ,a.update_date
            -- ,u.`name` as '调度员'
        FROM
            db_ods.db_trans_t_plan a
            LEFT JOIN db_ods.db_trans_t_plan_item b ON a.plan_no = b.plan_no
            LEFT JOIN db_ods.db_sys_t_point c ON b.end_point = c.location_id
            LEFT JOIN db_ods.db_inter_lms_bclp_loading_main d ON a.plan_no = RIGHT ( d.schedule_no, 14 )
            LEFT JOIN db_ods.db_sys_t_company_base e ON a.company_id = e.company_id 
            left join db_ods.db_sys_t_user u on a.create_id = u.user_id
            left join db_ods.db_trans_t_plan_driver r on r.plan_no = a.plan_no
            left join db_ods.db_sys_t_user du on du.user_id=r.driver_id
            left join db_ods.db_sys_t_user op on op.user_id=a.update_id
        WHERE
            a.business_moduleId IN ( '020' )  -- 业务板块是日钢汽运
            and a.consignor_company_id = 'C000000882'  -- 代表托运人是日钢物流
            AND a.create_date > current_date()
            AND c.city_name = '{}'
          order by a.create_date desc
    '''.format(rount)
    return pd_sel(sql)


def rount_house_echo(route, warn_beyond_weight=None, warn_under_weight=None):
    sql = '''
        select 
            a.ods_update_time
            ,a.cansendweight
            ,a.commodityname
            ,a.address
            ,a.ENDCUSTMER
            ,a.DELIWAREHOUSE
            ,a.WAINTFORDELWEIGHT
        from ods_db_inter_bclp_can_be_send_amount a
        where 
            a.`STATUS`<>'D'
            and a.city='{}'
            and a.cansendweight>0.0
            order by cast(a.cansendweight as decimal(10,2)) desc,a.ods_update_time desc
    '''.format(route)
    data = pd_sel(sql, env='test')

    #print(data.info())
    data['cansendweight'] = data['cansendweight'].apply(lambda x: float(x))
    sum_cansendweight = data['cansendweight'].sum()
    #print(sum_cansendweight)

    warn_body = ''

    if warn_beyond_weight:
        if isinstance(warn_beyond_weight,int) and sum_cansendweight > warn_beyond_weight:
            warn_body += '{} 库存 > {}\t'.format(route, warn_beyond_weight)
        if isinstance(warn_beyond_weight,list):
            warn_beyond_weight.reverse()
            for warn_weight in warn_beyond_weight:
                if sum_cansendweight > warn_weight:
                    warn_body += '{} 库存 > {}\t'.format(route, warn_weight)
                    break

    if warn_under_weight:
        if isinstance(warn_under_weight,int) and sum_cansendweight < warn_under_weight:
            warn_body += '{} 库存 < {}\t'.format(route, warn_under_weight)
        if isinstance(warn_under_weight,list):
            for warn_weight in warn_under_weight:
                if sum_cansendweight < warn_weight:
                    warn_body += '{} 库存 < {}\t'.format(route, warn_weight)
                    break

    if warn_body:
        #打印当天派单信息
        data_plan = get_plan(route)
        #print(data_plan)
        data_plan['vehicle_distance'] = data_plan['车牌'].map(lambda x: vehicle_distance(x))
        print(data_plan)

        title = warn_body
        text = str(data)+'\n'*2+str(data_plan)
        #mail(title, text)
    #print(data)

def route_weight_echo():
    #rount_house_echo('潍坊市', warn_under_weight=[500,1000])
    #rount_house_echo('济宁市', warn_beyond_weight=[100,200,500])
    rount_house_echo('泰安市', warn_beyond_weight=[100,200,500])

def vehicle_distance(vehicle_no):
    sql = '''
        select lat,lon
        from db_ads.hhy_truck_now_location_zjxl 
        where truck_no='鲁Q188CZ' 
        order by utc 
        limit 1;
    '''
    data = sel_one(sql, env='test')
    vehicle_tuple = (data['lat'], data['lon'])
    #print(vehicle_tuple)

    # 日钢位置：纬度、经度
    rg_tuple = (ModelConfig.PICK_RG_LAT.get("日钢纬度"), ModelConfig.PICK_RG_LON.get("日钢经度"))
    #print(rg_tuple)

    dist = distance.great_circle(vehicle_tuple, rg_tuple).km
    return dist


if __name__ == '__main__':
    #route_weight_echo()
    #vehicle_distance('鲁Q188CZ')
    while True:
        route_weight_echo()
        time.sleep(60*30)
