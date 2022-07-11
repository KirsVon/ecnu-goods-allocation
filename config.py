# -*- coding: utf-8 -*-
# Description: 应用配置文件
# Created: shaoluyu 2019/10/29
# Modified: shaoluyu 2019/10/29

import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """默认配置
    """
    # 应用参数
    APP_NAME = 'models-ecnu-goods-allocation'
    SERVER_PORT = 9268
    #
    FLATPAGES_AUTO_RELOAD = True
    FLATPAGES_EXTENSION = '.md'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'can you guess it'
    DEBUG = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """开发环境配置
    """


class TestConfig(Config):
    """测试环境配置
    """


class UatConfig(Config):
    # 数仓连接
    ODS_MYSQL_HOST = 'am-bp1v0e24374265699167320.ads.aliyuncs.com'
    ODS_MYSQL_PORT = 3306
    ODS_MYSQL_USER = 'modeluser'
    ODS_MYSQL_PASSWD = 'eSod!uuat'
    ODS_MYSQL_DB = 'db_model'
    ODS_MYSQL_CHARSET = 'utf8'

    # Redis配置，可选（不使用时可删除）
    REDIS_HOST = '172.16.110.156'
    REDIS_PORT = '6379'
    REDIS_PASSWD = 'JCdev@56zh'
    REDIS_MAX_CONNECTIONS = 2
    # 微服务url
    DISPATCH_SERVICE_URL = 'http://192.168.1.70:9078'
    # 招投标url
    # TENDER_SERVICE_URL = 'http://192.168.1.20:9108'
    # # 数仓url
    # DATA_WAREHOUSE_URL = 'http://192.168.1.26:9016'
    # tenderUrl
    TENDER_SERVICE_URL = 'https://www.uat.jczh56.com/api/tender'
    # 数仓url
    DATA_WAREHOUSE_URL = 'https://uat.jczh56.com/api/manage'
    # 运力服务url
    CAPACITY_SERVICE_URL = 'http://172.16.110.149:9258'
    # tender的url
    TENDER_URL = 'https://uat.jczh56.com/api/tender'
    # commission的url
    COMMISSION_URL = 'https://uat.jczh56.com/api/commission'
    # APScheduler定时任务配置，可选（不使用时可删除）
    SCHEDULER_OPEN = False
    SCHEDULER_API_ENABLED = True

    # Celery配置，可选（不使用时可删除）
    REDIS_URL = 'redis://:xiexieni56@172.16.110.162:6379/2'
    default_timeout = 60 * 60
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    # 导入任务所在的模块
    CELERY_IMPORTS = ('app.task.celery_task')
    CELERY_DEFAULT_QUEUE = "gc_goods_allocation"
    # 设置定时任务
    from datetime import timedelta
    from celery.schedules import crontab
    CELERY_TIMEZONE = 'Asia/Shanghai'  # 指定时区，不指定默认为 'UTC'
    CELERYBEAT_SCHEDULE = {
        # 'save_hour_stock_': {
        #     'task': 'app.task.celery_task.save_hour_stock_',
        #     'schedule': crontab(minute=0, hour='*/1'),
        #     'args': None
        # },
        # 'push_message': {
        #     'task': 'app.task.celery_task.push_message',
        #     'schedule': crontab(minute='*/5'),
        #     'args': None
        # },
        'push_gc_message': {
            'task': 'app.task.celery_task.push_gc_message',
            'schedule': crontab(minute='*/3'),
            'args': None
        },
        'check_wt_status': {
            'task': 'app.task.celery_task.check_wt_status',
            'schedule': crontab(minute='*/1'),
            'args': None
        },
        # 'check_driver_behavior': {
        #     'task': 'app.task.celery_task.check_driver_behavior',
        #     'schedule': crontab(hour=0, minute=30),
        #     'args': None
        # },
        # 'route_weight_check': {
        #     'task': 'app.task.celery_task.route_weight_check',
        #     'schedule': crontab(minute='*/30'),
        #     'args': None
        # },
        # 'pick_cdpzjh': {
        #     'task': 'app.task.celery_task.pick_cdpzjh',
        #     'schedule': crontab(minute=0, hour='*/1'),
        #     'args': None
        # }
    }


class ProductionConfig(Config):
    """生产环境配置
    """

    # APScheduler定时任务配置，可选（不使用时可删除）
    SCHEDULER_OPEN = False
    SCHEDULER_API_ENABLED = True


# 设置环境配置映射
config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'uat': UatConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_active_config():
    """获取当前生效的环境配置类

    :return: 当前生效的环境配置类
    """
    config_name = os.getenv('FLASK_CONFIG') or 'default'
    return config[config_name]


def get_active_config_name():
    """获取当前生效的环境配置名称

    :return: 当前生效的环境配置名称
    """
    config_name = os.getenv('FLASK_CONFIG') or 'default'
    return config_name
