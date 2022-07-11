# -*- coding: utf-8 -*-
# Description:
# Created: jjunf 2020/12/23
from collections import defaultdict
from typing import List


def split_group_util(temp_list: List, attr_list: List, sep=','):
    """
    将列表temp_list按照属性列表attr_list中的属性分组。返回分组后的字典：键为分组属性用分隔符sep（默认逗号）拼接而成，值为传入的对象分组后的列表
    :param sep: 分隔符
    :param attr_list: 分组属性列表
    :param temp_list:需要分组的对象列表
    :return:分组后的字典
    """
    result_dict = defaultdict(list)
    for temp in temp_list:
        key_list = []
        for attr in attr_list:
            # 注：getattr(temp, attr)必须转换为字符串，如果其为数字则下面join的时候会报错
            key_list.append(str(getattr(temp, attr)))
        result_dict[sep.join(key_list)].append(temp)
    return result_dict


def split_list_util(init_list, sep_len):
    """
    将列表init_list按照sep_len个一组进行切分(因为sql查询中的in条件中最多只能有2000个)
    :param init_list:初始列表
    :param sep_len:将多少个切分为一组
    :return:
    """
    result_list = []
    sum_len = 0
    while sum_len < len(init_list):
        result_list.append(init_list[sum_len:sum_len + sep_len])
        sum_len += sep_len
    return result_list
