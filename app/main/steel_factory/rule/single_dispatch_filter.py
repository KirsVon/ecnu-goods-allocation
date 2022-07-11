from app.main.steel_factory.rule import single_priority_rule, single_layer_rule, single_tail_stock_grouping_rule
from app.main.steel_factory.rule.knapsack_algorithm_model import single_knapsack_model
from app.main.steel_factory.service import single_stock_service
from app.main.steel_factory.entity.truck import Truck
from model_config import ModelConfig


def dispatch(truck: Truck):
    """
    单车分货模块
    """
    # 获取指定库存
    stock_list = single_stock_service.get_stock(truck)
    # 急发客户轮询，调整库存顺序
    stock_list = single_priority_rule.consumer_filter(stock_list)
    # 货物按尾货-tail、锁货-lock、大批量货-huge分组
    stock_dic = single_tail_stock_grouping_rule.tail_grouping_filter(stock_list)
    # 生成车次
    if truck.city in ModelConfig.SINGLE_USE_OPTIMAL_CITY or '全部' in ModelConfig.SINGLE_USE_OPTIMAL_CITY:
        load_task = single_knapsack_model(stock_list, stock_dic, truck)
    else:
        load_task = single_layer_rule.layer_filter_2(stock_list, stock_dic, truck)
    # 如果没有配载结果并且车辆报道重量不高于35/2，进行拆件配载
    if truck.city in ModelConfig.SINGLE_SUB_STOWAGE_CITY or '全部' in ModelConfig.SINGLE_SUB_STOWAGE_CITY:
        if not load_task and truck.load_weight <= ModelConfig.RG_MAX_WEIGHT:
            load_task = single_layer_rule.split_filter(stock_list, truck)
    return load_task
