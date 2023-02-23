import copy
import uuid
import time
import traceback
import io
from PIL import Image,UnidentifiedImageError
from khl import Message, Bot, Channel
from khl.card import Card, CardMessage, Element, Module, Types
from datetime import datetime, timedelta
from utils.KookApi import icon_cm,bot
from utils.Gtime import GetTime
from utils.FileManage import VipShopBgDict,config
from utils.ShopImg import img_requestor


#下图用于替换违规的vip图片
illegal_img_11 = "https://img.kookapp.cn/assets/2022-09/a1k6QGZMiW0rs0rs.png"
illegal_img_169 = "https://img.kookapp.cn/assets/2022-09/CVWFac7CJG0zk0k0.png"

#获取uuid
def get_uuid():
    get_timestamp_uuid = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    return get_timestamp_uuid


################################################################################

# 成功兑换vip的用户+vip的uuid
from utils.FileManage import VipUserDict, VipUuidDict


# 计算时间戳，用于给用户设置vip时间
def vip_time_stamp(kook_user_id: str, day: int = 0):
    # 算到下一个月的时间戳差值
    times_diff = day * 86400
    # 下n个月同时间的时间戳，86400是一天的秒数
    times_next_month = time.time() + times_diff

    # 如果用户不在dict里面，说明是新的vip
    if kook_user_id not in VipUserDict:
        return times_next_month
    else:
        times_end = VipUserDict[kook_user_id]['time']
        # 当前结束时间戳+下n个月的时间戳
        next_end = times_end + times_diff
        #print(next_end)
        return next_end


#检查vip的剩余时间
def vip_time_remain(user_id):
    """
    get_time_remain of vip,return in seconds
    """
    # 时间差值
    timeout = VipUserDict[user_id]['time'] - time.time()
    return timeout


# 生成uuid
async def create_vip_uuid(num: int = 10, day: int = 30):
    """_summary_

    Args:
        num (int): Defaults to 10.
        day (int): Defaults to 30.

    Returns:
        str: text for uuid
    """
    global VipUuidDict
    #一次性生成20个
    i = num
    NewUuid = list()  #当前创建的新uuid
    while (i > 0):
        uuid = str(get_uuid())
        VipUuidDict[uuid] = {'status': True, 'days': day, 'prime': False}
        if day > 3000: VipUuidDict[uuid]['prime'] = True  #永久会员
        NewUuid.append(uuid)
        i -= 1

    # 更新uuid
    VipUuidDict.save()

    text = ""
    for uuid in NewUuid:
        text += f"{uuid}" + "\n"

    print(f"[vip-c] create_vip_uuid - num:{num} - day:{day}")
    return text


#获取vip时间剩余卡片消息
async def vip_time_remain_cm(times):
    cm = CardMessage()
    c1 = Card(color='#e17f89')
    c1.append(
        Module.Section(Element.Text('您的「vip会员」还剩', Types.Text.KMD), Element.Image(src=icon_cm.ahri_forest, size='sm')))
    c1.append(Module.Divider())
    c1.append(Module.Countdown(datetime.now() + timedelta(seconds=times), mode=Types.CountdownMode.DAY))
    cm.append(c1)
    return cm


