import json
import random
import leancloud
import traceback
from khl.card import Card, CardMessage, Module, Element, Types

# 皮肤的评价
from utils.FileManage import config,SkinRateDict
leancloud.init(config["leancloud"]["appid"], master_key=config["leancloud"]["master_key"])

# 获取皮肤评价的信息
async def get_shop_rate(list_shop: dict, kook_user_id: str):
    """皮肤评分和评价，用户不在err_user里面才显示\n
    { "sum":rate_avg,"lv":rate_lv,"text_list":rate_text,"count":rate_count }
    """
    # 初始化相关值
    rate_text = []
    rate_count = 0
    rate_total = 0
    rate_avg = 0 # 平均分
    # leancould中搜索
    query = leancloud.Query('SkinRate')
    # 遍历用户的4个商店皮肤
    for skin in list_shop:
        # 查找数据库中和skin uuid相同的评价
        query.equal_to('skinUuid',skin)
        objlist = query.find()
        if len(objlist) > 0: #找到了
            obj = objlist[0]
            rate_total += obj.get('rating') # 获取评分
            skin_name = f"「{obj.get('skinName')}」" # 获取皮肤名
            text = f"%-50s\t\t评分: {obj.get('rating')}\n" % skin_name
            # 获取皮肤评价的list
            cmt = obj.get('comment')
            if len(cmt) == 0:# 元素内没有评论，出现错误
                text += f"「随机评论」 NO CMT ERR\n"
            else:# 有评论，生成随机数
                ran = random.randint(0, len(cmt) - 1)
                text += f"「随机评论」 {cmt[ran]}\n"
            # 插入text
            rate_text.append(text)

    rate_lv = "皮肤评价数据仍待收集…"
    rate_count = len(rate_text) # 直接计算长度
    if rate_count > 0:
        rate_avg = rate_total // rate_count
        #记录当日冠军和屌丝
        if rate_avg > SkinRateDict["cmp"]["best"]["pit"]:
            SkinRateDict["cmp"]["best"]["pit"] = rate_avg
            SkinRateDict["cmp"]["best"]["skin"] = list_shop
            SkinRateDict["cmp"]["best"]["kook_id"] = kook_user_id
            print(f"[shop] update rate-best  Au:{kook_user_id} = {rate_avg}")
        elif rate_avg < SkinRateDict["cmp"]["worse"]["pit"]:
            SkinRateDict["cmp"]["worse"]["pit"] = rate_avg
            SkinRateDict["cmp"]["worse"]["skin"] = list_shop
            SkinRateDict["cmp"]["worse"]["kook_id"] = kook_user_id
            print(f"[shop] update rate-worse Au:{kook_user_id} = {rate_avg}")

        if rate_avg >= 0 and rate_avg <= 20:
            rate_lv = "丐帮帮主"
        elif rate_avg > 20 and rate_avg <= 40:
            rate_lv = "省钱能手"
        elif rate_avg > 40 and rate_avg <= 60:
            rate_lv = "差强人意"
        elif rate_avg > 60 and rate_avg <= 80:
            rate_lv = "芜湖起飞"
        elif rate_avg > 80 and rate_avg <= 100:
            rate_lv = "天选之人"

    return { "sum":rate_avg,"lv":rate_lv,"text_list":rate_text,"count":rate_count }

# 获取皮肤评价的卡片
async def get_shop_rate_cm(list_shop: dict, kook_user_id: str, cm: CardMessage):
    ret = await get_shop_rate(list_shop, kook_user_id)
    if ret['count'] == 0:
        c1 = Card(Module.Header(f"{ret['lv']}"), Module.Context(f"你可以使用「/rate 皮肤名」参与评分哦！"), color='#fb4b57')
    else:
        c1 = Card(Module.Header(f"综合评分 {ret['sum']}，{ret['lv']}"),
                    Module.Context(f"以下评论来自其他用户，仅供图一乐"),
                    Module.Divider(),
                    color='#fb4b57')
        # 插入单个皮肤评价
        for text in ret['text_list']:
            c1.append(Module.Section(Element.Text(text, Types.Text.KMD)))
            c1.append(Module.Divider())
        c1.append(Module.Context(Element.Text(f"可以使用「/rate 皮肤名」参与评分\n或用「/kkn」查看昨日天选之子/丐帮帮主", Types.Text.KMD)))
    # 插入卡片
    cm.append(c1)
    return cm


# 每日提醒的时候，计算用户的得分，插入到当日最高和最低分中
async def check_shop_rate(kook_user_id: str, list_shop: list):
    global SkinRateDict
    rate_count = 0
    rate_total = 0
    for sk in list_shop:
        if sk in SkinRateDict['rate']:
            rate_count += 1
            rate_total += SkinRateDict['rate'][sk]['pit']

    if rate_count != 0:
        rate_avg = rate_total // rate_count  #平均分
        #记录冠军和屌丝
        if rate_avg > SkinRateDict["cmp"]["best"]["pit"]:
            SkinRateDict["cmp"]["best"]["pit"] = rate_avg
            SkinRateDict["cmp"]["best"]["skin"] = list_shop
            SkinRateDict["cmp"]["best"]["kook_id"] = kook_user_id
        elif rate_avg < SkinRateDict["cmp"]["worse"]["pit"]:
            SkinRateDict["cmp"]["worse"]["pit"] = rate_avg
            SkinRateDict["cmp"]["worse"]["skin"] = list_shop
            SkinRateDict["cmp"]["worse"]["kook_id"] = kook_user_id
        return True
    else:
        return False