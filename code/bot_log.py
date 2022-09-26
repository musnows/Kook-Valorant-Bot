import json
import time
from khl import Message, PrivateMessage


# 用户数量的记录文件
with open('./log/BotUserLog.json', 'r', encoding='utf-8') as f:
    BotUserDict = json.load(f)

#将获取当前时间封装成函数方便使用
def GetTime():  
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

# 保存用户的log文件
# 因为logging的使用很频繁，所以不需要经常保存
def log_bot_user_save():
    with open("./log/BotUserLog.json", 'w', encoding='utf-8') as fw2:
        json.dump(BotUserDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

# 记录用户信息
def log_bot_user(user_id:str,time):
    global BotUserDict
    # 新用户的时候保存用户记录文件
    if user_id not in BotUserDict:
        BotUserDict[user_id]={}
        BotUserDict[user_id]['init']=time
        BotUserDict[user_id]['last']=time
        log_bot_user_save()
        return "NAu"
    else:# 旧用户更新执行命令的时间，但是不保存文件
        BotUserDict[user_id]['last']=time
        return "Au"

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = GetTime()
    Ustr = log_bot_user(msg.author_id,now_time) # 记录用户id
    if isinstance(msg, PrivateMessage):
        print(
            f"[{now_time}] PrivateMessage - {Ustr}:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}"
        )
    else:
        print(
            f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - {Ustr}:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}"
        )

# bot用户数量
def log_bot_user_len():
    return len(BotUserDict)