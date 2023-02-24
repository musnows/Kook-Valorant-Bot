import zhconv
import random
import leancloud
import traceback
from khl.card import Card, CardMessage, Module, Element, Types

# 皮肤的评价
from utils.valorant import Val
from utils.FileManage import config,SkinRateDict
leancloud.init(config["leancloud"]["appid"], master_key=config["leancloud"]["master_key"])

# 获取皮肤评价的信息
async def get_shop_rate(list_shop: dict, kook_user_id: str):
    """皮肤评分和评价，用户不在err_user里面才显示\n
    { "sum":rate_avg,"lv":rate_lv,"text_list":rate_text,"count":rate_count }
    """
    try:
        # 初始化相关值
        rate_text = []
        rate_total = 0
        rate_avg = 0 # 平均分
        # leancould中搜索，用户评分列表
        query = leancloud.Query('UserRate')
        # 遍历用户的4个商店皮肤
        for skin in list_shop:
            # 查找数据库中和skinUuid相同的评价
            query.equal_to('skinUuid',skin)
            objlist = query.find()
            if len(objlist) > 0: # 找到了评论，生成随机数
                ran = random.randint(0, len(objlist) - 1)
                obj = objlist[ran] # 随机获取一个对象
                rate_total += obj.get('rating') # 获取评分
                skin_name = f"「{obj.get('skinName')}」" # 获取皮肤名
                text = f"%-50s\t\t评分: {obj.get('rating')}\n" % skin_name
                text += f"「随机评论」 {obj.get('comment')}\n"
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
    except Exception as result:
        print(f"ERR! [get_shop_rate]\n{traceback.format_exc()}")
        return { "sum":0,"lv":"皮肤评价数据仍待收集…","text_list":[],"count":0 }

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

# 每日早八，更新leancloud中的ShopCmp（被kill掉的时候也执行此函数）
def update_shop_cmp():
    """update shop rate in leancloud
    """
    try:
        # 获取对象
        ShopCmp = leancloud.Object.extend('ShopCmp')
        query = ShopCmp.query
        # 只更新昨日的
        query.equal_to('today',False)
        objlist = query.find()
        if len(objlist) == 0:
            raise Exception("leancloud find today err!")
        # 开始更新，先设置为最差
        platfrom = 'kook'
        rate_avg = SkinRateDict["kkn"]["worse"]["pit"]
        list_shop = SkinRateDict["kkn"]["worse"]["skin"]
        kook_user_id = SkinRateDict["kkn"]["worse"]["kook_id"]
        for i in objlist:
            if(i.get('best')): # 是最佳 
                if SkinRateDict["kkn"]["best"]["pit"] <= i.get('rating'): 
                    continue # 当前用户分数小于数据库中的,不更新
                # 设置值
                rate_avg = SkinRateDict["kkn"]["best"]["pit"]
                list_shop = SkinRateDict["kkn"]["best"]["skin"]
                kook_user_id = SkinRateDict["kkn"]["best"]["kook_id"]
            elif(SkinRateDict["kkn"]["worse"]["pit"] >= i.get('rating')): # 是最差，判断分数
                continue # 如果本地用户好于数据库记录，不更新
            
            # 更新对象并保存
            i.set('userId',kook_user_id)
            i.set('skinList',list_shop)
            i.set('rating',rate_avg)
            i.set('platfrom',platfrom)
            i.save()
            print(f"[update_shop_cmp] saving best:{i.get('best')}")
    except:
        print(f"ERR! [update_shop_cmp]\n{traceback.format_exc()}")

# 通过名字查找可以购买的皮肤，并返回一个list
async def get_available_skinlist(name:str):
    """name must be zh-CN
    Return: [{'skin': [{'displayName': skin['displayName'], 'lv_uuid': skin['levels'][0]['uuid']}], 'price': price}]
    """
    name = zhconv.convert(name, 'zh-tw')  #将名字繁体化
    sklist = Val.fetch_skin_list_byname(name)
    if sklist == []:  #空list代表这个皮肤不在里面
        return []

    retlist = list()  # 用于返回的list
    for s in sklist:
        # 查找皮肤价格
        # 因为不是所有搜到的皮肤都有价格，没有价格的皮肤就是商店不刷的
        res_price = Val.fetch_item_price_bylist(s['lv_uuid'])
        if res_price != None:  # 有可能出现返回值里面找不到这个皮肤的价格的情况，比如冠军套
            price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
            data = {'skin': s, 'price': price}
            retlist.append(data)

    return retlist

# 获取可以购买皮肤的相关信息
async def query_UserCmt(user_id:str):
    """Return
     A list containing the skin evaluated by the user,
    """
    query = leancloud.Query('UserCmt')
    query.equal_to('platform', 'kook')
    query.equal_to('userId', user_id) # 查找usercmt中有没有该用户
    objlist = query.find()
    print(objlist)
    if len(objlist) > 0 : # 存在 
        # 获取这个用户评价过的皮肤列表
        return objlist[0].get('skinList') 
    else: # 不存在
        return []

# 获取可以购买皮肤的相关信息的text
async def get_skinlist_rate_text(skinlist:list,user_id:str):
    """Args:
    - skinlist: return of get_available_skinlist()
    - user_id: kook user_id

    Return { "text":text,"sum":len(get_skinlist_rate_text)}\n
    - text: rating info of the skin in list\n
    - sum: the total skin rating by user\n
    `√ rate by user_id`,`+ rate by other_user`,`- no one rate`
    """
    # 获取该用户已评价的皮肤列表
    userCmtList = await query_UserCmt(user_id)
    print(userCmtList)
    i=0
    query = leancloud.Query('UserRate')
    query.equal_to('platform', 'kook')
    text = ""  # 模拟一个选择表
    for w in skinlist:
        # 先插入皮肤名字和皮肤价格
        text += f"[{i}] - {w['skin']['displayName']}  - VP {w['price']}"
        # 情况1，当前用户评价过这个皮肤
        if w['skin']['lv_uuid'] in userCmtList:
            text += " √\n"
        else:
            query.equal_to('skinUuid', w['skin']['lv_uuid'])
            objlist = query.find()
            # 情况2，其他用户评价过这个皮肤
            if len(objlist)>0: # 数据库中找到了其他用户的评价
                text += " +\n"
            else: # 情况3，无人问津
                text += " -\n"
        # 标号+1
        i += 1
    # 返回结果
    return { "text":text,"sum":len(userCmtList)}