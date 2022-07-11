#!/usr/bin/python
# -*- coding: utf-8 -*-
# Description: 
# Created: lei.cheng 2021/8/26
# Modified: lei.cheng 2021/8/26
from typing import List
from app.main.steel_factory.entity.stock import Stock


def knapsack(parameter, stock_list: List[Stock]):

    # 缩放重量精度，用于01背包模型的精度控制
    for stock in stock_list:
        stock.piece_weight /= parameter['multiple_num']
    max_weight = parameter['max_weight'] / parameter['multiple_num']

    # 重量权重
    w1 = parameter['weight_tuple'][0]
    # 装点权重
    w2 = parameter['weight_tuple'][1]
    # 卸点权重
    w3 = parameter['weight_tuple'][2]
    # 货物优先级权重
    w4 = parameter['weight_tuple'][3]
    # 仓库优先级权重
    w5 = parameter['weight_tuple'][4]

    # 装点数量上限
    max_load_point_num = parameter['max_load_point_num']
    # 卸点数量上限
    max_unload_point_num = parameter['max_unload_point_num']

    # 货物件数
    n = len(stock_list)
    # dp
    dp = [[{'score': 0, 'select': [0 for i in range(n)]} for j in range(int(max_weight)+1)] for i in range(n+1)]

    def cal_score(current_select_list):
        """根据选择的货物列表，计算分值"""

        # 默认货物优先级
        stock_priority = 10
        # 默认仓库优先级
        warehouse_priority = 10
        # 仓储库
        LC_warehouse = ["F1", "F2"]
        LBG_warehouse = ["F10", "F20"]
        # 默认为生产+仓储一体库
        default_warehouse_priority = 1
        LC_warehouse_priority = 2
        LBG_warehouse_priority = 3

        sum_weight = 0          # 总重量
        load_point = set()      # 装点集合
        unload_point = set()    # 卸点集合

        # 统计被选中的货物
        for i in range(n):
            if current_select_list[i]:
                sum_weight += stock_list[i].piece_weight
                load_point.add(stock_list[i].deliware_house)
                unload_point.add(stock_list[i].standard_address)
                # 若有拼货，该装车清单的优先级取最高优先级
                stock_priority = min(stock_priority, stock.priority)
                # 若有拼货，取优先级最高的仓库
                if stock.deliware_house in LC_warehouse:
                    curr_warehouse_priority = LC_warehouse_priority
                elif stock.deliware_house in LBG_warehouse:
                    curr_warehouse_priority = LBG_warehouse_priority
                else:
                    curr_warehouse_priority = default_warehouse_priority
                warehouse_priority = min(warehouse_priority, curr_warehouse_priority)

        # 计算分值
        score = sum_weight * w1 \
                + (2-len(load_point)) * w2 \
                + (2-len(unload_point)) * w3 \
                + (10-stock_priority) * w4 \
                + (10-warehouse_priority) * w5

        return score

    def cal_load_point_num(i, j):
        load_point = set()
        # front_dp
        front_dp = dp[i-1][int(j-stock_list[i-1].piece_weight)]
        select_list = front_dp['select']
        for k in range(n):
            # 如果该件货被选中
            if select_list[k]:
                load_point.add(stock_list[k].deliware_house)
        load_point.add(stock_list[i-1].deliware_house)
        return len(load_point)

    def cal_unload_point_num(i, j):
        unload_point = set()
        # front_dp
        front_dp = dp[i-1][int(j-stock_list[i-1].piece_weight)]
        select_list = front_dp['select']
        for k in range(n):
            # 如果该件货被选中
            if select_list[k]:
                unload_point.add(stock_list[k].standard_address)
        unload_point.add(stock_list[i-1].standard_address)
        return len(unload_point)

    def is_over_max_weight(i, j):
        """判断是否超过最大重量"""
        front_dp = dp[i - 1][int(j - stock_list[i - 1].piece_weight)]
        front_select_list = front_dp['select']
        current_select_list = []
        for k in range(n):
            if k == i-1:
                current_select_list.append(1)
            else:
                current_select_list.append(front_select_list[k])

        sum_weight = 0
        for index, state in enumerate(current_select_list):
            if state == 1:
                sum_weight += stock_list[index].piece_weight

        if sum_weight > max_weight:
            return True
        else:
            return False

    def judge_legal(i, j):
        """判断当前货物是否可以加入背包"""
        # 判断当前货物重量是否小于背包容量
        if stock_list[i-1].piece_weight > j:
            return False
        if cal_load_point_num(i, j) > max_load_point_num:
            return False
        if cal_unload_point_num(i, j) > max_unload_point_num:
            return False
        # 不超过最大重量
        if is_over_max_weight(i, j):
            return False

        return True

    def select_max_dp(i, j):
        """选择前一个dp、加入当前货物的dp的最大分数"""
        up_dp = dp[i - 1][j]
        front_dp = dp[i - 1][int(j - stock_list[i - 1].piece_weight)]
        front_select_list = front_dp['select']
        current_select_list = []

        for k in range(n):
            if k == i-1:
                current_select_list.append(1)
            else:
                current_select_list.append(front_select_list[k])

        up_score = up_dp['score']
        current_score = cal_score(current_select_list)
        if current_score > up_score:
            return {'score': current_score, 'select': current_select_list}
        else:
            return up_dp

    def generate_pre_load_task_list(select_state):
        """生成预装载任务列表"""
        sum_weight = 0
        pre_load_task_list = []
        for index, state in enumerate(select_state):
            if state == 1:
                pre_load_task_list.append(stock_list[index])
                sum_weight += stock_list[index].piece_weight

        if not pre_load_task_list or sum_weight < parameter['min_weight']:
            return None
        return pre_load_task_list

    for i in range(1, n+1):
        for j in range(1, int(max_weight)+1):
            # 判断当前货物是否可以加入背包
            if not judge_legal(i, j):
                dp[i][j] = dp[i-1][j]
            else:
                dp[i][j] = select_max_dp(i, j)

    # for i in range(0, n + 1):
    #     for j in range(0, int(max_weight) + 1):
    #         print(dp[i][j]['score'], end=' ')
    #     print('\n')

    # print(dp[n][int(max_weight)])

    for stock in stock_list:
        stock.piece_weight *= parameter['multiple_num']

    max_score = 0
    select_state = []
    for i in range(0, n + 1):
        for j in range(0, int(max_weight) + 1):
            if dp[i][j]['score'] > max_score:
                max_score = dp[i][j]['score']
                select_state = dp[i][j]['select']

    # return dp[n][int(max_weight)]['score'], dp[n][int(max_weight)]['select']

    pre_load_task_list = generate_pre_load_task_list(select_state)
    return pre_load_task_list
