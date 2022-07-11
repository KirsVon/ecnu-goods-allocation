# #发货能力Dao zby
# from app.main.steel_factory.entity.t_send_ability import T_send_ability
# from app.util.base.base_dao import BaseDao
# from model_config import ModelConfig
#
#
# class TSendAbilityDao(BaseDao):
#     def select_T_send_ability(self,city):
#         """
#         查询库存
#         :return:
#         """
#
#         sql = """
#         SELECT
#             *
#         FROM
#             db_model.t_send_ability
#         WHERE
#             city='{}'
#         """
#         sql = sql.format(city)
#
#         data = self.select_all(sql)
#         return data
#
#     def update_T_send_ability(self,detail_address,now_send):
#         sql="""
#             update  db_model.t_send_ability set now_send='{}'
#             where detail_address = '{}'
#
#         """
#         sql = sql.format(now_send,detail_address)
#         self.execute(sql)
#
# t_send_ability_dao = TSendAbilityDao()
