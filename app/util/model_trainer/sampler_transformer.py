# coding=utf-8

import random


def simple_sampling(data_mat: list, num: int) -> list:
    """
	简单随机采样
	:param data_mat:
	:param num:
	:return:
	"""
    try:
        samples = random.sample(data_mat, num)
        return samples
    except:
        print('采样样本数超过了数据集长度')


def systematic_sampling(data_mat: list, num: int) -> list:
    """
	系统采样
	:param data_mat:
	:param num:
	:return:
	"""
    k = int(len(data_mat) / num)
    samples = [random.sample(data_mat[i * k:(i + 1) * k], 1) for i in range(num)]
    return samples
