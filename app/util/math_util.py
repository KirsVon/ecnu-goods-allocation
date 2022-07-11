# -*- coding: utf-8 -*-
# Description: 
# Created: shaoluyu 2021/7/1 14:34
from typing import List


class MathUtil:
    """

    """

    @staticmethod
    def min(target_list: List, default):
        """

        :param target_list:
        :param default: 缺省值
        :return:
        """
        if not target_list:
            return default
        else:
            return min(target_list)

    @staticmethod
    def max(target_list: List, default):
        """

        :param target_list:
        :param default: 缺省值
        :return:
        """
        if not target_list:
            return default
        else:
            return max(target_list)
