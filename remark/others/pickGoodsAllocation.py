# -*- coding: utf-8 -*-
# Description: 摘单分货项目其他的说明
# Created: jjunf 2021/01/12


class OthersRemark:
    """
    其他的说明
    """

    # 项目名称
    project_name = '摘单分货项目'
    # 项目接口
    interface_name = '/pickGoodsAllocation'
    # 项目中不发的货物的标记，在存入日志表t_pick_log的时候用'-'拼接到出库仓库outstock_code的后面
    special_remark_dict_in_outstock_code = {
        '0': '件重大于载重上限的货物',
        '1': '被扣除的特殊品种的货物',
        '2': '被扣除的特殊客户的货物',
        '3': '可发小于待发，并且待发在标载范围内的货物',
        '4': '筛除掉的不需要发的货物'
    }
    # 在使用方案2对库存进行扣除时，可能存在倒库的现象，outstock_code中保存2两个库存信息，本次的库存的仓库-被扣除的库存开单的仓库
    # 使用方案2对库存进行扣除后，被扣除的库存仍然存入表中，标记-2，pick_id以deduct开头
