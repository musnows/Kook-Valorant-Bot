import os
import copy
import time
import traceback
from pyg2plot import Plot
from khl import Bot,Message
from ..utils.file.Files import BotUserDict,_log
from ..utils import Gtime
from ..utils.log import BotLog
from ..Admin import is_admin

SHOW_DAYS = 31
"""显示最近多少天的数据"""
WEB_ROOT_PATH  = "./web/ahri"
"""html文件的根路径，末尾不能带/"""
WEB_PAGE_PATH = ["gu","ngu"]
"""html页面文件的路径，末尾不能带/，不存在会创建"""

def create_web_path():
    """新建web路径"""
    if (not os.path.exists(WEB_ROOT_PATH)):
        os.makedirs(WEB_ROOT_PATH)  # 文件夹不存在，创建
        _log.info(f"[plugins] create web path {WEB_ROOT_PATH}")
    for path in WEB_PAGE_PATH:
        cur = f"{WEB_ROOT_PATH}/{path}"
        if (not os.path.exists(cur)):
            os.makedirs(cur)  # 文件夹不存在，创建
            _log.info(f"[plugins] create web path {path}")

def init(bot:Bot):
    """初始化之前，机器人会判断根路径是否存在，不在则创建文件夹
    - bot:Bot
    """
    create_web_path()
    
    async def data_manamge(key:str)->list:
        """处理日志文件中，服务器/用户/命令的数据
        Args(key):
        - init_time: 获取服务器/用户日增量的数据
        - used_time: 获取服务器/用户/命令日使用量的数据
        """
        data_list = []
        # 获取的是初始化时间
        if key == 'init_time':
            for g,ginfo in BotUserDict["guild"]["data"].items():
                date = Gtime.get_date_from_stamp(ginfo[key]) # 获取可读日期
                # 插入服务器
                flag = True
                for i in data_list:
                    if date == i['date'] and i['category']=="guild":
                        i['num']+=1 # 有相同日期的，计数器+1
                        flag = False
                        break
                # 没有相同日期的，才新建键值
                if flag:
                    data_list.append({"date":date,"category":'guild','num':1,'time':ginfo[key]})
            # 插入用户
            for u,uinfo in BotUserDict['user']['data'].items():
                # 用户记录的时间是可读时间，直接取出前几位就是日期22-10-02
                date = uinfo[key][:8]
                flag = True
                for i in data_list:
                    if date == i['date'] and i['category']=="user":
                        i['num']+=1
                        flag = False
                        break
                # 没有相同日期的，才新建键值
                if flag:
                    data_list.append({"date":date,"category":'user','num':1,'time':Gtime.get_time_stamp_from_str(uinfo[key])})
        # 如果是used_time，需要处理每日的命令/服务器/用户数量
        elif key == 'used_time':
            for d in BotUserDict['cmd']['data']:# 命令
                num = BotUserDict['cmd']['data'][d]
                data_list.append({"date":d,"category":'command','num':num,'time':Gtime.get_time_stamp_from_str(d)})
            for d in BotUserDict['cmd']['user']:# 用户
                num = len(BotUserDict['cmd']['user'][d]) # 长度就是用户数量
                data_list.append({"date":d,"category":'user','num':num,'time':Gtime.get_time_stamp_from_str(d)})
            for d in BotUserDict['cmd']['guild']:# 服务器
                num = len(BotUserDict['cmd']['guild'][d])
                data_list.append({"date":d,"category":'guild','num':num,'time':Gtime.get_time_stamp_from_str(d)})
        # 依照日期排序
        data_list = sorted(data_list,key=lambda kv: kv['date'])
        return data_list
    
    
    async def render_ngu_web(exp_raise = False):
        """渲染用户/服务器增量网页
        - exp_raise: 是否要重新抛出异常
        """
        try:
            # 获取处理好的数据
            guild_list = await data_manamge('init_time')
            # 获取上个月的时间戳，只显示最近30天的时间，将之前的删除掉
            last_month_time = time.time() - 86400 * SHOW_DAYS
            guild_list_tmp = copy.deepcopy(guild_list)
            for i in guild_list_tmp:
                if i['time'] < last_month_time :
                    guild_list.remove(i)
            # 网页参数
            line = Plot("Line")
            line.page_title = '服务器-用户-增长图 | Kook-Valorant-Bot'
            line.set_options({
                "appendPadding": 40,
                "data": guild_list,
                "xField": "date",
                "yField": "num",
                "label": {},
                'seriesField': 'category',
                "smooth": True,
                "lineStyle": {
                    "lineWidth": 3,
                }
            })
            # 生成html文件
            line.render(f"{WEB_ROOT_PATH}/ngu/index.html")
            _log.info(f"render new guild/user status web")
        except Exception as result:
            _log.exception("Error occur")
            if exp_raise:raise result

    async def render_guc_web(exp_raise = False):
        """渲染用户/服务器/命令使用情况的网页
        - exp_raise: 是否要重新抛出异常
        """
        try:
            # 获取处理好的数据
            guild_list = await data_manamge('used_time')
            # 获取上个月的时间戳，只显示最近30天的时间，将之前的删除掉
            last_month_time = time.time() - 86400 * SHOW_DAYS
            guild_list_tmp = copy.deepcopy(guild_list)
            for i in guild_list_tmp:
                if i['time'] < last_month_time :
                    guild_list.remove(i)
            # 网页参数
            line = Plot("Line")
            line.page_title = '机器人-活跃用户图 | Kook-Valorant-Bot'
            line.set_options({
                "appendPadding": 40,
                "data": guild_list,
                "xField": "date",
                "yField": "num",
                "label": {},
                'seriesField': 'category',
                "smooth": True,
                "lineStyle": {
                    "lineWidth": 3,
                }
            })
            # 生成html文件
            line.render(f"{WEB_ROOT_PATH}/gu/index.html")
            _log.info(f"render guild/user/cmd status web")
        except Exception as result:
            _log.exception("Error occur")
            if exp_raise:raise result

    @bot.task.add_cron(hour="0",timezone='Asia/Shanghai')
    async def update_web_task():
        try:
            _log.info("web update begin")
            await render_ngu_web()
            await render_guc_web()
            _log.info("web update success")
        except:
            _log.exception("Error occur")

    @bot.command(name='upd-web',case_sensitive=False)
    async def update_web_cmd(msg:Message):
        BotLog.log_msg(msg)
        try:
            if not is_admin(msg.author_id):
                return
            await render_ngu_web(True)
            await render_guc_web(True)
            await msg.reply(f"网页更新成功")
        except:
            await msg.reply(f"网页渲染出现错误\n```\n{traceback.format_exc()}```\n")
    
    _log.info("[plugins] load StatusWeb.py")