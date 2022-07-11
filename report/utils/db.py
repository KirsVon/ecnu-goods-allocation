import pymysql
import pandas as pd

def get_con(env='production'):
    if env == 'production':
        MYSQL_HOST = 'am-bp117g8ua37t2f4vh90650.ads.aliyuncs.com'
        MYSQL_PORT = 3306
        MYSQL_USER = 'sc_prod_read'
        MYSQL_PASSWD = 'UiPtdC!0720'
        MYSQL_DB = 'db_ods'
        MYSQL_CHARSET = 'utf8'
    elif env == 'test':
        MYSQL_HOST = 'am-bp16yam2m9jqm2tyk90650.ads.aliyuncs.com'
        MYSQL_PORT = 3306
        MYSQL_USER = 'modeluser'
        MYSQL_PASSWD = 'eSod!0615'
        MYSQL_DB = 'db_dw'
        MYSQL_CHARSET = 'utf8'
    else:
        raise Exception(env)

    conn = pymysql.connect(
        host = MYSQL_HOST,
        port = MYSQL_PORT,
        user = MYSQL_USER,
        password = MYSQL_PASSWD,
        database = MYSQL_DB,
        charset = MYSQL_CHARSET)
    return conn


def pd_sel(sql, env='production'):
    con = get_con(env)

    try:
        df_data = pd.read_sql(sql, con)
    finally:
        con.close()

    return df_data

def sel_one(sql, env='production'):
    con = get_con(env)

    try:
        cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        dict_data = cursor.fetchone()
    finally:
        if cursor: cursor.close()
        con.close()

    return dict_data


if __name__ == '__main__':
    pass

