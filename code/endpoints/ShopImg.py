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
from endpoints.Val import *
from endpoints.Gtime import *

#bot_token='1/MTMxMjU=/Utb3x1c2V2KpqruGAGJUOA==' #机器人token，用来上传图片到kook

font_color = '#ffffff'  # 文字颜色：白色

#用于临时存放图片的dict
shop_img_temp = {}
weapon_icon_temp = {}
skin_level_icon_temp = {}
# 图片透明背景框
bg_main_169_WithOutLogo = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-10/uFfgpWWlDy0zk0k0.png').content))
# 图片透明背景框,有水印
bg_main_169 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/rLxOSFB1cC0zk0k0.png').content)) 

default_bg_11 = "https://img.kookapp.cn/assets/2022-09/a1k6QGZMiW0rs0rs.png"
default_bg_169 = "https://img.kookapp.cn/assets/2022-09/CVWFac7CJG0zk0k0.png"

# # 用户背景图片文件
# with open("./log/UserShopBg.json", 'r', encoding='utf-8') as frpr:
#     VipShopBgDict = json.load(frpr)

# 图片获取器
async def img_requestor(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as r:
            return await r.read()

# 缩放图片，部分皮肤图片大小不正常
def resize_skin(standard_x, img, standard_y=''):
    standard_y = standard_x if standard_y == '' else standard_y
    log_info = "[resize] "
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

# 将16比9的背景图片缩放到标准大小
def resize_169(standard_x, standard_y, img):
    w, h = img.size
    log_info = "[resize_169] "
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

# 处理图片，这个函数能够生成单个皮肤的图片，最后再一起粘贴到主图中
def sm_comp_169(skin_img_url, skin_name, price, skin_level_icon, skinuuid):
    bg = Image.new(mode='RGBA', size=(400, 240))  # 新建一个画布
    # 处理皮肤图片
    start = time.perf_counter()  #开始计时
    if os.path.exists(f'./log/img_temp_vip/weapon/{skinuuid}.png'):
        layer_icon = Image.open(f'./log/img_temp_vip/weapon/{skinuuid}.png')  # 打开皮肤图片
    else:
        layer_icon = Image.open(io.BytesIO(requests.get(skin_img_url).content))  # 打开皮肤图片
        layer_icon.save(f'./log/img_temp_vip/weapon/{skinuuid}.png', format='PNG')
    end = time.perf_counter() # 结束获取皮肤图片计时
    log_time = f"[GetWeapen] {format(end - start, '.4f')} "# 记录获取皮肤图片用时

    # 按缩放比例后的长宽进行resize（resize就是将图像原长宽拉伸到新长宽） Image.Resampling.LANCZOS 是一种处理方式
    layer_icon = resize_skin(300, layer_icon, 130) 
    # layer_icon = layer_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
   
    # 用小图的宽度减去皮肤图片的宽度再除以二 得到皮肤图片x轴坐标  y轴坐标 是固定值 standard_icon_top_blank
    w, h = layer_icon.size
    x = 50 if w == 300 else int((350 - w) / 2)
    y = int((240 - h) / 2) if w == 300 else 30
    bg.paste(layer_icon, (x, y), layer_icon)
    # bg.paste代表向bg粘贴一张图片
    # 第一个参数是图像layer_icon
    # 第二个参数(left_position, standard_icon_top_blank)就是刚刚算出来的 x,y 坐标 最后一个layer_icon是蒙版

    # 处理皮肤level的图片(存到本地dict里面方便调用)
    start = time.perf_counter()  # 开始计时
    if skin_level_icon not in skin_level_icon_temp: #本地没有，获取
        level_icon = Image.open(io.BytesIO(requests.get(skin_level_icon).content))# 打开皮肤等级图标
        skin_level_icon_temp[skin_level_icon] = level_icon
    else: # 本地有，直接用本地的
        level_icon = skin_level_icon_temp[skin_level_icon]
    end = time.perf_counter() # 结束获取皮肤等级图片的计时
    log_time += f"- [GetIters] {format(end - start, '.4f')} " # 记录皮肤等级图片用时
    print(log_time) #打印用时
    
    # 缩放皮肤等级图标
    level_icon = level_icon.resize((25, 25), Image.Resampling.LANCZOS)
    bg.paste(level_icon, (368, 11), level_icon) # 在指定位置粘贴皮肤等级图标
    text = zhconv.convert(skin_name, 'zh-cn')  # 将名字简体化
    draw = ImageDraw.Draw(bg)  # 让bg这个图层能被写字
    # 第一个参数 standard_text_position 是固定参数坐标 ， 第二个是文字内容 ， 第三个是字体 ， 第四个是字体颜色
    draw.text((15, 205), text, font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 25), fill=font_color)
    text = f"{price}"  # 价格
    draw.text((320, 13), text, font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    # bg.show() #测试用途，展示图片 (linux不可用)

    # 判断该皮肤图片的本地路径是否存在，如果不存在，则保存到本地
    if not os.path.exists(f'./log/img_temp_vip/comp/{skinuuid}.png'):
        bg.save(f'./log/img_temp_vip/comp/{skinuuid}.png')
    global weapon_icon_temp #皮肤图片的抽屉
    if skinuuid not in weapon_icon_temp:
        weapon_icon_temp[skinuuid] = bg
    return bg

# 在本地文件中查找皮肤的图片，并插入到temp中
def skin_uuid_to_comp(skinuuid, ran):
    res_item = fetch_skin_bylist(skinuuid)  # 从本地文件中查找皮肤信息
    res_price = fetch_item_price_bylist(skinuuid)  # 在本地文件中查找皮肤价格
    price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'] # 取出价格
    res_iters = fetch_skin_iters_bylist(skinuuid) # 在本地文件中查找皮肤等级
    # 画单个皮肤的图片
    img = sm_comp_169(res_item["data"]['levels'][0]["displayIcon"], res_item["data"]["displayName"], price,
                        res_iters['data']['displayIcon'], skinuuid)
    global shop_img_temp  # 这里是把处理好的图片存到当前执行用户的临时库中
    shop_img_temp[ran].append(img) 

# 往底图的指定位置粘贴单个皮肤的图片
def bg_comp(bg, img, x, y):
    position = (x, y)
    bg.paste(img, position, img) 
    return bg

# 获取16比9的每日商店的图片
async def get_shop_img_169(list_shop: dict,player_uuid:str,vp:str,rp:str,bg_img_src=default_bg_169):
    """ args:
     - list_shop: user daily shop skin dict
     - bg_img_src: background img url
     - player_uuid: riot player uuid

    returns dict:
     - {"status":False,"value":"err_str"}
     - {"status":True,"value":bg}
    """
    # 背景图缩放后保存
    bg_img = Image.open(io.BytesIO(await img_requestor(bg_img_src)))
    bg_img = resize_169(1280, 720, bg_img)
    bg_img = bg_img.convert('RGBA')
    # alpha_composite才能处理透明的png。参数1是底图，参数2是需要粘贴的图片
    bg_img = Image.alpha_composite(bg_img, bg_main_169)
    bg = copy.deepcopy(bg_img)  # 两种情况都需要把背景图图片加载到bg中
    #开始画图
    x = 50
    y = 100
    ran = 0 # 设立ran的基准值为0
    global shop_img_temp 
    #循环判断创建的随机值在不在其中，如果在，那就还需要继续生成，直到产生一个不在其中的 
    while(ran in shop_img_temp): 
        ran = random.randint(1, 9999) # 创建一个1-9999的随机值
    
    # 创建键值，用于保存多线程的返回值
    shop_img_temp[ran] = [] 
    # 开始遍历4个皮肤uuid
    for skinuuid in list_shop:
        img_path = f'./log/img_temp_vip/comp/{skinuuid}.png'
        if skinuuid in weapon_icon_temp:# 16-9需要用的全局变量
            shop_img_temp[ran].append(weapon_icon_temp[skinuuid])
        elif os.path.exists(img_path):# 全局变量里面没有，要去本地路径里面找
            shop_img_temp[ran].append(Image.open(img_path))
        else: # 都没有，画图
            th = threading.Thread(target=skin_uuid_to_comp, args=(skinuuid, ran))
            th.start()
        await asyncio.sleep(0.7) # 睡一会，尝试错开网络请求

    # 开始粘贴获取到的4个武器图片
    img_num = 0
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
        if img_num >= 4: # 为4代表处理完毕了
            break # 退出循环
        await asyncio.sleep(0.2)
    # 写入vp和r点
    draw = ImageDraw.Draw(bg)
    # vp
    vp_c = (f"{vp}") 
    draw.text((537, 670), vp_c, font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    # rp
    rp_c = (f"{rp}") 
    rp_pos = (710, 670)
    if rp < 100: #改变位置，避免数字覆盖r点的icon
        rp_pos = (722, 670)
    draw.text(rp_pos, rp_c, font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    # 删除用于获取返回值的临时键值
    if ran in shop_img_temp:
        del shop_img_temp[ran]
    # 画完图之后返回结果
    bg.save(f"./{player_uuid}.png",format='PNG')
    return {"status": True, "value": bg}