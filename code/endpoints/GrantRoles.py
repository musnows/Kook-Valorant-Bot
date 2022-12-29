import json
import time
from khl import Bot,Message,PublicMessage,Event
from khl.card import Card, CardMessage, Element, Module, Types

# 预加载文件
with open("./log/color_idsave.json", 'r', encoding='utf-8') as frcl:
    ColorIdDict = json.load(frcl)

with open("./config/color_emoji.json", 'r', encoding='utf-8') as fremoji:
    EmojiDict = json.load(fremoji)

#将获取当前时间封装成函数方便使用
def GetTime():  
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

# 用于记录使用表情回应获取ID颜色的用户
def save_userid_color(userid: str, emoji: str):
    global ColorIdDict
    flag = 0
    # 需要先保证原有dict里面没有保存该用户的id，才进行追加
    if userid in ColorIdDict.keys():
        flag = 1  #因为用户已经回复过表情，将flag置为1
        return flag
    #原有txt内没有该用户信息，进行追加操作
    ColorIdDict[userid] = emoji
    with open("./log/color_idsave.json", 'w', encoding='utf-8') as fw2:
        json.dump(ColorIdDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

    return flag


# 在不改代码的前提下修改监听服务器和监听消息，并保存到文件
async def Color_SetGm(msg:Message,Card_Msg_id: str):
    global EmojiDict  #需要声明全局变量
    EmojiDict['guild_id'] = msg.ctx.guild.id
    EmojiDict['msg_id'] = Card_Msg_id
    await msg.reply(f"颜色监听服务器更新为 {EmojiDict['guild_id']}\n监听消息更新为 {EmojiDict['msg_id']}\n")
    with open("./log/color_emoji.json", 'w', encoding='utf-8') as fw2:
        json.dump(EmojiDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)


# 给用户上角色
async def Color_GrantRole(bot:Bot,event:Event):
    g = await bot.client.fetch_guild(EmojiDict['guild_id'])  # 填入服务器id
    #将msg_id和event.body msg_id进行对比，确认是我们要的那一条消息的表情回应
    if event.body['msg_id'] == EmojiDict['msg_id']:
        now_time = GetTime()  #记录时间
        print(f"[{now_time}] React:{event.body}")  # 这里的打印eventbody的完整内容，包含emoji_id

        channel = await bot.client.fetch_public_channel(event.body['channel_id'])  #获取事件频道
        s = await bot.client.fetch_user(event.body['user_id'])  #通过event获取用户id(对象)
        # 判断用户回复的emoji是否合法
        emoji = event.body["emoji"]['id']
        if emoji in EmojiDict['data']:
            ret = save_userid_color(event.body['user_id'], event.body["emoji"]['id'])  # 判断用户之前是否已经获取过角色
            if ret == 1:  #已经获取过角色
                await bot.client.send(channel, f'你已经设置过你的ID颜色啦！修改要去找管理员哦~', temp_target_id=event.body['user_id'])
                return
            else:
                role = int(EmojiDict['data'][emoji])
                await g.grant_role(s, role)
                await bot.client.send(channel, f'阿狸已经给你上了 {emoji} 对应的颜色啦~', temp_target_id=event.body['user_id'])
        else: #回复的表情不合法
            await bot.client.send(channel, f'你回应的表情不在列表中哦~再试一次吧！', temp_target_id=event.body['user_id'])



# 设置角色的消息，bot会自动给该消息添加对应的emoji回应作为示例表情
async def Color_SetMsg(bot:Bot,msg:Message):
    cm = CardMessage()
    c1 = Card(Module.Header('在下面添加回应，来设置你的id颜色吧！'), Module.Context('五颜六色等待上线...'))
    c1.append(Module.Divider())
    c1.append(Module.Section('「:pig:」粉色  「:heart:」红色\n「:black_heart:」黑色  「:yellow_heart:」黄色\n'))
    c1.append(Module.Section('「:blue_heart:」蓝色  「:purple_heart:」紫色\n「:green_heart:」绿色  「:+1:」默认\n'))
    cm.append(c1)
    sent = await msg.ctx.channel.send(cm)  #接受send的返回值
    # 自己new一个msg对象
    setMSG = PublicMessage(msg_id=sent['msg_id'],
                           _gate_=msg.gate,
                           extra={
                               'guild_id': msg.ctx.guild.id,
                               'channel_name': msg.ctx.channel,
                               'author': {
                                   'id': bot.me.id
                               }
                           })
    # extra部分留空也行
    # 让bot给卡片消息添加对应emoji回应
    for emoji in EmojiDict['data']:
        await setMSG.add_reaction(emoji)