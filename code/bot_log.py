import json
import time
import traceback
from khl import Message, PrivateMessage
from endpoints import guild_list, guild_view

# 用户数量的记录文件
with open('./log/BotUserLog.json', 'r', encoding='utf-8') as f:
    BotUserDict = json.load(f)

#将获取当前时间封装成函数方便使用
def GetTime():  
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

# 保存用户的log文件
# 因为logging的使用很频繁，所以不需要经常保存
def log_bot_save():
    with open("./log/BotUserLog.json", 'w', encoding='utf-8') as fw2:
        json.dump(BotUserDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

# 记录用户信息
def log_bot_user(user_id:str,guild_id:str,time):
    global BotUserDict
    BotUserDict['cmd_total']+=1
    # 服务器不存在，新的用户服务器
    if guild_id not in BotUserDict['data']:
        BotUserDict['data'][guild_id] = {} #不能连续创建两个键值！
        BotUserDict['data'][guild_id]['user'] = {}
        BotUserDict['data'][guild_id]['user'][user_id] = time
        BotUserDict['user_total'] += 1
        log_bot_save()
        return "GNAu"
    # 服务器存在，新用户
    elif user_id not in BotUserDict['data'][guild_id]['user']:
        BotUserDict['data'][guild_id]['user'][user_id] = time
        BotUserDict['user_total'] += 1
        log_bot_save()
        return "NAu"
    # 旧用户更新执行命令的时间，但是不保存文件
    else:
        BotUserDict['data'][guild_id]['user'][user_id] = time
        return "Au"

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    try:
        now_time = GetTime()
        if isinstance(msg, PrivateMessage):
            print(
                f"[{now_time}] PrivateMessage - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}"
            )
        else:
            Ustr = log_bot_user(msg.author_id,msg.ctx.guild.id,now_time) # 记录服务器和用户
            print(
                f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - {Ustr}:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}"
            )
    except:
        err_str = f"ERR! [{GetTime()}] logging\n```\n{traceback.format_exc()}\n```"
        print(err_str)

# bot用户记录dict处理
async def log_bot_list(msg:Message):
    global BotUserDict
    try:
        # 加入的服务器数量，api获取
        Glist = await guild_list()
        Glist = Glist['data']['meta']['total']
        # api正常返回结果，赋值给全局变量
        BotUserDict['guild_total'] = Glist
        # dict里面保存的服务器，有用户活跃的服务器数量
        BotUserDict['guild_active'] = len(BotUserDict['data'])
        # 遍历列表，获取服务器名称
        for gu in BotUserDict['data']:
            if 'name' not in BotUserDict['data'][gu]:
                Gret = await guild_view(gu)
                BotUserDict['data'][gu]['name'] = Gret['data']['name']
            else:
                continue
        # 保存文件
        log_bot_save()
        print("[log_bot_list] file handling finish, return BotUserDict")
        return BotUserDict
    except:
        err_str = f"ERR! [{GetTime()}] log-list\n```\n{traceback.format_exc()}\n```"
        await msg.reply(f"{err_str}")
        print(err_str)