# -*- coding: utf-8 -*-
# Description: 
# Created: shaoluyu 2020/12/22 13:37
import traceback

from flask import current_app, g, request


class LogBufferUtil(object):

    @staticmethod
    def collect_log(log_str):
        g.log_list.append(str(log_str))

    @staticmethod
    def collect_log_list(log_str_list):
        g.log_list.extend([str(log_str) for log_str in log_str_list])

    @staticmethod
    def output_log():
        target_log = '\n'.join(g.log_list)
        current_app.logger.info(target_log)

    @staticmethod
    def exception_log():
        target_log = '\n'.join([
            '===error_api_name:{}==='.format(request.url.split('/')[-1]),
            traceback.format_exc(),
            '===error_end==='
        ])
        current_app.logger.info(target_log)
