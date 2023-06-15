# 本文件将帮助您将 kook-valorant-bot v1.2.x 版本的 json 数据转为 sqlite3 存储
# 目前正在进行 sqlite3 数据库重构；除了部分比较难转换的，和从api下载下来用来当缓存的文件外

import sqlite3, json, time
import traceback

from pkg.utils.log.Logging import _log
from pkg.utils.file import Files
from pkg.utils import Gtime

DB_NAME = './ahri.db'
"""数据库名"""


class TB_SQL:
    """创建表的sql语句"""
    USER_TB_CREATE = "CREATE TABLE IF NOT EXISTS user(\
                        user_id TEXT NOT NULL UNIQUE,\
                        user_name TEXT DEFAULT NULL,\
                        game_nick TEXT DEFAULT NULL,\
                        color_id TEXT DEFAULT NULL,\
                        vip_upto TIMESTAMP DEFAULT 0,\
                        update_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')),\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """用户"""
    VIP_TB_CREATE = "CREATE TABLE IF NOT EXISTS vip_user(\
                        user_id TEXT NOT NULL UNIQUE,\
                        vip_upto TIMESTAMP DEFAULT 0,\
                        update_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')),\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """VIP用户表
    - 由于测试过的单开一张表，查询时间差距过小，所以不使用这个表
    """
    VIP_SHOP_BG_CREATE = "CREATE TABLE IF NOT EXISTS vip_shop_bg(\
                        user_id TEXT NOT NULL UNIQUE,\
                        bg_img TEXT DEFAULT NULL,\
                        cache_status DEFAULT false,\
                        update_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')),\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """VIP用户背景图片配置表"""
    VIP_SHOP_CACAHE_CREATE = "CREATE TABLE IF NOT EXISTS vip_shop_cache(\
                        riot_uuid TEXT NOT NULL UNIQUE,\
                        shop_img TEXT NOT NULL,\
                        update_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')),\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """VIP用户背景图片缓存表"""
    VIP_TOKEN_CREATE = "CREATE TABLE IF NOT EXISTS vip_token(\
                        token TEXT NOT NULL UNIQUE,\
                        is_prime BOOLEAN DEFAULT false,\
                        is_avali BOOLEAN DEFAULT true,\
                        user_id TEXT DEFAULT NULL,\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """vip token"""
    CMD_TB_CREATE = "CREATE TABLE IF NOT EXISTS cmd(\
                        user_id TEXT NOT NULL,\
                        guild_id TEXT NOT NULL,\
                        channel_id TEXT NOT NULL,\
                        cmd TEXT NOT NULL,\
                        date TEXT(8) NOT NULL,\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """CMD
    - cmd表是用来替代BotUserLog.json，但是该文件太复杂了，所以暂时还是继续用json吧
    """
    USER_AUTH_CREATE = "CREATE TABLE IF NOT EXISTS auth_user(\
                        user_id TEXT NOT NULL UNIQUE,\
                        riot_uuid TEXT DEFAULT NULL,\
                        acpw_log TEXT DEFAULT NULL,\
                        update_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')),\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """user auth 记录
    - 包含VIP的登录记录（kook用户id+游戏uuid）
    - riot_uuid：json list，存放拳头游戏uuid列表
    - acpw_log：json dict，账户密码登录记录，包含使用账户密码登录的时间和登录的账户
    """
    API_AUTH_CREATE = "CREATE TABLE IF NOT EXISTS auth_api(\
                        key TEXT NOT NULL UNIQUE,\
                        riot_uuid TEXT DEFAULT NULL,\
                        acpw_log TEXT DEFAULT NULL,\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """api auth 记录
    - 包含api的登录记录（用作标识的key+游戏uuid）当前用拳头账户来做key
    - riot_uuid：只有一个，账户对应的uuid，为了保证设计唯一性，采用[uuid]方式存放
    - acpw_log：json dict，账户密码登录记录，包含使用账户密码登录的时间和登录的账户（目前是留空，后续可能会使用）
    """
    API_TOKEN_CREATE = "CREATE TABLE IF NOT EXISTS api_token(\
                        token TEXT NOT NULL UNIQUE,\
                        days NUMERIC NOT NULL,\
                        is_prime BOOLEAN DEFAULT false,\
                        used_sum NUMERIC DEFAULT 0,\
                        od_time TIMESTAMP NOT NULL,\
                        used_time TIMESTAMP DEFAULT NULL,\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """api token
    - days: 有效天数
    - od_time: 过期时间戳
    - used_time: 最近一次使用的时间
    """
    SKIN_NOTIFY_CREATE = "CREATE TABLE IF NOT EXISTS skin_notify(\
                        user_id TEXT NOT NULL UNIQUE,\
                        skin_uuid TEXT DEFAULT NULL,\
                        banned_time TIMESTAMP DEFAULT 0,\
                        update_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')),\
                        insert_time TIMESTAMP DEFAULT (datetime('now', '+8 hours')));"
    """皮肤提醒
    - skin_uuid: 皮肤uuid-list
    - banned_time: 是否因为异常操作被ban？（评论出现过分的关键词）被ban了时间戳不为0
    """


class INSERT_SQL:
    """插入信息的sql语句"""
    INSERT_USER_SQL = "insert into user (user_id,game_nick,color_id,vip_upto) values (?,?,?,?);"
    """插入用户"""
    INSERT_VIP_SQL = "insert into vip_user (user_id,vip_upto) values (?,?);"
    """插VIP用户"""
    INSERT_SHOP_BG_SQL = "insert into vip_shop_bg (user_id,bg_img,cache_status) values (?,?,?);"
    """插入vip用户的商店背景图"""
    INSERT_SHOP_CACHE_SQL = "insert into vip_shop_cache (riot_uuid,shop_img,update_time) values (?,?,?);"
    """插入商店图片缓存"""
    INSERT_VIP_TOKEN_SQL = "insert into vip_token (token,is_prime,is_avali,user_id) values (?,?,?,?);"
    """VIP TOKEN"""
    INSERT_API_TOKEN_SQL = "insert into api_token (token,days,is_prime,used_sum,od_time,used_time) values (?,?,?,?,?,?);"
    """API TOKEN"""


def vip_check(user_id: str):
    """是否vip，是vip则返回到期时间；不是返回0"""
    cur_time = time.time()
    if user_id not in Files.VipUserDict:
        return 0
    # 是否是vip还需要判断时间戳是否过期，当前时间小于过期时间，没有过期
    elif (cur_time < Files.VipUserDict[user_id]['time']):
        return Files.VipUserDict[user_id]['time']
    return 0


def insert_user_game_nick(db: sqlite3.Connection):
    """遍历游戏名列表"""
    query = db.cursor()
    for user_id, game_nick in Files.GameIdDict.items():
        SELECT_USER_SQL = f"select * from user where user_id='{user_id}';"
        if query.execute(SELECT_USER_SQL).rowcount != 0:  # 数据库中已有
            continue  # 跳过
        color_id = None if user_id not in Files.ColorIdDict else Files.ColorIdDict[user_id]
        is_vip = vip_check(user_id)
        query.execute(INSERT_SQL.INSERT_USER_SQL, (user_id, game_nick, color_id, is_vip))
        db.commit()
    _log.info("[处理完毕] 游戏名列表")


def insert_user_color_id(db: sqlite3.Connection):
    """遍历color_id列表"""
    query = db.cursor()
    for user_id, color_id in Files.ColorIdDict.items():
        SELECT_USER_SQL = f"select * from user where user_id='{user_id}';"
        if query.execute(SELECT_USER_SQL).rowcount != 0:  # 数据库中已有
            continue  # 跳过
        game_nick = None if user_id not in Files.GameIdDict else Files.GameIdDict[user_id]
        is_vip = vip_check(user_id)
        query.execute(INSERT_SQL.INSERT_USER_SQL, (user_id, game_nick, color_id, is_vip))
        db.commit()
    _log.info("[处理完毕] color_id列表")


def insert_user_vip(db: sqlite3.Connection):
    """遍历vip用户列表"""
    query = db.cursor()
    for user_id, vinfo in Files.VipUserDict.items():
        SELECT_USER_SQL = f"select * from user where user_id='{user_id}';"
        if query.execute(SELECT_USER_SQL).rowcount != 0:  # 数据库中已有
            continue  # 跳过
        is_vip = vip_check(user_id)
        game_nick = None if user_id not in Files.GameIdDict else Files.GameIdDict[user_id]
        color_id = None if user_id not in Files.ColorIdDict else Files.ColorIdDict[user_id]
        query.execute(INSERT_SQL.INSERT_USER_SQL, (user_id, game_nick, color_id, is_vip))
        db.commit()
        # if is_vip:
        #     query.execute(INSERT_VIP_SQL,(user_id,vinfo['time']))
        #     db.commit()
    _log.info("[处理完毕] vip用户列表")


def select_user_test(db: sqlite3.Connection):
    """测试用户/vip用户查询速度；经过测试，速度差距不大，暂时不分表"""
    query = db.cursor()
    user_list = ["2003185237", "3032082901"]  # 测试用例
    # 在用户表里面查询
    start_time = time.time()
    for u in user_list:
        ret = query.execute(f"select * from user where user_id='{u}';")
    end_time = time.time()
    _log.info('user', end_time - start_time)
    # 在vip用户表里面查询
    start_time = time.time()
    for u in user_list:
        ret = query.execute(f"select * from vip_user where user_id='{u}';")
    end_time = time.time()
    _log.info('vip_user', end_time - start_time)


def insert_shop_bg(db: sqlite3.Connection):
    """插入vip用户商店的背景图"""
    query = db.cursor()
    for user in Files.VipShopBgDict['bg']:
        status = Files.VipShopBgDict['bg'][user]['status']
        bg_list = json.dumps(Files.VipShopBgDict['bg'][user]['background'])  # 转str
        query.execute(INSERT_SQL.INSERT_SHOP_BG_SQL, (user, bg_list, status))
        db.commit()
    _log.info("[处理完毕] vip商店背景图列表")


def insert_shop_cache(db: sqlite3.Connection):
    query = db.cursor()
    for riot_uuid in Files.VipShopBgDict['cache']:
        # 排除之前的遗留数据（key是kook的用户id）
        if '-' not in riot_uuid:
            continue
        shop_img = Files.VipShopBgDict['cache'][riot_uuid]['cache_img']
        cache_time = Files.VipShopBgDict['cache'][riot_uuid]['cache_time']
        query.execute(INSERT_SQL.INSERT_SHOP_CACHE_SQL, (riot_uuid, shop_img, cache_time))
        db.commit()
    _log.info("[处理完毕] vip商店缓存列表")


def insert_vip_token(db: sqlite3.Connection):
    query = db.cursor()
    for token,info in Files.VipUuidDict.items():
        is_prime = info['prime']
        status = info['status']
        user_id = None if 'user_id' not in info else info['user_id']
        query.execute(INSERT_SQL.INSERT_VIP_TOKEN_SQL, (token, is_prime, status,user_id))
        db.commit()
    _log.info("[处理完毕] vip token")

def insert_api_token(db: sqlite3.Connection):
    query = db.cursor()
    for token,info in Files.ApiTokenDict['data'].items():
        query.execute(INSERT_SQL.INSERT_API_TOKEN_SQL, (token, 
                                                        info['days'],
                                                        info['prime'],
                                                        info['sum'],
                                                        info['od_time'],
                                                        info['last_used']))
        db.commit()
    _log.info("[处理完毕] api token")


if __name__ == '__main__':
    try:
        _log.info("start  sqlite3 transfer")

        # 0.先创建数据库中的表(如果表不存在才创建)
        db = sqlite3.connect(DB_NAME)
        """数据库连接"""
        query = db.cursor()
        query.execute(TB_SQL.USER_TB_CREATE)  # 用户表
        query.execute(TB_SQL.VIP_SHOP_BG_CREATE)  # 商店背景图表
        query.execute(TB_SQL.VIP_SHOP_CACAHE_CREATE)  # 商店缓存表
        query.execute(TB_SQL.VIP_TOKEN_CREATE)  # vip-token表
        query.execute(TB_SQL.API_AUTH_CREATE)  # api-auth记录
        query.execute(TB_SQL.USER_AUTH_CREATE)  # user-auth记录
        query.execute(TB_SQL.API_TOKEN_CREATE)  # api-token表
        query.execute(TB_SQL.SKIN_NOTIFY_CREATE)  # 皮肤评价表
        db.commit()  # 执行

        # 1.插入用户 user 数据
        insert_user_game_nick(db)
        insert_user_color_id(db)
        insert_user_vip(db)
        # select_user_test(db)

        # 2.插入vip背景图和缓存
        insert_shop_cache(db)
        insert_shop_bg(db)

        # 3.插入token表
        insert_api_token(db)
        insert_vip_token(db)

        # 4.插入auth表

        # 5.插入皮肤评价表

        db.close()  # 关闭
        _log.info('finish sqlite3 transfer')
    except:
        _log.exception('err in sqlite3 transfer')