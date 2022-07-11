from app.main.steel_factory.service.pick_model_config_service import get_model_config_service
from app.main.steel_factory.service.model_config_service import get_single_model_config_service


class ModelConfig:
    """模型参数配置
    """

    # 日钢标载
    RG_DEFAULT_CITY = '临沂市'
    RG_U289 = 'U289-绿色通道库暂时关闭'
    # 相同区县相同客户相同品种的货物切分时的载重界限
    RG_CONSUMER_WEIGHT = 200000
    # 整个区县的货物在不超此重量且能一车拼走的情况下直接一车带走
    RG_EARLY_MAX_WEIGHT = 40400
    # 滨州的载重上限
    RG_TO_BZ_MAX_WEIGHT = 39000
    # 标载上限
    RG_MAX_WEIGHT = 35000
    # 标载下限（非卷类）
    RG_MIN_WEIGHT = 31000
    # 标载下限（卷类）
    RG_J_MIN_WEIGHT = 29000
    RG_J_PIECE_MIN_WEIGHT = 26000
    # 单件卷类在无货可拼时的下限
    RG_SECOND_MIN_WEIGHT = 24000
    # 载重上限上浮
    RG_SINGLE_UP_WEIGHT = 1000
    # 非标载 最大下浮下限（例45吨的车，载重下限为43吨）
    RG_SINGLE_LOWER_WEIGHT = 2000
    # 各品种载重下限
    RG_COMMODITY_WEIGHT = {'老区-卷板': RG_J_MIN_WEIGHT,
                           '新产品-卷板': RG_J_MIN_WEIGHT,
                           '新产品-白卷': RG_J_MIN_WEIGHT,
                           '老区-型钢': RG_MIN_WEIGHT,
                           '老区-线材': RG_MIN_WEIGHT,
                           '老区-螺纹': RG_MIN_WEIGHT,
                           '老区-开平板': RG_MIN_WEIGHT,
                           '新产品-窄带': RG_MIN_WEIGHT,
                           '新产品-冷板': RG_MIN_WEIGHT
                           }
    # 品种中的卷类
    RG_J_GROUP = ['老区-卷板', '新产品-卷板', '新产品-白卷']
    # 滨州只发下面的货物
    RG_BZ_GROUP = ['老区-卷板', '新产品-卷板', '新产品-白卷', '老区-型钢', '老区-线材', '老区-螺纹', '老区-开平板']
    # 优先级
    RG_PRIORITY = {'客户催货一级': 1, '客户催货二级': 2, '超期清理': 3}
    # 优先级:1.客户催货1；2.客户催货2；3（保留为仓库效率）；4.超期清理1(24-48小时)；5.超期清理2(>48小时)；9.其余
    RG_PRIORITY_GRADE = {}  # {1: "A", 2: "B", 3: "C", 4: "D"}
    # 超期清理的时间下限(小时)
    OVER_TIME_LOW_HOUR = 24
    # 超期清理的时间上限(小时)
    OVER_TIME_UP_HOUR = 48
    # 需要按备注指定客户的城市：支持全部，只要其中包含全部，就是全部城市
    SINGLE_DESIGNATE_CONSUMER_CITY = ['全部']
    # 是否严格按照调度备注指定的客户进行筛选：0：完全按照指定的客户筛选，没货不推荐；1：先按照指定的客户筛选，没货后放宽条件，开其他客户的货
    SINGLE_DESIGNATE_CONSUMER_FLAG = 0
    # 使用优化版本的城市：支持全部，只要其中包含全部，就是全部城市
    SINGLE_USE_OPTIMAL_CITY = []
    # 配载无结果后进行拆件配载的城市：支持全部，只要其中包含全部，就是全部城市
    SINGLE_SUB_STOWAGE_CITY = []
    # 单车分货时最多匹配结果数量的一个阈值上限
    RG_SINGLE_COMPOSE_MAX_LEN = 8
    # 单车分货中优先级的价值
    SINGLE_VALUE_OF_PRIORITY = [10, 10]
    # 单车分货中卸点客户的价值
    SINGLE_VALUE_OF_CONSUMER = [2, 2]
    # 单车分货中装点仓库的价值
    SINGLE_VALUE_OF_DELIWARE = [2, 1]
    # 单车分货中装点仓库效率的价值:各仓库默认一般车辆容纳数、仓库作业效率放大的比例、联储仓库被扣减的价值
    SINGLE_VALUE_OF_DELIWARE_EFFICIENCY = [20, 5, -2]
    # 单车分货中装点厂区的价值
    SINGLE_VALUE_OF_FACTORY = [2, 2]
    # 单车分货中载重的价值
    SINGLE_VALUE_OF_WEIGHT = [2]
    # 单车分货中订单的价值
    SINGLE_VALUE_OF_ORDER_NUM = [-0.5]
    # 件重大于此值的优先排到前面配货
    SINGLE_BIG_PIECE_WEIGHT = 16500
    # 单车分货中额外添加的价值
    SINGLE_VALUE_OF_EXTRA = [80]
    # 单车分货中非生产用来存储货物的仓库
    SINGLE_STORAGE_DELIWARE = ['F2', 'F1', 'F20', 'F10']
    # 外贸对应的入库仓库
    RG_FOREIGN_TRADE_DELIWARE = ['东泰码头', '东联码头', '东鸿码头']
    # 暂停推荐的码头
    STOP_RG_FOREIGN_TRADE_DELIWARE = ['东泰码头', '东联码头', '东鸿码头']
    # 按流向只发哪些客户的货
    SINGLE_KEEP_CONSUMER = {
        # '连云港市,连云区': ['东方国际集装箱（连云港）有限公司']
    }
    # 按流向不发哪些客户的货
    SINGLE_REJECT_CONSUMER = {
        # '连云港市,连云区': ['东方国际集装箱（连云港）有限公司']
    }
    # 不使用推荐开单的（流向、车队）：['连云港市,连云区,源运物流', '连云港市,连云区,全部', '连云港市,全部,全部', '全部,全部,全部']
    SINGLE_BLACK_LIST = []
    # 相同的单子被删除多少次后将被锁定
    SINGLE_NUM_LOCK = 2
    # 相同的单子被删除多少次后将被锁定的时间：小时
    SINGLE_LOCK_HOUR = 12
    # 被删除后需要锁定的单子 是否需要筛掉：1筛掉，0不筛掉
    SINGLE_LOCK_ORDER_FLAG = 1
    # 被删除后需要锁定的单子：发货通知单号、订单号、出库仓库 ["F2105130102,DH2105130017-007,Z1"]
    SINGLE_LOCK_ORDER = []
    # 联运码头对应报道区县
    RG_LY_GROUP = {
        # '赣榆区': ['U220-赣榆库', '赣榆区'],
        # '黄岛区': ['U210-董家口库', '黄岛区'],
        # '淮阴区': ['U288-岚北港口库2', '淮阴区'],
        # '灌云县': ['U288-岚北港口库2LYG', '灌云县'],
        # '连云区': ['U123-连云港东泰码头(外库)', 'U124-连云港东联码头(外库)', '连云区']
    }
    # 窄带的包装形式
    RG_NB_PACK = [
        ['FJC71', 'GJC71', 'HLC02', 'PJC71'],  # 木托
        ['CJC77', 'FJC77', 'FJC76', 'HLC01', 'HLC03', 'GJC76', 'PJC77', 'PJC76']  # 窄带卷
    ]
    # 使用遗传算法的标志：1使用，0不使用
    GA_USE_FLAG = 1
    # 使用遗传算法的结果作为输出的标志：1将遗传算法的结果作为输出，0不将遗传算法的结果作为输出
    GA_USE_RESULT_FLAG = 0
    # 遗传中迭代的次数、交叉的次数
    GA_PARAM = [400, 40]
    # 遗传算法中车次数减少1的价值、尾货的价值
    GA_FITNESS_VALUE_PARAM = [4, -10]
    # 遗传算法中卸点客户的价值
    GA_FITNESS_VALUE_CONSUMER = [1, -1, -2]
    # 遗传算法中装点仓库的价值
    GA_FITNESS_VALUE_DELIWARE = [1, -1, -2]
    # 遗传算法中装点厂区的价值
    GA_FITNESS_VALUE_FACTORY = [1, -1, -2]
    # 需要按客户取价格的城市
    GET_PRICE_BY_CONSUMER_CITY = ['青岛市']
    # 调度人员联系方式：庞强年18939958645；付鑫源15254482915；李相锐17686338303；厉岩15306338087
    DISPATCHER_PHONE_DICT = {
        '泰安市': '15254482915',
        '淄博市': '15254482915',
        '滨州市': '15254482915',
        '莱芜市': '15254482915',
        '青岛市': '17686338303',
        '济宁市': '15306338087'
    }
    # 各城市的发运量限制：字典：{城市：[给运营预留的派单重量,摘单和派单的重量上限]}（单位：吨）
    CITY_DISPATCH_WEIGHT_LIMIT_DICT = {
        '青岛市': [0, 900],
        '泰安市': [300, 9999]
    }
    # 一条摘单计划，最大的车次数限制
    PICK_TRUCK_NUM_UP_LIMIT = 10
    # 库存扣除标志：0使用库存扣除方案1，1使用库存扣除方案2
    RG_STOCK_DEDUCT_FLAG = 0
    # 没有开单明细的库存、或者只有部分有开单明细（这部分在生成摘单计划后扣除）
    deduct_stock_list_without_detail = []
    # 被扣除的有开单明细的库存（在库存预处理中被扣除）在pick_deduct_stock_service.deduct_operation方法这初始化
    be_deducted_stock_list = []
    # 相同客户配置
    CONSUMER_DICT = {
        '山东省博兴县拓鑫钢铁贸易有限公司': '山东鹏禾新材料有限公司'
    }
    # 可跨区县拼货配置：键为优先级，值为可跨区县拼货的区县（要求已经按照优先级从高到低排好序）
    ACROSS_DISTRICT_DICT = {
        '1': ['山东省,济南市,天桥区', '山东省,济南市,历城区'],
        '2': ['山东省,济南市,天桥区', '山东省,济南市,槐荫区'],
        '3': ['山东省,济南市,天桥区', '山东省,济南市,市中区'],
        '4': ['山东省,济南市,历城区', '山东省,济南市,槐荫区'],
        '5': ['山东省,济南市,槐荫区', '山东省,济南市,市中区']
    }
    RG_COMMODITY_GROUP = {'老区-型钢': ['老区-型钢'],
                          '老区-线材': ['老区-线材'],
                          '老区-螺纹': ['老区-螺纹'],
                          '老区-开平板': ['老区-开平板'],
                          '老区-卷板': ['新产品-白卷', '老区-卷板', '新产品-卷板'],
                          '新产品-白卷': ['新产品-白卷', '老区-卷板', '新产品-卷板'],
                          '新产品-卷板': ['新产品-白卷', '老区-卷板', '新产品-卷板'],
                          # '新产品-白卷': ['新产品-窄带', '新产品-冷板', '新产品-白卷', '老区-卷板', '新产品-卷板'],
                          # '新产品-卷板': ['新产品-窄带', '新产品-冷板', '新产品-白卷', '老区-卷板', '新产品-卷板'],
                          '新产品-窄带': ['新产品-窄带', '新产品-冷板', '新产品-白卷', '新产品-卷板'],
                          '新产品-冷板': ['新产品-窄带', '新产品-冷板', '新产品-白卷', '新产品-卷板']
                          }

    RG_QD_COMMODITY_GROUP = {'老区-型钢': ['老区-型钢'],
                             '老区-线材': ['老区-线材'],
                             '老区-螺纹': ['老区-螺纹'],
                             '老区-开平板': ['老区-开平板'],
                             '老区-卷板': ['老区-卷板'],
                             '新产品-冷板': ['新产品-冷板','新产品-开平板'],
                             '新产品-白卷': ['新产品-白卷', '新产品-卷板', '新产品-窄带'],
                             '新产品-卷板': ['新产品-白卷', '新产品-卷板', '新产品-窄带'],
                             '新产品-窄带': ['新产品-窄带', '新产品-白卷', '新产品-卷板'],
                             '新产品-开平板':['新产品-冷板','新产品-开平板']
                             }
    # 拼货时各品种车上剩余最低重量限制（kg），即各品种的单件重量应都大于下面的值
    RG_COMMODITY_COMPOSE_LOW_WEIGHT = {'老区-型钢': 0,
                                       '老区-线材': 0,
                                       '老区-螺纹': 0,
                                       '老区-开平板': 0,
                                       '老区-卷板': 2000,
                                       '新产品-白卷': 1000,
                                       '新产品-卷板': 1000,
                                       '新产品-窄带': 0,
                                       '新产品-冷板': 0
                                       }
    # 摘单备注时的简写品种
    PICK_REMARK = {'老区-型钢': '型钢',
                   '老区-线材': '线材',
                   '老区-螺纹': '螺纹',
                   '老区-开平板': '开平板',
                   '老区-卷板': '黑卷',
                   '新产品-白卷': '白卷',
                   '新产品-白卷(热镀锌)': '白卷(热镀锌)',
                   '新产品-卷板': '黑卷',
                   '新产品-窄带': '窄带',
                   '新产品-窄带(木托窄带)': '窄带(木托窄带)',
                   '新产品-窄带(窄带卷)': '窄带(窄带卷)',
                   '新产品-冷板': '冷板'}
    RG_COMMODITY_GROUP_FOR_SQL = {'老区-型钢': ['型钢'],
                                  '老区-线材': ['线材'],
                                  '老区-螺纹': ['螺纹'],
                                  '老区-开平板': ['开平板'],
                                  '老区-卷板': ['黑卷', '白卷'],
                                  '新产品-白卷': ['白卷', '黑卷'],
                                  '新产品-卷板': ['白卷', '黑卷'],
                                  '新产品-窄带': ['窄带', '白卷'],
                                  '新产品-冷板': ['开平板', '冷板']
                                  }
    # 所有的车辆配件
    RG_FITTINGS_OF_VEHICLE = ['鞍座', '草垫子', '钢丝绳', '垫皮', '垫木', '汽线改装']
    # 各品种所需的配件
    RG_VARIETY_VEHICLE = {
        "老区-型钢": ["垫木", "垫皮", "钢丝绳"],
        "老区-线材": ["垫木"],
        "老区-螺纹": ["垫木"],
        "新产品-白卷": ["鞍座", "草垫子", "垫皮", "垫木"],
        "老区-卷板": ["鞍座", "草垫子", "垫皮", "垫木"],
        "新产品-卷板": ["鞍座", "草垫子", "垫皮", "垫木"],
        "新产品-窄带": ["钢丝绳", "垫皮", "垫木"],
        "新产品-冷板": ["钢丝绳"],
        "老区-开平板": ["垫木"]
    }
    RG_COMMODITY_LYG = ["老区-卷板", "新产品-卷板", "新产品-白卷"]
    # RG_PORT_NAME_END_LYG = ["泰州钢冉码头", "泰州华纳码头",
    #                         "常州钢材现货交易市场码头", "常州万都码头",
    #                         "常州新东港码头", "常州武进码头",
    #                         "无锡国联皋桥码头", "无锡国信码头"]
    RG_PORT_NAME_END_LYG = []

    RG_WAREHOUSE_GROUP = [
        ["P5", "P6", "P7", "P8"],
        ["B1", "B2", "E1", "E2", "E3", "E4", "E5", "F1", "F2", "H1", "T1",
         "X1", "X2", "Z1", "Z2", "Z4", "Z5", "Z8", "ZA", "ZC"],
        ["F10", "F20"]
    ]
    # RG_WAREHOUSE_GROUP_LIST = ["P5", "P6", "P7", "P8",
    #                            "B1", "B2", "E1", "E2", "E3", "E4", "E5", "F1", "F2", "H1", "T1",
    #                            "X1", "X2", "Z1", "Z2", "Z4", "Z5", "Z8", "ZA", "ZC",
    #                            "F10", "F20"]

    RG_WAREHOUSE_NAME = ["宝华", "厂内", "岚北港", "未知厂区"]
    # 摘单推送司机冷却期时间（小时）
    PICK_PROPELLING_COLD_HOUR = 6
    # 摘单推送司机上限倍数
    PICK_DRIVER_NUM_LIMIT = 10
    # 判断司机是否移动，20分钟内移动的最低距离限制（米）
    PICK_PROPELLING_DISTANCE_LIMIT = 1000
    # 各仓库最大车辆容纳数
    WAREHOUSE_WAIT_DICT = {
        'stock_name': ['B2', 'E1', 'E2', 'E3', 'E4', 'F1', 'F10', 'F2', 'F20', 'H1', 'P5', 'P6', 'P7', 'P8', 'T1',
                       'X1', 'X2', 'Z1', 'Z2', 'Z4', 'Z5', 'Z8', 'ZA', 'ZC'],
        'truck_count_std': [15, 10, 10, 10, 10, 10, 25, 30, 25, 15, 25, 25, 10, 15, 15, 15, 15, 15, 20, 15, 15, 15, 15,
                            15]
    }
    # 各仓库一般车辆容纳数
    SINGLE_WAREHOUSE_WAIT_DICT = {
        'B2': 15,
        'E1': 10,
        'E2': 10,
        'E3': 10,
        'E4': 10,
        'F1': 10,
        'F10': 25,
        'F2': 30,
        'F20': 25,
        'H1': 15,
        'P5': 25,
        'P6': 25,
        'P7': 10,
        'P8': 15,
        'T1': 15,
        'X1': 15,
        'X2': 15,
        'Z1': 15,
        'Z2': 20,
        'Z4': 15,
        'Z5': 15,
        'Z8': 15,
        'ZA': 15,
        'ZC': 15
    }
    # 各仓库当前查询到的车辆数（从out_stock_queue_dao中取值）
    SINGLE_NOW_WAREHOUSE_DICT = {
        'B2': 0,
        'E1': 0,
        'E2': 0,
        'E3': 0,
        'E4': 0,
        'F1': 0,
        'F10': 0,
        'F2': 0,
        'F20': 0,
        'H1': 0,
        'P5': 0,
        'P6': 0,
        'P7': 0,
        'P8': 0,
        'T1': 0,
        'X1': 0,
        'X2': 0,
        'Z1': 0,
        'Z2': 0,
        'Z4': 0,
        'Z5': 0,
        'Z8': 0,
        'ZA': 0,
        'ZC': 0
    }
    # 4个城市区县的编码
    RG_DISTRICT_CODE = {
        '济南市': '3701',
        '淄博市': '3703',
        '滨州市': '3716',
        '菏泽市': '3717'
        # '济南市历下区': '370102', '济南市市中区': '370103', '济南市槐荫区': '370104',
        # '济南市天桥区': '370105', '济南市历城区': '370112', '济南市长清区': '370113',
        # '济南市平阴县': '370124', '济南市济阳县': '370125', '济南市章丘区': '370181',
        # '济南市商河县': '370126',  # 济南市
        # '淄博市淄川区': '370302', '淄博市张店区': '370303', '淄博市博山区': '370304',
        # '淄博市临淄区': '370305', '淄博市周村区': '370306', '淄博市桓台县': '370321',
        # '淄博市高青县': '370322', '淄博市沂源县': '370323',  # 淄博市
        # '滨州市滨城区': '371602', '滨州市沾化区': '371603', '滨州市惠民县': '371621',
        # '滨州市阳信县': '371622', '滨州市无棣县': '371623', '滨州市博兴县': '371625',
        # '滨州市邹平县': '371626',  # 滨州市
        # '菏泽市牡丹区': '371702', '菏泽市定陶区': '371703', '菏泽市曹县': '371721',
        # '菏泽市单县': '371722', '菏泽市成武县': '371723', '菏泽市巨野县': '371724',
        # '菏泽市郓城县': '371725', '菏泽市鄄城县': '371726', '菏泽市东明县': '371728'  # 菏泽市
    }
    # 厂区编码
    RG_WAREHOUSE_CODE = {'宝华': '01', '厂内': '02', '岚北港': '03'}
    # 品种编码
    RG_COMMODITY_CODE = {'老区-型钢': '01',
                         '老区-线材': '02',
                         '老区-螺纹': '03',
                         '老区-开平板': '04',
                         '老区-卷板': '05',
                         '新产品-白卷': '06',
                         '新产品-卷板': '07',
                         '新产品-窄带': '08',
                         '新产品-冷板': '09'}
    # 标准车载最大重量
    STANDARD_MAX_WEIGHT = 33000
    # 背包重量下浮
    PACKAGE_LOWER_WEIGHT = 1000
    # 体积上限系数
    MAX_VOLUME = 1.18
    # 缺省值
    DEFAULT_VOLUME = 0.001
    # 分车次限制重量
    TRUCK_SPLIT_RANGE = 1000
    # 考虑体积的物资代码前缀
    ITEM_ID_DICT = {
        # 焊管
        '112': 22,
        '111': 16,
        '110': 20,
        '109': 34,
        '108': 34,
        '107': 34,
        '106': 34,
        '105': 34,
        # 热镀
        '212': 22,
        '211': 16,
        '210': 20,
        '209': 34,
        '208': 34,
        '207': 34,
        '206': 34,
        '205': 40,
        # QF热镀管
        '712': 22,
        '711': 16,
        '710': 20,
        '709': 34,
        '708': 34,
        '707': 34,
        '706': 34,
        '705': 40,
        # 螺旋焊管
        '501': 100,
        '502': 75,
        '503': 49,
        '504': 25,
        '505': 20,
        '506': 18,
        '507': 12,
        '508': 8,
        '509': 6,
    }

    # 成都彭州京华，定时、手动调接口生成摘单计划的标记
    CDPZJH_REQUEST_FLAG = 1

    PICK_LABEL_TYPE = {
        "L1": "运力池",
        "L2": "新司机",
        "L3": "常运流向",
        "L4": "常运品种",
        "L5": "活跃司机",
        "L6": "运力服务"
    }

    PICK_RG_LAT = {"日钢纬度": 35.1582116300}

    PICK_RG_LON = {"日钢经度": 119.3315992000}

    PICK_RESULT_TYPE = {
        "DEFAULT": 500,
        "DIST5": 5,
        "DIST10": 10,
        "DIST20": 20,
        "DIST30": 30,
        "DIST40": 40,
        "DIST50": 50
    }

    PICK_CONTINUE_TIME = {
        "MINUTE10": 10,
        "MINUTE15": 15,
        "MINUTE20": 20,
        "MINUTE25": 25,
        "MINUTE30": 30
    }
    PICK_TOTAL_WEIGHT = 40

    # 摘单调用的策略
    PICK_SELECT_TYPE = [
        "SJLY10",  # 按模型动态推荐
        "SJLY20",  # 装点附近司机
        "SJLY30",  # 人工设定司机池
        "SJLY40",  # 新司机优先
        "SJLY50"  # 定时查临近线路司机
    ]

    # 各区县活跃司机上限设置
    PICK_ACTIVE_DRIVER_NUM = {
        # 泰安市
        "岱岳区": 77,  # 384
        "泰山区": 10,  # 51
        "新泰市": 2,  # 9
        "肥城市": 3,  # 15
        "东平市": 3,  # 15

        # 青岛市
        "城阳区": 79,  # 395
        "黄岛区": 181,  # 907
        "胶州市": 108,  # 540
        "即墨区": 55,  # 278
        "李沧区": 3,  # 13
        "平度市": 2,  # 11
        "市北区": 1,  # 5
        "莱西市": 3,  # 16

        # 滨州市
        "博兴县": 21,  # 107
        "沾化区": 0,  # 0
        "滨城区": 1,  # 5
        "邹平市": 0,  # 1

        # 淄博市
        "周村区": 13,  # 65
        "张店区": 7,  # 35
        "淄川区": 5,  # 25
        "临淄区": 0,  # 21
        "沂源县": 0,  # 14
        "博山区": 3,  # 15
        "桓台县": 0,  # 1

        # 菏泽市
        "牡丹区": 3,  # 17
        "曹县": 1,  # 4
        "郓城县": 6,  # 30
        "定陶区": 0,  # 1

        # 济南市
        "历城区": 15,  # 73
        "槐荫区": 3,  # 15
        "天桥区": 3,  # 13
        "平阴县": 0,  # 0
        "长清区": 0,  # 0
        "章丘区": 3,  # 13
        "市中区": 1,  # 6

        # 济宁市
        "任城区": 0,  # 175
        "梁山县": 0,  # 144
        "微山县": 0,  # 71
        "曲阜市": 0,  # 1
        "嘉祥县": 0,  # 22
        "兖州区": 0,  # 29
        "邹城市": 0,  # 12
        "鱼台县": 0,  # 0
        "泗水县": 0,  # 4
        "汶上县": 0,  # 1
        # "市中区": 0,  # 0
        "市辖区": 0,  # 0
        "金乡县": 0  # 0
    }

    # 使用摘单功能的对象
    PICK_OBJECT = {
        "PO1": "日钢省内汇好运单车",
        "PO2": "成都管厂"
    }

    # 是用摘单功能的对象（详细）
    PICK_COMPANY_CONFIG = {
        "PCC1": ["C000062070", "020"],  # 汇好运单车
        "PCC2": ["C000000888", "001"]  # 成都管厂
    }