# 兑换vip
async def using_vip_uuid(msg: Message, uuid1: str, bot: Bot, debug_ch: Channel):
    user_id = msg.author_id
    cm = CardMessage()
    c = Card(color='#e17f89')
    text = ""
    log_str = ""
    global VipUuidDict, VipUserDict
    # 判断uuid类型
    if uuid1 in VipUuidDict and VipUuidDict[uuid1]['status']:
        VipUuidDict[uuid1]['status'] = False
        days = VipUuidDict[uuid1]['days']
        time = vip_time_stamp(user_id, days)
        # 设置用户的时间和个人信息
        VipUserDict[user_id] = {'time': time, 'name_tag': f"{msg.author.username}#{msg.author.identify_num}"}
        # 记录uuid被谁使用了
        VipUuidDict[uuid1]['user_id'] = user_id
        if VipUuidDict[uuid1]['prime']:
            log_str += f"[vip-u] prime_vip - Au:{user_id}"
            text = "您已「永久」包养了阿狸！\n"
        else:
            log_str += f"[vip-u] vip {days} - Au:{user_id}"
            text = f"您已激活阿狸「{days}」天会员\n"
    else:
        log_str = "ERR! [vip-u] uuid not in dict or used"
        text = f"该兑换码无效！"
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.ahri_dark, size='sm')))
        c.append(Module.Context(Element.Text("或许是填错了？一个兑换码只能用一次哦", Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)
        print(log_str)
        return False

    # 发送卡片消息
    c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.ahri_kda3, size='sm')))
    c.append(Module.Context(Element.Text("您的恩情，阿狸会永远铭记。", Types.Text.KMD)))
    c.append(
        Module.Countdown(datetime.now() + timedelta(seconds=vip_time_remain(user_id)), mode=Types.CountdownMode.DAY))
    c.append(Module.Divider())
    c.append(Module.Section('加入官方服务器，即可获得「阿狸赞助者」身份组', Element.Button('来狸', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
    cm.append(c)
    await msg.reply(cm)
    print(log_str)
    # 发送消息到日志频道
    await bot.client.send(debug_ch, f"用户「{user_id}_{VipUserDict[user_id]['name_tag']}」兑换了「{days}」天阿狸vip！")
    return True


# 检查用户vip是否失效或者不是vip
async def vip_ck(msg):
    """
    params can be:
        * `msg:Message`   check & inform user if they aren't vip
        * `author_id:str` will not send reply, just check_if_vip 
    
    retuns:
        * True: is vip
        * False: not vip
    """
    flag = False
    user_id = msg
    if isinstance(msg, Message):
        user_id = msg.author_id  #如果是消息就修改
        flag = True

    cm = CardMessage()
    c = Card(color='#e17f89')
    text = "您并非vip用户，可以来 [支持一下](https://afdian.net/a/128ahri?tab=shop) 阿狸呢~"
    c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.ahri_game, size='sm')))
    c.append(Module.Context(Element.Text("您的恩情，阿狸会永远铭记。", Types.Text.KMD)))
    cm.append(c)
    # 检查
    if user_id in VipUserDict:
        #用户的vip是否过期？
        if time.time() > VipUserDict[user_id]['time']:
            del VipUserDict[user_id]
            #如果是消息，那就发送提示
            if flag:
                await msg.reply(cm)
                print(f"[vip-ck] Au:{user_id} msg.reply(vip out of date)")
            return False
        else:  #没有过期，返回真
            print(f"[vip-ck] Au:{user_id} is vip")
            return True
    else:  #用户不是vip
        if flag:  #如果是消息，那就发送提示
            await msg.reply(cm)
            print(f"[vip-ck] Au:{user_id} msg.reply(not vip)")
        return False


#获取当前vip用户列表
async def fetch_vip_user():
    global VipUserDict
    vipuserdict_temp = copy.deepcopy(VipUserDict)
    text = ""
    for u, ifo in vipuserdict_temp.items():
        if await vip_ck(u):  # vip-ck会主动修改dict
            time = vip_time_remain(u)
            time = format(time / 86400, '.2f')
            #通过/86400计算出大概的天数
            text += f"{u}_{ifo['name_tag']}\t = {time}\n"

    if vipuserdict_temp != VipUserDict:
        #将修改存放到文件中
        VipUserDict.save()
        print(f"[vip-r] update VipUserDict")

    return text


