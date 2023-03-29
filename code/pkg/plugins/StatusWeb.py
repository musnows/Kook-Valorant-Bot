import copy
import time
import traceback
from pyg2plot import Plot
from khl import Bot,Message
from ..utils.file.Files import BotUserDict,_log
from ..utils import Gtime
from ..utils.log import BotLog

SHOW_DAYS = 31
"""显示最近多少天的数据"""


def init(bot:Bot,master_id:str):
    async def data_manamge():
        guild_list = []
        user_dict = {}
        for g,ginfo in BotUserDict["guild"]["data"].items():
            lt = []
            for u in ginfo['user']:
                tis = Gtime.getTimeStampFromStr(ginfo['user'][u])
                lt.append(tis) # 当前服务器用户使用命令的时间戳
                # 插入用户，必须要用户不存在dict中，或者时间比dict中的小才能添加
                if u in user_dict and tis >= user_dict[u]:
                    continue
                user_dict[u] = tis
            # 获取lt中时间的最小值，即服务器第一个使用命令的用户的时间，可以认为是服务器的初始化时间
            min_time = min(lt)
            date = Gtime.getDateFromStamp(min_time) # 获取可读日期
            # 插入服务器
            flag = True
            for i in guild_list:
                if date == i['date'] and i['category']=="guild":
                    i['num']+=1 # 有相同日期的，计数器+1
                    flag = False
                    break
            # 没有相同日期的，才新建键值
            if flag:
                guild_list.append({"date":date,"category":'guild','num':1,'time':min_time})
        # 插入用户
        for u in user_dict:
            date = Gtime.getDateFromStamp(user_dict[u])
            flag = True
            for i in guild_list:
                if date == i['date'] and i['category']=="user":
                    i['num']+=1
                    flag = False
                    break
            # 没有相同日期的，才新建键值
            if flag:
                guild_list.append({"date":date,"category":'user','num':1,'time':user_dict[u]})
        # 依照日期排序
        guild_list = sorted(guild_list,key=lambda kv: kv['date'])
        return guild_list
    
    async def render_gu_web(exp_raise = False):
        """渲染用户/服务器增量网页
        - exp_raise: 是否要重新抛出异常
        """
        try:
            # 获取处理好的数据
            guild_list = await data_manamge()
            # 获取上个月的时间戳，只显示最近30天的时间，将之前的删除掉
            last_month_time = time.time() - 86400 * SHOW_DAYS
            guild_list_tmp = copy.deepcopy(guild_list)
            for i in guild_list_tmp:
                if i['time'] < last_month_time :
                    guild_list.remove(i)
            # 网页参数
            line = Plot("Line")
            line.page_title = '服务器-用户-增长图 | Kook阿狸机器人'
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
            line.render("./web/ahri/gu/index.html")
            _log.info(f"render guild/user status web")
        except Exception as result:
            _log.exception("Error occur")
            if exp_raise:raise result

    @bot.task.add_cron(hour="0",timezone='Asia/Shanghai')
    async def update_web_task():
        try:
            _log.info("web update begin")
            await render_gu_web()
            _log.info("web update success")
        except:
            _log.exception("Error occur")

    @bot.command(name='upd-web',case_sensitive=False)
    async def update_web_cmd(msg:Message):
        BotLog.logMsg(msg)
        try:
            if msg.author_id !=master_id:
                return
            await render_gu_web(True)
        except:
            await msg.reply(f"网页渲染出现错误\n```\n{traceback.format_exc()}```\n")
    