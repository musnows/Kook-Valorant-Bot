import asyncio
import copy
import io
import json
import os
import random
import threading
import time
import aiohttp
import requests
import zhconv
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from api_endpoints import *


bot_token='1/MTMxMjU=/Utb3x1c2V2KpqruGAGJUOA==' #机器人颜色
font_color = '#ffffff'  # 文字颜色：白色

#用于临时存放图片的dict
shop_img_temp = {}
weapon_icon_temp = {}
level_icon_temp = {}
# 图片透明背景框
bg_main_169_WithOutLogo = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-10/uFfgpWWlDy0zk0k0.png').content))
# 有水印的背景框
bg_main_169 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/rLxOSFB1cC0zk0k0.png').content)) 

# 用户图片文件
with open("./log/UserShopBg.json", 'r', encoding='utf-8') as frpr:
    VipShopBgDict = json.load(frpr)

#将获取当前时间封装成函数方便使用
def GetTime():  
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
#将获取当前日期成函数方便使用
def GetDate(): 
    return time.strftime("%y-%m-%d", time.localtime())

# 图片获取器
async def img_requestor(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as r:
            return await r.read()

# 缩放图片，部分皮肤图片大小不正常
def resize(standard_x, img, standard_y=''):
    standard_y = standard_x if standard_y == '' else standard_y
    log_info = "[shop] "
    w, h = img.size
    log_info += f"原始图片大小:({w},{h}) - "
    ratio = w / h
    if ratio > standard_x / standard_y:
        sizeco = w / standard_x
        log_info += f"缩放系数:{format(sizeco,'.3f')} - "
        w_s = int(w / sizeco)
        h_s = int(h / sizeco)
    else:
        sizeco = h / standard_y
        log_info += f"缩放系数:{format(sizeco,'.3f')} - "
        w_s = int(w / sizeco)
        h_s = int(h / sizeco)
    log_info += f"缩放后大小:({w_s},{h_s})"
    print(log_info)
    img = img.resize((w_s, h_s), Image.Resampling.LANCZOS)
    return img

# 处理图片
def sm_comp_vip(icon, name, price, level_icon, skinuuid):
    bg = Image.new(mode='RGBA', size=(400, 240))  # 新建一个画布
    # 处理武器图片
    start = time.perf_counter()  #开始计时
    if os.path.exists(f'./log/img_temp/weapon/{skinuuid}.png'):
        layer_icon = Image.open(f'./log/img_temp/weapon/{skinuuid}.png')  # 打开武器图片
    else:
        layer_icon = Image.open(io.BytesIO(requests.get(icon).content))  # 打开武器图片
        layer_icon.save(f'./log/img_temp/weapon/{skinuuid}.png', format='PNG')
    end = time.perf_counter()
    log_time = f"[GetWeapen] {format(end - start, '.4f')} "
    layer_icon = resize(300, layer_icon, 130)
    # layer_icon = layer_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
    # 按缩放比例后的长宽进行resize（resize就是将图像原长宽拉伸到新长宽） Image.Resampling.LANCZOS 是一种处理方式
    # 用小图的宽度减去武器图片的宽度再除以二 得到武器图片x轴坐标  y轴坐标 是固定值 standard_icon_top_blank
    w, h = layer_icon.size
    x = 50 if w == 300 else int((350 - w) / 2)
    y = int((240 - h) / 2) if w == 300 else 30
    bg.paste(layer_icon, (x, y), layer_icon)
    # bg.paste代表向bg粘贴一张图片
    # 第一个参数是图像layer_icon
    # 第二个参数(left_position, standard_icon_top_blank)就是刚刚算出来的 x,y 坐标 最后一个layer_icon是蒙版
    # 处理武器level的图片(存到本地dict里面方便调用)
    start = time.perf_counter()  #开始计时
    if level_icon not in level_icon_temp:
        LEVEL_Icon = Image.open(io.BytesIO(requests.get(level_icon).content))  # 打开武器图片
        level_icon_temp[level_icon] = LEVEL_Icon
    else:
        LEVEL_Icon = level_icon_temp[level_icon]
    end = time.perf_counter()
    log_time += f"- [GetIters] {format(end - start, '.4f')} "
    print(log_time)
    LEVEL_Icon = LEVEL_Icon.resize((25, 25), Image.Resampling.LANCZOS)
    bg.paste(LEVEL_Icon, (368, 11), LEVEL_Icon)
    text = zhconv.convert(name, 'zh-cn')  # 将名字简体化
    draw = ImageDraw.Draw(bg)  # 让bg这个图层能被写字
    # 第一个参数 standard_text_position 是固定参数坐标 ， 第二个是文字内容 ， 第三个是字体 ， 第四个是字体颜色
    draw.text((15, 205), text, font=ImageFont.truetype('./log/SourceHanSansCN-Regular.otf', 25), fill=font_color)
    text = f"{price}"  # 价格
    draw.text((320, 13), text, font=ImageFont.truetype('./log/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    # bg.show() #测试用途，展示图片(linux貌似不可用)
    if not os.path.exists(f'./log/img_temp/comp/{skinuuid}.png'):
        bg.save(f'./log/img_temp/comp/{skinuuid}.png')
    global weapon_icon_temp#vip用户的抽屉
    if skinuuid not in weapon_icon_temp:
        weapon_icon_temp[skinuuid] = bg
    return bg

#如sm—comp中一样，向bg粘贴img
def bg_comp(bg, img, x, y):
    position = (x, y)
    bg.paste(img, position, img) 
    return bg

# 创建图片
async def kook_create_asset(bg):
    imgByteArr = io.BytesIO()
    bg.save(imgByteArr, format='PNG')
    imgByte = imgByteArr.getvalue()
    data = aiohttp.FormData()
    data.add_field('file',imgByte)
    url = "https://www.kookapp.cn/api/v3/asset/create"
    kook_headers = {f'Authorization': f"Bot {bot_token}"}
    body = {'file':data}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=kook_headers,data=data) as response:
            res = json.loads(await response.text())
    return res

# 将图片修改到标准大小
def resize_vip(standard_x, standard_y, img):
    w, h = img.size
    log_info = "[resize_vip] "
    log_info += f"原始图片大小:({w},{h}) - "
    ratio = w / h
    if ratio <= 1.78:
        sizeco = w / standard_x
        log_info += f"缩放系数:{format(sizeco,'.3f')} - "
        w_s = int(w / sizeco)
        h_s = int(h / sizeco)
        log_info += f"缩放后大小:({w_s},{h_s})"
        blank = (h_s - standard_y) / 2
        img = img.resize((w_s, h_s), Image.Resampling.LANCZOS)
        img = img.crop((0, blank, w_s, h_s - blank))
    else:
        sizeco = h / standard_y
        log_info += f"缩放系数:{format(sizeco,'.3f')} - "
        w_s = int(w / sizeco)
        h_s = int(h / sizeco)
        log_info += f"缩放后大小:({w_s},{h_s})"
        blank = (w_s - standard_x) / 2
        img = img.resize((w_s, h_s), Image.Resampling.LANCZOS)
        img = img.crop((blank, 0, w_s - blank, h_s))
    return img

def skin_uuid_to_comp(skinuuid, ran):
    res_item = fetch_skin_bylist(skinuuid)  # 从本地文件中查找
    res_price = fetch_item_price_bylist(skinuuid)  # 在本地文件中查找
    price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
    res_iters = fetch_skin_iters_bylist(skinuuid)
        
    img = sm_comp_vip(res_item["data"]['levels'][0]["displayIcon"], res_item["data"]["displayName"], price,
                        res_iters['data']['displayIcon'], skinuuid)
    global shop_img_temp  #这里是把处理好的图片存到本地
    shop_img_temp[ran].append(img)


# 获取vip用户每日商店的图片
async def get_daily_shop_vip_img(list_shop: dict,userdict: dict,account: str,img_src:str):
    """returns dict:
     - {"status":False,"value":f"{err_str}"}
     - {"status":True,"value":bg}
    """
    global VipShopBgDict
    player_uuid = userdict['auth_user_id'] #玩家uuid
    cur_time = GetTime() #当前时间
    # 判断uuid在不在
    if player_uuid not in VipShopBgDict['data']:
        VipShopBgDict['data'][player_uuid] = { 
            'img_back':img_src,
            'init_time':cur_time,
            'last_time':cur_time
        }#设立初始值
    try:  #打开图片进行测试
        bg_vip = Image.open(io.BytesIO(await img_requestor(img_src)))
        VipShopBgDict['data'][player_uuid]['img_back']=img_src #替换背景图url
        VipShopBgDict['data'][player_uuid]['last_time']=cur_time
        with open("./log/UserShopBg.json", 'w', encoding='utf-8') as fw1:
            json.dump(VipShopBgDict, fw1, indent=2, sort_keys=True, ensure_ascii=False)
    except UnidentifiedImageError as result:
        err_str = f"ERR! [{GetTime()}] vip_shop_imgck\n```\n{result}\n```"
        print(err_str)  #写入文件后打印log信息
        return {"status": False, "value": f"当前使用的图片无法获取！请重新上传您的背景图\n{err_str}"}

    #图没有问题，则缩放后保存
    bg_vip = resize_vip(1280, 720, bg_vip)
    bg_vip = bg_vip.convert('RGBA')
    # alpha_composite才能处理透明的png。参数1是底图，参数2是需要粘贴的图片
    bg_vip = Image.alpha_composite(bg_vip, bg_main_169)
    bg = copy.deepcopy(bg_vip)  # 两种情况都需要把vip图片加载到bg中
    #开始画图
    x = 50
    y = 100
    ran = random.randint(1, 9999)
    global shop_img_temp
    shop_img_temp[ran] = []
    img_num = 0

    for skinuuid in list_shop:
        img_path = f'./log/img_temp/comp/{skinuuid}.png'
        if skinuuid in weapon_icon_temp:#vip用户需要用的抽屉
            shop_img_temp[ran].append(weapon_icon_temp[skinuuid])
        elif os.path.exists(img_path):
            shop_img_temp[ran].append(Image.open(img_path))
        else:
            th = threading.Thread(target=skin_uuid_to_comp, args=(skinuuid, ran))
            th.start()
        await asyncio.sleep(0.8)  #尝试错开网络请求
    while True:
        img_temp = [i for i in shop_img_temp[ran]]
        for i in img_temp:
            shop_img_temp[ran].pop(shop_img_temp[ran].index(i))
            #i.save(f"./t{x}_{y}.png", format='PNG')
            bg = bg_comp(bg, i, x, y)
            if x == 50:
                x += 780
            elif x == 830:
                x = 50
                y += 279
            img_num += 1
        if img_num >= 4:
            break
        await asyncio.sleep(0.2)
    #vip用户写入vp和r点
    play_currency = await fetch_valorant_point(userdict)
    vp = play_currency["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #vp
    rp = play_currency["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]  #R点
    draw = ImageDraw.Draw(bg)
    vp_c = (f"{vp}")  #vp
    draw.text((537, 670), vp_c, font=ImageFont.truetype('./log/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    #rp = 89
    rp_c = (f"{rp}")  #rp
    rp_pos = (710, 670)
    if rp < 100:
        rp_pos = (722, 670)
    draw.text(rp_pos, rp_c, font=ImageFont.truetype('./log/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    if ran in shop_img_temp:
        del shop_img_temp[ran]
    #画完图之后返回结果
    #bg.save(f"./log/img_temp/ret/{player_uuid}.png",format='PNG')
    return {"status": True, "value": bg}