# vip抽奖相关代码（卡片消息）
def roll_vip_start(vip_num: int, vip_day: int, roll_day):
    """
    Args:
        vip_num (int): num of vip uuid
        vip_day (int): day of vip
        roll_day (int): day of roll end

    Returns:
        CardMessage for roll 
    """
    roll_second = roll_day * 86400
    cm = CardMessage()
    c = Card()
    c.append(Module.Section(Element.Text(f"添加表情回应，参加抽奖！"), Element.Image(src=icon_cm.ahri_kda3, size='sm')))
    c.append(Module.Context(Element.Text(f"奖励: {vip_day}天阿狸vip激活码   |  奖品: {vip_num}个", Types.Text.KMD)))
    c.append(Module.Countdown(datetime.now() + timedelta(seconds=roll_second), mode=Types.CountdownMode.DAY))
    cm.append(c)
    return cm


######################################################################################################

#替换掉违规图片（传入list的下标)
async def replace_illegal_img(user_id: str, num: int):
    """
        user_id:  kook user_id
        num: VipShopBgDict list index
    """
    try:
        global VipShopBgDict
        img_str = VipShopBgDict['bg'][user_id]["background"][num]
        VipShopBgDict['bg'][user_id]["background"][num] = illegal_img_169
        VipShopBgDict['bg'][user_id]["status"] = False  #需要重新加载图片
        print(f"[Replace_img] Au:{user_id} [{img_str}]")  #写入文件后打印log信息
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] replace_illegal_img\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        debug_ch = await bot.fetch_public_channel(config['channel']['debug_ch'])
        await bot.client.send(debug_ch, err_str)  #发送消息到debug频道

#计算用户背景图的list大小，避免出现空list的情况
def len_VusBg(user_id: str):
    """
       - len(VipShopBgDict[user_id]["background"])
       - return 0 if user not in dict 
    """
    if user_id in VipShopBgDict['bg']:
        return len(VipShopBgDict['bg'][user_id]["background"])
    else:
        return 0

# 获取自定义背景图的展示卡片
async def get_vip_shop_bg_cm(msg: Message):
    global VipShopBgDict
    if msg.author_id not in VipShopBgDict['bg']:
        return "您尚未自定义商店背景图！"
    elif len_VusBg(msg.author_id) == 0:
        return "您尚未自定义商店背景图！"

    cm = CardMessage()
    c1 = Card(color='#e17f89')
    c1.append(Module.Header('您当前设置的商店背景图如下'))
    c1.append(Module.Container(Element.Image(src=VipShopBgDict['bg'][msg.author_id]["background"][0])))
    sz = len(VipShopBgDict['bg'][msg.author_id]["background"])
    if sz > 1:
        c1.append(Module.Divider())
        c1.append(Module.Section(Element.Text('当前未启用的背景图，可用「/vip-shop-s 序号」切换', Types.Text.KMD)))
        i = 0
        while (i < sz):
            try:
                # 打开图片进行测试，没有问题就append
                bg_test = Image.open(
                    io.BytesIO(await img_requestor(VipShopBgDict['bg'][msg.author_id]["background"][i])))
                if i == 0:  #第一张图片只进行打开测试，没有报错就是没有违规，不进行后续的append操作
                    i += 1
                    continue
                # 插入后续其他图片
                c1.append(
                    Module.Section(Element.Text(f' [{i}]', Types.Text.KMD),
                                   Element.Image(src=VipShopBgDict['bg'][msg.author_id]["background"][i])))
                i += 1
            except UnidentifiedImageError as result:
                err_str = f"ERR! [{GetTime()}] checking [{msg.author_id}] img\n```\n{result}\n"
                #把被ban的图片替换成默认的图片，打印url便于日后排错
                err_str += f"[UnidentifiedImageError] url={VipShopBgDict['bg'][msg.author_id]['background'][i]}\n```"
                await replace_illegal_img(msg.author_id, i)  #替换图片
                debug_ch = await bot.fetch_public_channel(config['channel']['debug_ch']) 
                await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道
                print(err_str)
                return f"您上传的图片违规！请慎重选择图片。多次上传违规图片会导致阿狸被封！下方有违规图片的url\n{err_str}"

    cm.append(c1)
    return cm