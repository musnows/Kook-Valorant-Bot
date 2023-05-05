import io
import copy
import random
import traceback
import time
from datetime import datetime, timedelta
from khl import (Bot, Event, EventTypes, Message, PrivateMessage, requester, Channel)
from khl.card import Card, CardMessage, Element, Module, Types, Struct
from PIL import Image, UnidentifiedImageError  # 用于合成图片

#用来存放roll的频道/服务器/回应用户的dict
from ..utils.file.Files import VipShopBgDict, VipRollDcit, VipUserDict, VipAuthLog,_log
from ..utils.log import BotLog
from ..utils.Gtime import getTime
from ..utils import BotVip,ShopImg
from ..utils.KookApi import icon_cm,get_card,upd_card,get_card_msg

VIP_BG_SIZE = 4
"""vip用户背景图片数量限制"""

def init(bot:Bot,bot_upd_img:Bot,master_id:str,debug_ch:Channel,cm_send_test:Channel):
    """- bot 主机器人
    - bot_upd_img 用来上传图片的机器人
    - master_id 机器人主人用户id
    - debug_ch 用于发送debug信息的文字频道
    - cm_send_test 用于发送图片测试的文字频道
    """
    # 新建vip的uuid，第一个参数是天数，第二个参数是数量
    @bot.command(name="vip-a")
    async def get_vip_uuid(msg: Message, day: int = 30, num: int = 10):
        BotLog.logMsg(msg)
        try:
            if msg.author_id == master_id:
                text = await BotVip.create_vip_uuid(num, day)
                cm = CardMessage()
                c = Card(Module.Header(f"已生成新的uuid   数量:{num}  天数:{day}"),
                        Module.Divider(),
                        Module.Section(Element.Text(text, Types.Text.KMD)),
                        color='#e17f89')
                cm.append(c)
                await msg.reply(cm)
                _log.info("vip-a | create_vip_uuid reply successful!")
            else:
                await msg.reply("您没有权限操作此命令！")
        except Exception as result:
            await BotLog.BaseException_Handler("vip-a", traceback.format_exc(), msg)


    # 兑换vip
    @bot.command(name="vip-u", aliases=['兑换'])
    async def buy_vip_uuid(msg: Message, uuid: str = 'err', *arg):
        BotLog.logMsg(msg)
        if uuid == 'err':
            await msg.reply(f"只有输入vip的兑换码才可以操作哦！uuid: `{uuid}`")
            return
        try:
            #把bot传过去是为了让阿狸在有人成兑换激活码之后发送消息到log频道
            ret = await BotVip.using_vip_uuid(msg, uuid, bot, debug_ch)
        except Exception as result:
            await BotLog.BaseException_Handler("vip-u", traceback.format_exc(), msg, debug_send=debug_ch)


    # 看vip剩余时间
    @bot.command(name="vip-c")
    async def check_vip_timeremain(msg: Message, *arg):
        BotLog.logMsg(msg)
        try:
            if not await BotVip.vip_ck(msg):
                return
            # 获取时间
            ret_t = BotVip.vip_time_remain(msg.author_id)
            ret_cm = await BotVip.vip_time_remain_cm(ret_t)
            await msg.reply(ret_cm)
        except Exception as result:
            await BotLog.BaseException_Handler("vip-c", traceback.format_exc(), msg, debug_send=debug_ch)


    # 看vip用户列表
    @bot.command(name="vip-l")
    async def list_vip_user(msg: Message, *arg):
        BotLog.logMsg(msg)
        try:
            if msg.author_id == master_id:
                text = await BotVip.fetch_vip_user()
                cm2 = CardMessage()
                c = Card(Module.Header(f"当前vip用户列表如下"), color='#e17f89')
                c.append(Module.Section(Element.Text(f"```\n{text}```", Types.Text.KMD)))
                cm2.append(c)
                await msg.reply(cm2)
            else:
                await msg.reply("您没有权限操作此命令！")
        except Exception as result:
            await BotLog.BaseException_Handler("vip-l", traceback.format_exc(), msg)


    @bot.command(name="vip-shop")
    async def vip_shop_bg_set(msg: Message, icon: str = "err", *arg):
        BotLog.logMsg(msg)
        if icon != 'err' and ('http' not in icon or '](' not in icon):
            await msg.reply(f"请提供正确的图片url！\n当前：`{icon}`")
            return

        x3 = "[None]"
        cm = CardMessage()
        try:
            if not await BotVip.vip_ck(msg):
                return
            
            if icon != 'err': # 不为空且走到这里了，代表通过了对icon参数是否为http链接的检查
                user_ind = (msg.author_id in VipShopBgDict['bg']) # 判断当前用户在不在dict中
                if user_ind and len(VipShopBgDict['bg'][msg.author_id]["background"]) >= VIP_BG_SIZE:
                    cm = await get_card_msg(f"当前仅支持保存{VIP_BG_SIZE}个自定义图片", "您可用「/vip-shop-d 图片编号」删除已有图片再添加", icon_cm.that_it)
                    await msg.reply(cm)
                    return

                # 提取图片url
                x1 = icon.find('](')
                x2 = icon.find(')', x1 + 2)
                x3 = icon[x1 + 2:x2]
                _log.info(f"Au:{msg.author_id} get_url | {x3}")
                try:
                    # 检查图片链接格式是否支持
                    if ('png' not in x3) and ('jpg' not in x3) and ('jpeg' not in x3):
                        text = f"您当前上传的图片格式不支持！请上传png/jpg/jpeg格式的图片"
                        cm = await get_card_msg(text, "请优先尝试png格式图片，其余格式兼容性有一定问题", icon_cm.ahri_dark)
                        await msg.reply(cm)
                        _log.info(f"Au:{msg.author_id} | img_type_not support")
                        return
                    #打开图片(测试)
                    bg_vip = Image.open(io.BytesIO(await ShopImg.img_requestor(x3)))
                except UnidentifiedImageError as result:
                    err_str = f"ERR! [{getTime()}] vip_shop_imgck\n```\n{result}\n```"
                    _log.error(err_str)
                    await msg.reply(f"图片违规！请重新上传\n{err_str}")
                    return

                #到插入的时候再创建list，避免出现图片没有通过检查，但是list又被创建了的情况
                if not user_ind:
                    VipShopBgDict['bg'][msg.author_id] = {}
                    VipShopBgDict['bg'][msg.author_id]["background"] = list()
                    #新建用户，但是有可能已经缓存了默认的背景图片，所以状态为false（重画）
                    VipShopBgDict['bg'][msg.author_id]["status"] = False
                #插入图片
                VipShopBgDict['bg'][msg.author_id]["background"].append(x3)

            cm = await BotVip.get_vip_shop_bg_cm(msg)
            #先让测试bot把这个卡片发到频道，如果发出去了说明json没有问题
            await bot_upd_img.client.send(cm_send_test, cm)
            _log.info(f"Au:{msg.author_id} | cm_send_test success")
            #然后阿狸在进行回应
            await msg.reply(cm)

            # 打印用户新增的图片日后用于排错
            _log.info(f"Au:{msg.author_id} img add | {x3}")

        except requester.HTTPRequester.APIRequestFailed as result:
            await BotLog.APIRequestFailed_Handler("vip_shop", traceback.format_exc(), msg, bot, cm)
            VipShopBgDict['bg'][msg.author_id]["background"].remove(x3)  #删掉里面的图片
            _log.error(f"Au:{msg.author_id} | remove({x3})")
        except Exception as result:
            await BotLog.BaseException_Handler("vip_shop", traceback.format_exc(), msg)


    @bot.command(name="vip-shop-s")
    async def vip_shop_bg_set_s(msg: Message, num: str = "err", *arg):
        BotLog.logMsg(msg)
        if num == 'err':
            await msg.reply(f"请提供正确的图片序号！\n当前：`{num}`")
            return
        cm = CardMessage()
        try:
            global VipShopBgDict
            if not await BotVip.vip_ck(msg):
                return
            if msg.author_id not in VipShopBgDict['bg']:
                await msg.reply("您尚未自定义商店背景图！")
                return

            num = int(num) # type: ignore
            assert isinstance(num,int)
            if num < len(VipShopBgDict['bg'][msg.author_id]["background"]):
                try:  #打开用户需要切换的图片
                    bg_vip = Image.open(
                        io.BytesIO(await ShopImg.img_requestor(VipShopBgDict['bg'][msg.author_id]["background"][num])))
                except UnidentifiedImageError as result:
                    err_str = f"ERR! [{getTime()}] vip_shop_s_imgck\n```\n{result}\n```"
                    await msg.reply(f"图片违规！请重新上传\n{err_str}")
                    await BotVip.replace_illegal_img(msg.author_id, num)  #替换图片
                    _log.exception("Exception occur")
                    return
                # 图片检查通过，交换两个图片的位置
                icon_num = VipShopBgDict['bg'][msg.author_id]["background"][num]
                VipShopBgDict['bg'][msg.author_id]["background"][num] = VipShopBgDict['bg'][msg.author_id]["background"][0]
                VipShopBgDict['bg'][msg.author_id]["background"][0] = icon_num
                VipShopBgDict['bg'][msg.author_id]['status'] = False
                #修改图片之后，因为8点bot存储了商店图，所以需要重新获取 以新的背景图为背景 的商店图片
            else:
                await msg.reply("请提供正确返回的图片序号，可以用`/vip-shop`进行查看")
                return

            cm = await BotVip.get_vip_shop_bg_cm(msg)
            #先让测试bot把这个卡片发到频道，如果发出去了说明json没有问题
            await bot_upd_img.client.send(cm_send_test, cm)
            _log.info(f"Au:{msg.author_id} | cm_send_test success")
            #然后阿狸在进行回应
            await msg.reply(cm)

            _log.info(f"Au:{msg.author_id} | switch to [{VipShopBgDict['bg'][msg.author_id]['background'][0]}]")
        except requester.HTTPRequester.APIRequestFailed as result:
            await BotLog.APIRequestFailed_Handler("vip_shop_s", traceback.format_exc(), msg, bot, cm)
        except Exception as result:
            await BotLog.BaseException_Handler("vip_shop_s", traceback.format_exc(), msg)


    @bot.command(name="vip-shop-d")
    async def vip_shop_bg_set_d(msg: Message, num: str = "err", *arg):
        BotLog.logMsg(msg)
        if num == 'err':
            await msg.reply(f"请提供正确的图片序号！\n当前：`{num}`")
            return
        cm = CardMessage()
        try:
            if not await BotVip.vip_ck(msg):
                return
            if msg.author_id not in VipShopBgDict['bg']:
                await msg.reply("您尚未自定义商店背景图！")
                return

            num = int(num) # type: ignore
            assert isinstance(num,int)
            if num < len(VipShopBgDict['bg'][msg.author_id]["background"]) and num > 0:
                # 删除图片
                del_img_url = VipShopBgDict['bg'][msg.author_id]["background"][num]
                del VipShopBgDict['bg'][msg.author_id]["background"][num]
            elif num == 0:
                await msg.reply("不支持删除当前正在使用的背景图！")
                return
            else:
                await msg.reply("请提供正确返回的图片序号，可以用`/vip-shop`进行查看")
                return

            cm = await BotVip.get_vip_shop_bg_cm(msg)
            #先让测试bot把这个卡片发到频道，如果发出去了说明json没有问题
            await bot_upd_img.client.send(cm_send_test, cm)
            _log.info(f"Au:{msg.author_id} | cm_send_test success")
            #然后阿狸在进行回应
            await msg.reply(cm)

            _log.info(f"Au:{msg.author_id} | delete [{del_img_url}]")
        except requester.HTTPRequester.APIRequestFailed as result:
            await BotLog.APIRequestFailed_Handler("vip_shop_d", traceback.format_exc(), msg, bot, cm)
        except Exception as result:
            await BotLog.BaseException_Handler("vip_shop_d", traceback.format_exc(), msg)


    # 判断消息的emoji回应，并记录id
    @bot.on_event(EventTypes.ADDED_REACTION)
    async def vip_roll_log(b: Bot, event: Event):
        global VipRollDcit
        if event.body['msg_id'] not in VipRollDcit:
            return
        else:
            user_id = event.body['user_id']
            # 把用户id添加到list中
            log_str = f"[vip-roll-log] Au:{user_id} roll_msg:{event.body['msg_id']}"
            if user_id not in VipRollDcit[event.body['msg_id']]['user']:
                VipRollDcit[event.body['msg_id']]['user'].append(user_id)
                channel = await bot.client.fetch_public_channel(event.body['channel_id'])
                await bot.client.send(channel, f"[添加回应]->抽奖参加成功！", temp_target_id=event.body['user_id'])
                log_str += " Join"  #有join的才是新用户

            _log.info(log_str)


    # 开启一波抽奖
    @bot.command(name='vip-r', aliases=['vip-roll'])
    async def vip_roll(msg: Message, vday: int = 7, vnum: int = 5, rday: float = 1.0):
        BotLog.logMsg(msg)
        try:
            if msg.author_id != master_id:
                await msg.reply(f"您没有权限执行本命令")
                return
            # 设置开始抽奖
            global VipRollDcit
            cm = BotVip.roll_vip_start(vnum, vday, rday)
            roll_ch = await bot.client.fetch_public_channel(msg.ctx.channel.id)
            roll_send = await bot.client.send(roll_ch, cm)
            VipRollDcit[roll_send['msg_id']] = {  # type: ignore
                'time': time.time() + rday * 86400,
                'nums': vnum,
                'days': vday,
                'channel_id': msg.ctx.channel.id,
                'guild_id': msg.ctx.guild.id,
                'user': []
            }
            _log.info(f"card message send | C:{msg.ctx.channel.id}")
        except:
            await BotLog.BaseException_Handler("vip-r", traceback.format_exc(), msg)


    @bot.task.add_interval(seconds=80)
    async def vip_roll_task():
        global VipRollDcit, VipUserDict
        viprolldict_temp = copy.deepcopy(VipRollDcit)  #临时变量用于修改
        log_str = ''
        for msg_id, minfo in viprolldict_temp.items():
            if time.time() < minfo['time']:
                continue
            else:
                _log.info(f"[BOT.TASK] vip_roll_task msg:{msg_id}")
                vday = VipRollDcit[msg_id]['days']  # vip天数
                vnum = VipRollDcit[msg_id]['nums']  # 奖品数量
                # 结束抽奖
                log_str = f"```\n[MsgID] {msg_id}\n"
                send_str = "恭喜 "
                # 人数大于奖品数量
                if len(VipRollDcit[msg_id]['user']) > vnum:
                    ran = random.sample(range(0, len(VipRollDcit[msg_id]['user'])), vnum)  # 生成n个随机数
                else:  # 生成一个从0到len-1的列表 如果只有一个用户，生成的是[0]
                    ran = list(range(len(VipRollDcit[msg_id]['user'])))
                # 开始遍历
                for j in ran:
                    user_id = VipRollDcit[msg_id]['user'][j]
                    user = await bot.client.fetch_user(user_id)
                    # 设置用户的时间和个人信息
                    time_vip = BotVip.vip_time_stamp(user_id, vday)
                    VipUserDict[user_id] = {'time': time_vip, 'name_tag': f"{user.username}#{user.identify_num}"}
                    # 创建卡片消息
                    cm = CardMessage()
                    c = Card(
                        Module.Section(Element.Text("恭喜您中奖阿狸vip了！", Types.Text.KMD),
                                    Element.Image(src=icon_cm.ahri_kda2, size='sm')))
                    c.append(Module.Context(Element.Text(f"您抽中了{vday}天vip，可用/vhelp查看vip权益", Types.Text.KMD)))
                    c.append(
                        Module.Countdown(datetime.now() + timedelta(seconds=BotVip.vip_time_remain(user_id)),
                                        mode=Types.CountdownMode.DAY))
                    c.append(Module.Divider())
                    c.append(
                        Module.Section('加入官方服务器，即可获得「阿狸赞助者」身份组',
                                    Element.Button('来狸', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
                    cm.append(c)
                    await user.send(cm)
                    log_str += f"[vip-roll] Au:{user_id} get [{vday}]day-vip\n"
                    send_str += f"(met){user_id}(met) "

                log_str += "```"
                send_str += "获得了本次奖品！"
                await bot.client.send(debug_ch, log_str)  #发送此条抽奖信息的结果到debug
                #发送结果到抽奖频道
                roll_ch = await bot.client.fetch_public_channel(VipRollDcit[msg_id]['channel_id'])
                cm1 = CardMessage()
                c = Card(Module.Header(f"🎊 阿狸vip {VipRollDcit[msg_id]['days']}天体验卡 🎊"),
                        Module.Section(Element.Text(send_str, Types.Text.KMD)),
                        Module.Context(Element.Text(f"本次抽奖结束，奖励已私信发送", Types.Text.KMD)))
                cm1.append(c)
                await bot.client.send(roll_ch, cm1)
                del VipRollDcit[msg_id]  #删除此条抽奖信息

        # 更新抽奖列表(如果有变化)
        if viprolldict_temp != VipRollDcit:
            _log.info(log_str)  # 打印中奖用户作为log


    # 给所有vip用户添加时间，避免出现某些错误的时候浪费vip时间
    @bot.command(name='vip-ta')
    async def vip_time_add(msg: Message, vday: int = 1, *arg):
        BotLog.logMsg(msg)
        if msg.author_id != master_id:
            await msg.reply(f"您没有权限执行此命令！")
            return
        try:
            global VipUserDict
            # 给所有vip用户上天数
            for vip, vinfo in VipUserDict.items():
                time_vip = BotVip.vip_time_stamp(vip, vday)
                VipUserDict[vip]['time'] = time_vip

            await msg.reply(f"操作完成，已给所有vip用户增加 `{vday}` 天时长")
            _log.info(f"[vip_time_add] update VipUserDict")
        except:
            err_str = f"ERR! [{getTime()}] vip_time_add\n```\n{traceback.format_exc()}\n```"
            await msg.reply(f"{err_str}")
            _log.exception("Exception occur")


    
    async def check_vip_img():
        """检查vip提供的背景图有么有问题（有问题会被kook封掉）"""
        _log.info("[BOT.TASK] check_vip_img start!")
        try:
            global VipShopBgDict
            cm0 = CardMessage()
            c = Card(color='#fb4b57')  #卡片侧边栏颜色
            text = f"您设置的vip背景图违规！请尽快替换"
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.powder, size='sm')))
            c.append(Module.Context(Element.Text("多次发送违禁图片会导致阿狸被封，请您慎重选择图片！", Types.Text.KMD)))
            #遍历vip用户的图片
            log_str_user = "[BOT.TASK] check_vip_img Au:"
            for vip_user, vip_bg in VipShopBgDict['bg'].items():
                user = await bot.client.fetch_user(vip_user)
                sz = len(vip_bg["background"])
                i = 0
                while i < sz:
                    try:
                        bg_test = Image.open(io.BytesIO(await ShopImg.img_requestor(vip_bg["background"][i])))
                        i += 1
                    except UnidentifiedImageError as result:
                        err_str = f"ERR! [{getTime()}] checking [{vip_user}] img\n```\n{result}\n"
                        #把被ban的图片替换成默认的图片，打印url便于日后排错
                        err_str += f"[UnidentifiedImageError] url={vip_bg['background'][i]}\n```"
                        c.append(Module.Section(Element.Text(err_str, Types.Text.KMD)))
                        cm0.append(c)
                        await user.send(cm0)  # 发送私聊消息给用户
                        await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道
                        vip_bg["background"][i] = BotVip.illegal_img_169  #修改成16比9的图片
                        vip_bg["status"] = False  #需要重新加载图片
                        _log.error(err_str)
                    except Exception as result:
                        err_str = f"ERR! [{getTime()}] checking[{vip_user}]img\n```\n{traceback.format_exc()}\n```"
                        _log.error(err_str)
                        c.append(Module.Section(Element.Text(err_str, Types.Text.KMD)))
                        cm0.append(c)
                        await user.send(cm0)
                        await bot.client.send(debug_ch, err_str)

                # 遍历完一个用户后打印结果
                log_str_user += f"({vip_user})"

            #所有用户成功遍历后，写入文件
            _log.info(log_str_user)
            _log.info("[BOT.TASK] check_vip_img finished!")
        except Exception as result:
            err_str = f"ERR! [{getTime()}] check_vip_img\n```\n{traceback.format_exc()}\n```"
            _log.exception("Exception occur")
            await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道


    #因为这个功能很重要，所以设置成可以用命令调用+定时任务
    @bot.task.add_cron(hour=3, minute=0, timezone="Asia/Shanghai")
    async def check_vip_img_task():
        await check_vip_img()


    @bot.command(name="vip-img")
    async def check_vip_img_cmd(msg: Message, *arg):
        BotLog.logMsg(msg)
        if msg.author_id == master_id:
            await check_vip_img()
            await msg.reply("背景图片diy检查完成！")
        else:
            return await msg.reply("您没有权限执行此命令！")