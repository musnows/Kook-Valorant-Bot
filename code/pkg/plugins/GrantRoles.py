import json
import aiohttp
import traceback
from khl import Bot, Message, PublicMessage, Event,EventTypes
from khl.card import Card, CardMessage, Element, Module, Types

# 预加载文件
from ..utils.file.Files import SponsorDict, ColorIdDict, EmojiDict,_log
from ..utils.KookApi import kook_headers
from ..utils.Gtime import get_time
from ..utils.log import BotLog
from ..Admin import is_admin


def save_userid_color(userid: str, emoji: str):
    """用于记录使用表情回应获取ID颜色的用户"""
    global ColorIdDict
    flag = 0
    # 需要先保证原有dict里面没有保存该用户的id，才进行追加
    if userid in ColorIdDict.keys():
        flag = 1  #因为用户已经回复过表情，将flag置为1
        return flag
    #原有txt内没有该用户信息，进行追加操作
    ColorIdDict[userid] = emoji
    return flag


async def color_guild_msg_send(msg: Message, card_msg_id: str):
    """在不改代码的前提下修改监听服务器和监听消息，并保存到文件"""
    global EmojiDict  #需要声明全局变量
    EmojiDict['guild_id'] = msg.ctx.guild.id
    EmojiDict['msg_id'] = card_msg_id
    await msg.reply(f"颜色监听服务器更新为 {EmojiDict['guild_id']}\n监听消息更新为 {EmojiDict['msg_id']}\n")


async def color_grant_role(bot: Bot, event: Event):
    """给用户上角色"""
    g = await bot.client.fetch_guild(EmojiDict['guild_id'])  # 填入服务器id
    #将msg_id和event.body msg_id进行对比，确认是我们要的那一条消息的表情回应
    if event.body['msg_id'] == EmojiDict['msg_id']:
        _log.info(f"React: {event.body}")  # 这里的打印eventbody的完整内容，包含emoji_id

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
        else:  #回复的表情不合法
            await bot.client.send(channel, f'你回应的表情不在列表中哦~再试一次吧！', temp_target_id=event.body['user_id'])


async def color_set_msg(bot: Bot, msg: Message):
    """设置角色的消息，bot会自动给该消息添加对应的emoji回应作为示例表情"""
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


#########################################感谢助力者#########################################

def check_sponsor(it: dict):
    """检查文件中是否有这个助力者的id"""
    global SponsorDict
    flag = 0
    # 需要先保证原有txt里面没有保存该用户的id，才进行追加
    if it['id'] in SponsorDict.keys():
        flag = 1
        return flag

    #原有txt内没有该用户信息，进行追加操作
    SponsorDict[it['id']] = it['nickname']

    return flag


async def thanks_sponser(bot: Bot, kook_header=kook_headers):
    """调用api检查并感谢助力者"""
    _log.info("[BOT.TASK] thanks_sponser start!")
    #在api链接重需要设置服务器id和助力者角色的id，目前这个功能只对KOOK最大valorant社区生效
    api = f"https://www.kaiheila.cn/api/v3/guild/user-list?guild_id={EmojiDict['guild_id']}&role_id={EmojiDict['sp_role_id']}"
    async with aiohttp.ClientSession() as session:
        async with session.post(api, headers=kook_header) as response:
            json_dict = json.loads(await response.text())

    #长度相同无需更新
    sz = len(SponsorDict)
    if json_dict['data']['meta']['total'] == sz:
        _log.info(f"[BOT.TASK] No new sponser, same_len [{sz}]")
        return

    for its in json_dict['data']['items']:
        if check_sponsor(its) == 0:
            channel = await bot.client.fetch_public_channel("8342620158040885")  #发送感谢信息的文字频道
            await bot.client.send(channel, f"感谢 (met){its['id']}(met) 对本服务器的助力")
            _log.info(f"[%s] 感谢{its['nickname']}对本服务器的助力" % get_time())
    _log.info("[BOT.TASK] thanks_sponser finished!")


#############################################################################################


def init(bot:Bot):
    """bot: main bot"""
    # 在不修改代码的前提下设置上色功能的服务器和监听消息
    @bot.command(name='Color-Set-GM', case_sensitive=False)
    async def color_set_gm_cmd(msg: Message, card_msg_id: str):
        try:
            BotLog.log_msg(msg)
            if is_admin(msg.author_id):
                await color_guild_msg_send(msg, card_msg_id)
        except:
            await BotLog.base_exception_handler("Color-Set-GM",traceback.format_exc(),msg)

    # 判断消息的emoji回应，并给予不同角色
    @bot.on_event(EventTypes.ADDED_REACTION)
    async def grant_roles_event(b: Bot, event: Event):
        try:
            await color_grant_role(b, event)
        except:
            _log.exception(f"Err in grant_roles")
    
    @bot.command(name='Color-Set', case_sensitive=False)
    async def color_set_msg_cmd(msg: Message):
        """给用户上色功能的消息（在发出消息后，机器人自动添加回应）"""
        try:
            BotLog.log_msg(msg)
            if is_admin(msg.author_id):
                await color_set_msg(bot, msg)
        except:
            await BotLog.base_exception_handler("Color-Set",traceback.format_exc(),msg)

    # # 感谢助力者（每天19点进行检查）
    # @bot.task.add_cron(hour=19, minute=0, timezone="Asia/Shanghai")
    # async def thanks_sponser_task():
    #     await thanks_sponser(bot)