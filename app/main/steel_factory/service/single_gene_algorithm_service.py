#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/18 15:31
# @Author  : \pingyu
# @File    : gene_algorithm_model.py
# @Software: PyCharm
import copy
import random
from operator import itemgetter
from typing import List

from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule.genetic_stock_filter import carpooling_or_not
from app.main.steel_factory.rule.get_value import get_value_load_plan


class Gene:
    def __init__(self, **data):
        self.__dict__.update(data)
        self.size = len(data['data'])


class GA:
    def __init__(self, parameter, truck):
        """
        生成初代种群，并初始化参数
        parameter = [CXPB, MUTPB, NGEN, popsize, low, up, city_stock]
        参数分别为：交叉率，变异率，繁殖代数，种群大小，最小值，最大值，库存
        """
        self.parameter = parameter
        self.truck = truck

        low = self.parameter[4]
        up = self.parameter[5]

        self.stock = self.parameter[6]
        self.n_cargo = len(self.stock)
        self.n_truck = 1

        self.bound = []
        self.bound.append(low)
        self.bound.append(up)

        pop = []
        for i in range(self.parameter[3]):
            geneinfo = [0 for _ in range(self.n_cargo)]

            cargo_pos = random.randint(-1, self.n_cargo - 1)
            if cargo_pos != -1:
                geneinfo[cargo_pos] = 1

            # evaluate each chromosome
            fitness = self.evaluate(geneinfo, flag=0)
            # store the chromosome
            pop.append({'Gene': Gene(data=geneinfo), 'fitness': fitness})

        self.pop = pop
        # store the best chromosome in the population
        self.bestindividual = self.selectBest(self.pop)

    def evaluate(self, geneinfo, flag=1):
        """
        若该（总）装车清单不符合业务规则则返回0
        若该（总）装车清单总重量为0则返回1
        否则返回（总）装车清单总重量
        :param flag: 0表示当前是初始种群，不需要判断是否符合规则
        :param geneinfo:
        :return:
        """
        # 将数组转化为库存数据
        pre_cargo_list: List[Stock] = []
        for cargo_pos in range(self.n_cargo):
            if geneinfo[cargo_pos]:
                pre_cargo_list.append(self.stock[cargo_pos])

        # 若当前车次无货，则直接返回1
        if sum(geneinfo) == 0:
            return 1

        # 非初始种群需做额外规则判断
        if flag == 1:
            if not carpooling_or_not(pre_cargo_list, self.truck):
                return 0

        curr_value = 0
        """
        收益定义：
        1. 货物优先级，数字越小，优先级越高
        2. 装卸优先级，数字越小，优先级越高
        3. 仓库优先级，数字越小，优先级越高
        4. 重量优先级，数字越大，优先级越高
        """
        # 各特征对应的权重值
        priority_weights = [10, 5, 7, -1]
        # 得到当前预装车清单的价值
        curr_value = get_value_load_plan(pre_cargo_list, priority_weights)

        # 缩放value，使得最终的收益大于0且值越大表示解越优秀
        curr_value = -curr_value
        curr_value += 100

        return curr_value

    def selectBest(self, pop):
        """
        初代最好的个体保留作为记录
        对整个种群按照适应度函数降序排列，取最大值的个体
        """

        s_inds = sorted(pop, key=itemgetter("fitness"), reverse=True)

        return s_inds[0]

    def selection(self, individuals, k):
        """
        # 按照概率选择后代，适应度函数大的个体大概率被选到下一代，对重新生成的新一代种群按照适应度升序排列
        """

        s_inds = sorted(individuals, key=itemgetter("fitness"), reverse=True)
        sum_fits = sum(ind['fitness'] for ind in individuals)

        chosen = []
        for i in range(k):
            # 随机生成一个[0, sum_fits]范围内的数字作为阈值
            u = random.random() * sum_fits
            sum_ = 0
            for ind in s_inds:
                sum_ += ind['fitness']
                if sum_ >= u:
                    chosen.append(ind)
                    break
        chosen = sorted(chosen, key=itemgetter("fitness"), reverse=False)
        return chosen

    def crossoperate(self, offspring):
        """
        使用双点交叉，改变原基因序列从而实现优化
        从选中的种群中分别选出第一个和第二个子代
        [1, 2, 3, 4, 5], [6, 7, 8, 9, 10]
        [1, 7, 8, 9, 5], [6, 2, 3, 4, 10]
        """

        geninfo1 = offspring[0]['Gene'].data
        geninfo2 = offspring[1]['Gene'].data

        if self.n_cargo == 1:
            pos1 = 0
            pos2 = 0
        else:
            pos1 = random.randint(0, self.n_cargo-1)
            pos2 = random.randint(0, self.n_cargo-1)

        newoff1 = Gene(data=[])
        newoff2 = Gene(data=[])
        temp1 = []
        temp2 = []

        for cargo_index in range(self.n_cargo):
            if min(pos1, pos2) <= cargo_index < max(pos1, pos2):
                temp2.append(geninfo2[cargo_index])
                temp1.append(geninfo1[cargo_index])
            else:
                temp2.append(geninfo1[cargo_index])
                temp1.append(geninfo2[cargo_index])

        newoff1.data = temp1
        newoff2.data = temp2

        return newoff1, newoff2

    def mutation(self, crossoff):
        """
        变异过程：这里使用单点变异
        [0, 0, 0, 1, 0, 0]
        随机选取变异位置，变异后为
        [1, 0, 0, 1, 0, 0]
        """

        mut_gene = copy.deepcopy(crossoff.data)

        pos = random.randint(0, self.n_cargo-1)
        if mut_gene[pos] == 0:
            mut_gene[pos] = 1

        crossoff.data = mut_gene
        return crossoff

    def GA_main(self):
        """
        主函数入口
        利用初代种群进行进化，每一次进化都保存当前种群中最优秀的个体和对用的适应度值
        """

        CXPB = self.parameter[0]
        MUTPB = self.parameter[1]
        NGEN = self.parameter[2]
        popsize = self.parameter[3]

        best_fitness = []

        #print("Start of evolution")
        # 开始进化
        for g in range(NGEN):
            #print("######### Generation {} #########".format(g))

            # 根据转换的合适度选择种群
            selectpop = self.selection(self.pop, popsize)

            nextoff = []
            while selectpop:
                # 对子代进行交叉和变异
                # 选择两个个体
                offspring = [selectpop.pop() for _ in range(2)]
                if random.random() < CXPB:
                    # 进行交叉
                    crossoff1, crossoff2 = self.crossoperate(offspring)
                    if random.random() < MUTPB:
                        # 进行变异
                        muteoff1 = self.mutation(crossoff1)
                        muteoff2 = self.mutation(crossoff2)
                        fit_muteoff1 = self.evaluate(muteoff1.data)
                        fit_muteoff2 = self.evaluate(muteoff2.data)
                        # fit_muteoff3 = self.evaluate(muteoff3.data)
                        # fit_muteoff4 = self.evaluate(muteoff4.data)
                        nextoff.append({'Gene': muteoff1, 'fitness': fit_muteoff1})
                        nextoff.append({'Gene': muteoff2, 'fitness': fit_muteoff2})
                        # nextoff.append({'Gene': muteoff3, 'fitness': fit_muteoff3})
                        # nextoff.append({'Gene': muteoff4, 'fitness': fit_muteoff4})
                    else:
                        fit_crossoff1 = self.evaluate(crossoff1.data)
                        fit_crossoff2 = self.evaluate(crossoff2.data)
                        nextoff.append({'Gene': crossoff1, 'fitness': fit_crossoff1})
                        nextoff.append({'Gene': crossoff2, 'fitness': fit_crossoff2})
                else:
                    nextoff.extend(offspring)


            # 子代种群替代父代种群
            self.pop = nextoff

            # 计算并收集适应度函数
            fits = [ind['fitness'] for ind in self.pop]

            best_ind = self.selectBest(self.pop)

            if best_ind['fitness'] > self.bestindividual['fitness']:
                self.bestindividual = best_ind

            best_fitness.append(self.bestindividual['fitness'])

            #print("Best individual found is {}, {}".format(self.bestindividual['Gene'].data, self.bestindividual['fitness']))

            #print(" Max fitness of current pop: {}".format(max(fits)))

        #print("-------- End of (successful) evolution --------")

        return self.bestindividual['Gene'].data, self.bestindividual['fitness']

        # x = [i for i in range(NGEN)]
        # y = best_fitness
        # plt.plot(x, y)
        # plt.xlabel('迭代次数')
        # plt.ylabel('总收益')
        # plt.rcParams['font.sans-serif'] = ['SimHei']
        # plt.show()