def set_singleGoodsAllocation_model_config():
    """
    从数据表中获取singleGoodsAllocation项目的参数配置，说明：https://docs.qq.com/doc/DRExZZ0VqZlNHT1Zi
    :return:
    """
    '''
    注意：【这里有坑】一旦从数据库中配置了ModelConfig中相关属性的值之后，ModelConfig中的值就会被改变，并且暂存起来直到下次再启动程序，
    就算将数据库中配置的数据给删除了，原来配置的值也还会被保留在变量中，下次拿到的还是上次的值。因此在将数据库中的配置的数据删除之前，先将
    其值修改为ModelConfig中配置的默认值，并且在程序至少运行运行一次后再将其值删除（分布式中，不同机器上值不一样？）。对于ModelConfig
    中默认没有数据的值，在读配置表的时候先将其值设为没有数据的，如果表中有数据再用表中数据更新。一旦在配置表中配置了ModelConfig中某个变
    量的值后，就算使用默认配置中一样的数据，也不建议将表中数据删除掉。
    '''
    # 获取参数配置字典
    model_config = get_single_model_config_service()
    # 各仓库最大车辆容纳数
    ModelConfig.WAREHOUSE_WAIT_DICT = model_config.get('WAREHOUSE_WAIT_DICT', ModelConfig.WAREHOUSE_WAIT_DICT)
    # 各仓库一般车辆容纳数
    ModelConfig.SINGLE_WAREHOUSE_WAIT_DICT = model_config.get('SINGLE_WAREHOUSE_WAIT_DICT',
                                                              ModelConfig.SINGLE_WAREHOUSE_WAIT_DICT)
    # 超期清理的时间下限(小时)
    ModelConfig.OVER_TIME_LOW_HOUR = model_config.get('OVER_TIME_LOW_HOUR', ModelConfig.OVER_TIME_LOW_HOUR)
    # 超期清理的时间上限(小时)
    ModelConfig.OVER_TIME_UP_HOUR = model_config.get('OVER_TIME_UP_HOUR', ModelConfig.OVER_TIME_UP_HOUR)
    # 拼货时各品种车上剩余最低重量限制（kg）：对数据库中配置的做更新操作，没配的还是默认
    if model_config.get('RG_COMMODITY_COMPOSE_LOW_WEIGHT', {}):
        for key in model_config.get('RG_COMMODITY_COMPOSE_LOW_WEIGHT').keys():
            ModelConfig.RG_COMMODITY_COMPOSE_LOW_WEIGHT[key] = model_config['RG_COMMODITY_COMPOSE_LOW_WEIGHT'][key]
    # 单车分货时最多匹配结果数量的一个阈值上限
    ModelConfig.RG_SINGLE_COMPOSE_MAX_LEN = model_config.get('RG_SINGLE_COMPOSE_MAX_LEN',
                                                             ModelConfig.RG_SINGLE_COMPOSE_MAX_LEN)
    # 单车分货中优先级的价值
    ModelConfig.SINGLE_VALUE_OF_PRIORITY = model_config.get('SINGLE_VALUE_OF_PRIORITY',
                                                            ModelConfig.SINGLE_VALUE_OF_PRIORITY)
    # 单车分货中卸点客户的价值
    ModelConfig.SINGLE_VALUE_OF_CONSUMER = model_config.get('SINGLE_VALUE_OF_CONSUMER',
                                                            ModelConfig.SINGLE_VALUE_OF_CONSUMER)
    # 单车分货中装点仓库的价值
    ModelConfig.SINGLE_VALUE_OF_DELIWARE = model_config.get('SINGLE_VALUE_OF_DELIWARE',
                                                            ModelConfig.SINGLE_VALUE_OF_DELIWARE)
    # 单车分货中装点仓库效率的价值:各仓库默认一般车辆容纳数、仓库作业效率放大的比例、联储仓库被扣减的价值
    ModelConfig.SINGLE_VALUE_OF_DELIWARE_EFFICIENCY = model_config.get('SINGLE_VALUE_OF_DELIWARE_EFFICIENCY',
                                                                       ModelConfig.SINGLE_VALUE_OF_DELIWARE_EFFICIENCY)
    # 单车分货中装点厂区的价值
    ModelConfig.SINGLE_VALUE_OF_FACTORY = model_config.get('SINGLE_VALUE_OF_FACTORY',
                                                           ModelConfig.SINGLE_VALUE_OF_FACTORY)
    # 单车分货中载重的价值
    ModelConfig.SINGLE_VALUE_OF_WEIGHT = model_config.get('SINGLE_VALUE_OF_WEIGHT',
                                                          ModelConfig.SINGLE_VALUE_OF_WEIGHT)
    # 单车分货中订单的价值
    ModelConfig.SINGLE_VALUE_OF_ORDER_NUM = model_config.get('SINGLE_VALUE_OF_ORDER_NUM',
                                                             ModelConfig.SINGLE_VALUE_OF_ORDER_NUM)
    # 单车分货中额外添加的价值
    ModelConfig.SINGLE_VALUE_OF_EXTRA = model_config.get('SINGLE_VALUE_OF_EXTRA',
                                                         ModelConfig.SINGLE_VALUE_OF_EXTRA)
    # 使用优化版本的城市
    ModelConfig.SINGLE_USE_OPTIMAL_CITY = model_config.get('SINGLE_USE_OPTIMAL_CITY')
    # 配载无结果后进行拆件配载的城市：支持全部，只要其中包含全部，就是全部城市
    ModelConfig.SINGLE_SUB_STOWAGE_CITY = model_config.get('SINGLE_SUB_STOWAGE_CITY', [])
    # 需要按备注指定客户的城市
    ModelConfig.SINGLE_DESIGNATE_CONSUMER_CITY = model_config.get('SINGLE_DESIGNATE_CONSUMER_CITY',
                                                                  ModelConfig.SINGLE_DESIGNATE_CONSUMER_CITY)
    # 是否严格按照调度备注指定的客户进行筛选：0：完全按照指定的客户筛选，没货不推荐；1：先按照指定的客户筛选，没货后放宽条件，开其他客户的货
    ModelConfig.SINGLE_DESIGNATE_CONSUMER_FLAG = model_config.get('SINGLE_DESIGNATE_CONSUMER_FLAG',
                                                                  ModelConfig.SINGLE_DESIGNATE_CONSUMER_FLAG)
    # 单车分货中非生产用来存储货物的仓库
    ModelConfig.SINGLE_STORAGE_DELIWARE = model_config.get('SINGLE_STORAGE_DELIWARE',
                                                           ModelConfig.SINGLE_STORAGE_DELIWARE)
    # 外贸对应的入库仓库
    ModelConfig.RG_FOREIGN_TRADE_DELIWARE = model_config.get('RG_FOREIGN_TRADE_DELIWARE',
                                                             ModelConfig.RG_FOREIGN_TRADE_DELIWARE)
    # 件重大于此值的优先排到前面配货
    ModelConfig.SINGLE_BIG_PIECE_WEIGHT = model_config.get('SINGLE_BIG_PIECE_WEIGHT',
                                                           ModelConfig.SINGLE_BIG_PIECE_WEIGHT)
    # 按流向只发哪些客户的货
    ModelConfig.SINGLE_KEEP_CONSUMER = model_config.get('SINGLE_KEEP_CONSUMER')
    # 按流向不发哪些客户的货
    ModelConfig.SINGLE_REJECT_CONSUMER = model_config.get('SINGLE_REJECT_CONSUMER')
    # 不使用推荐开单的（流向、车队）：['连云港市,连云区,源运物流', '连云港市,连云区,全部', '连云港市,全部,全部']
    ModelConfig.SINGLE_BLACK_LIST = model_config.get('SINGLE_BLACK_LIST')
    # 相同的单子被删除多少次后将被锁定
    ModelConfig.SINGLE_NUM_LOCK = model_config.get('SINGLE_NUM_LOCK', ModelConfig.SINGLE_NUM_LOCK)
    # 相同的单子被删除多少次后将被锁定的时间：小时
    ModelConfig.SINGLE_LOCK_HOUR = model_config.get('SINGLE_LOCK_HOUR', ModelConfig.SINGLE_LOCK_HOUR)
    # 被删除后需要锁定的单子 是否需要筛掉：1筛掉，0不筛掉
    ModelConfig.SINGLE_LOCK_ORDER_FLAG = model_config.get('SINGLE_LOCK_ORDER_FLAG', ModelConfig.SINGLE_LOCK_ORDER_FLAG)
    # 被删除后需要锁定的单子：发货通知单号、订单号、出库仓库
    ModelConfig.SINGLE_LOCK_ORDER = model_config.get('SINGLE_LOCK_ORDER', ModelConfig.SINGLE_LOCK_ORDER)


