# -*- coding: utf-8 -*-
# Description: 模型配置参数类
# Created: jjunf 2021/5/21 12:43
from app.util.base.base_entity import BaseEntity


class ModelConfig(BaseEntity):
    """
    模型配置参数类
    """

    def __init__(self, model_config=None):
        # 项目接口名称
        self.interface_name = None
        # 模型配置参数名称
        self.config_name = None
        # 字符1
        self.str_1 = None
        # 字符2
        self.str_2 = None
        # 字符3
        self.str_3 = None
        # 字符4
        self.str_4 = None
        # 整型1
        self.int_1 = None
        # 整型2
        self.int_2 = None
        # 整型3
        self.int_3 = None
        # 整型4
        self.int_4 = None
        # 小数1
        self.decimal_1 = None
        # 小数2
        self.decimal_2 = None
        # 小数3
        self.decimal_3 = None
        # 小数4
        self.decimal_4 = None

        if model_config:
            self.set_attr(model_config)



