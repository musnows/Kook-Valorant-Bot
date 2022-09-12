import uuid
import json
import time
from khl import Message,Bot
from khl.card import Card, CardMessage, Element, Module, Types
from datetime import datetime, timedelta
from upd_msg import icon_cm

Debug_ch = '6248953582412867'
#获取uuid
def get_uuid():
    get_timestamp_uuid = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    return get_timestamp_uuid


#将获取当前时间封装成函数方便使用
def GetTime():
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())


################################################################################

# 创建uuid dict
VipUuidDict = {}
# 成功兑换vip的用户
VipUserDict = {}

# 加载文件中的uuid
with open("./log/VipUuid.json", 'r', encoding='utf-8') as frrk:
    VipUuidDict = json.load(frrk)

# 加载文件中的vip的用户
with open("./log/VipUser.json", 'r', encoding='utf-8') as frus:
    VipUserDict = json.load(frus)


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
        num (int, optional): _description_. Defaults to 10.
        day (int, optional): _description_. Defaults to 30.

    Returns:
        _type_: _description_
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
    with open("./log/VipUuid.json", 'w', encoding='utf-8') as fw2:
        json.dump(VipUuidDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

    text = ""
    for uuid in NewUuid:
        text += f"{uuid}" + "\n"

    print(f"[vip-c] create_vip_uuid - num:{num} - day:{day}")
    return text


#获取vip时间剩余卡片消息
async def vip_time_remain_cm(times):
    cm = CardMessage()
    c1 = Card(color='#e17f89')
    c1.append(Module.Section(Element.Text('您的「vip会员」还剩', Types.Text.KMD), Element.Image(src=icon_cm.ahri_forest, size='sm')))
    c1.append(Module.Divider())
    c1.append(Module.Countdown(datetime.now() + timedelta(seconds=times), mode=Types.CountdownMode.DAY))
    cm.append(c1)
    return cm


# 兑换vip
async def using_vip_uuid(msg: Message, uuid1: str,bot:Bot):
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
        VipUserDict[user_id] = {
            'time':time,
            'name_tag':f"{msg.author.username}#{msg.author.identify_num}"
        }
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

    # 更新uuid
    with open("./log/VipUuid.json", 'w', encoding='utf-8') as fw2:
        json.dump(VipUuidDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
    # 更新vip用户列表
    with open("./log/VipUser.json", 'w', encoding='utf-8') as fw2:
        json.dump(VipUserDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

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
    debug_ch = await bot.client.fetch_public_channel(Debug_ch)
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
                print(f"[vip-ck] Au:{user_id} msg.reply(vip out of date!)")
            return False
        else:#没有过期，返回真
            return True
    else:#用户不是vip
        if flag: #如果是消息，那就发送提示
            await msg.reply(cm)
            print(f"[vip-ck] Au:{user_id} msg.reply(not vip)")
        return False
    
#获取当前vip用户列表
def fetch_vip_user():
    text=""
    for u,ifo in VipUserDict.items():
        time = vip_time_remain(u)
        time = format(time/86400, '.2f')
        #通过/86400计算出大概的天数
        text +=f"{u}_{ifo['name_tag']}\t = {time}\n"
        
    return text
        