def set_model_config():
    """
    从数据表中获取模型的参数配置，说明：https://docs.qq.com/doc/DRExZZ0VqZlNHT1Zi
    :return:
    """
    # 获取参数配置字典
    model_config = get_model_config_service()
    # FLAG标记：1读取表中的配置；0：使用默认配置
    if model_config.get('FLAG', 0):
        # 各城市的发运量限制
        ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT = model_config.get('CITY_DISPATCH_WEIGHT_LIMIT_DICT',
                                                                       ModelConfig.CITY_DISPATCH_WEIGHT_LIMIT_DICT)
        # 每条摘单计划的最大车次数限制
        ModelConfig.PICK_TRUCK_NUM_UP_LIMIT = model_config.get('PICK_TRUCK_NUM_UP_LIMIT',
                                                               ModelConfig.PICK_TRUCK_NUM_UP_LIMIT)
        # 相同客户配置
        ModelConfig.CONSUMER_DICT = model_config.get('CONSUMER_DICT', ModelConfig.CONSUMER_DICT)
        # 厂区仓库配置
        # 宝华
        ModelConfig.RG_WAREHOUSE_GROUP[0] = model_config.get('RG_WAREHOUSE_GROUP', {}
                                                             ).get('宝华', ModelConfig.RG_WAREHOUSE_GROUP[0])
        # 厂内
        ModelConfig.RG_WAREHOUSE_GROUP[1] = model_config.get('RG_WAREHOUSE_GROUP', {}
                                                             ).get('厂内', ModelConfig.RG_WAREHOUSE_GROUP[1])
        # 岚北港
        ModelConfig.RG_WAREHOUSE_GROUP[2] = model_config.get('RG_WAREHOUSE_GROUP', {}
                                                             ).get('岚北港', ModelConfig.RG_WAREHOUSE_GROUP[2])
        # 调度人员联系方式
        if model_config.get('DISPATCHER_PHONE_DICT', {}):
            # 更新数据表中配置的城市
            for city_key in model_config['DISPATCHER_PHONE_DICT'].keys():
                ModelConfig.DISPATCHER_PHONE_DICT[city_key] = model_config['DISPATCHER_PHONE_DICT'][city_key]
        # 载重上限
        ModelConfig.RG_MAX_WEIGHT = model_config.get('RG_MAX_WEIGHT', ModelConfig.RG_MAX_WEIGHT)
        # 载重下限
        ModelConfig.RG_MIN_WEIGHT = model_config.get('RG_MIN_WEIGHT', ModelConfig.RG_MAX_WEIGHT)
        # 使用遗传算法的标志
        ModelConfig.GA_USE_FLAG = model_config.get('GA_USE_FLAG', ModelConfig.GA_USE_FLAG)
        # 使用遗传算法的结果作为输出的标志
        ModelConfig.GA_USE_RESULT_FLAG = model_config.get('GA_USE_RESULT_FLAG', ModelConfig.GA_USE_RESULT_FLAG)

        # 遗传中迭代的次数、交叉的次数
        ModelConfig.GA_PARAM = model_config.get('GA_PARAM', ModelConfig.GA_PARAM)
        # 遗传算法中车次数减少1的价值、尾货的价值
        ModelConfig.GA_FITNESS_VALUE_PARAM = model_config.get('GA_FITNESS_VALUE_PARAM',
                                                              ModelConfig.GA_FITNESS_VALUE_PARAM)
        # 遗传算法中卸点客户的价值
        ModelConfig.GA_FITNESS_VALUE_CONSUMER = model_config.get('GA_FITNESS_VALUE_CONSUMER',
                                                                 ModelConfig.GA_FITNESS_VALUE_CONSUMER)
        # 遗传算法中装点仓库的价值
        ModelConfig.GA_FITNESS_VALUE_DELIWARE = model_config.get('GA_FITNESS_VALUE_DELIWARE',
                                                                 ModelConfig.GA_FITNESS_VALUE_DELIWARE)
        # 遗传算法中装点厂区的价值
        ModelConfig.GA_FITNESS_VALUE_FACTORY = model_config.get('GA_FITNESS_VALUE_FACTORY',
                                                                ModelConfig.GA_FITNESS_VALUE_FACTORY)
