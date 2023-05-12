import asyncio
import copy
import io
import os
import random
import threading
import time
import aiohttp
import requests
import zhconv
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from .valorant.api import Local
from .Gtime import get_time
from .log.Logging import _log

DRAW_SLEEP_TIME = 0.3
"""每次画图遍历的休眠时间"""
DRAW_WAIT_TIME = 0.2
"""skinuuid交付后，等待画图完成的休眠时间"""

font_color = '#ffffff' 
"""文字颜色：白色"""
#用于临时存放图片的dict
shop_img_temp_11 = {}
shop_img_temp_169 = {}
weapon_icon_temp_11 = {}
weapon_icon_temp_169 = {}
skin_level_icon_temp = {}

bg_main_169 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/lSj90Xr9yA0zk0k0.png').content)) 
"""16-9 商店默认背景"""
bg_main_11 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/m8o9eCuKHQ0rs0rs.png').content)) 
"""1-1 商店默认背景"""
bg_window_169_without_logo = Image.open(
    io.BytesIO(requests.get('https://img.kookapp.cn/assets/2022-10/uFfgpWWlDy0zk0k0.png').content))
"""16-9 图片透明背景框，无水印"""
bg_window_169 = Image.open(
    io.BytesIO(requests.get('https://img.kookapp.cn/assets/2022-09/rLxOSFB1cC0zk0k0.png').content))
"""16-9 图片透明背景框,有水印"""
bg_window_11 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/FjPcmVwDkf0rs0rs.png').content))
"""1-1 透明背景框, 有水印"""
skin_err_11 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2023-04/ANlEitSBx60dw0dw.png').content))
"""1-1单个武器错误图片"""
skin_err_169 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2023-04/hj5GwwCN7Z0b406o.png').content))
"""16-9单个武器错误图片"""


standard_length = 1000 
"""图片默认边长 px"""
# 用math.floor 是用来把float转成int 我也不晓得为啥要用 但是不用会报错（我以前不用也不会）
# 所有的数都  * standard_length / 1000 是为了当标准边长变动时这些参数会按照比例缩放
standard_length_sm = int(standard_length / 2)  # 组成四宫格小图的边长
stardard_blank_sm = 60 * standard_length / 1000  # 小图左边的留空
stardard_icon_resize_ratio = 0.59 * standard_length / 1000  # 枪的默认缩放
standard_icon_top_blank = int(180 * standard_length / 1000)  # 枪距离图片顶部的像素
standard_text_position = (int(124 * standard_length / 1000), int(317 * standard_length / 1000))  # 默认文字位置
standard_price_position = (int(280 * standard_length / 1000), int(120 * standard_length / 1000))  # 皮肤价格文字位置
standard_level_icon_reszie_ratio = 0.13 * standard_length / 1000  # 等级icon图标的缩放
standard_level_icon_position = (int(350 * standard_length / 1000), int(120 * standard_length / 1000))  # 等级icon图标的坐标


async def img_requestor(img_url):
    """图片获取器"""
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as r:
            return await r.read()

def bg_comp(bg, img, x, y):
    """往底图的指定位置粘贴单个皮肤的图片"""
    position = (x, y)
    bg.paste(img, position, img)
    return bg

def get_weapon_img(skinuuid: str, skin_icon: str):
    """获取武器皮肤的图片"""
    if skin_icon == None: 
        _log.error(f"None-icon | {skinuuid}") # 出现None
    if os.path.exists(f'./log/img_temp/weapon/{skinuuid}.png'):
        layer_icon = Image.open(f'./log/img_temp/weapon/{skinuuid}.png')  # 打开本地皮肤图片
    else:
        layer_icon = Image.open(io.BytesIO(requests.get(skin_icon).content))  # 打开url皮肤图片
        layer_icon.save(f'./log/img_temp/weapon/{skinuuid}.png', format='PNG')
    return layer_icon

def resize_skin(standard_x, img, standard_y:int=-1):
    """缩放皮肤图片，部分皮肤图片大小不正常"""
    standard_y = standard_x if standard_y == -1 else standard_y
    log_info = "[resize_skin] "
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
    _log.info(log_info)
    img = img.resize((w_s, h_s), Image.Resampling.LANCZOS)
    return img

def resize_standard(standard_x, standard_y, img):
    """将背景图片缩放到标准大小，否则粘贴的时候大小不统一会报错"""
    w, h = img.size
    log_info = "[resize_std] "
    log_info += f"原始图片大小:({w},{h}) - "
    ratio = w / h
    if ratio <= standard_x / standard_y:
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


def sm_comp_169(skin_img_url:str, skin_name:str, price:str|int, skin_level_icon:str, skinuuid:str):
    """处理16-9图片，这个函数能够生成单个皮肤的图片，最后再一起粘贴到主图中"""
    try:
        bg = Image.new(mode='RGBA', size=(400, 240))  # 新建一个画布
        # 处理皮肤图片
        start = time.perf_counter()  #开始计时
        layer_icon = get_weapon_img(skinuuid=skinuuid, skin_icon=skin_img_url)
        end = time.perf_counter()  # 结束获取皮肤图片计时
        log_time = f"[GetWeapen] {format(end - start, '.4f')} "  # 记录获取皮肤图片用时

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
        if skin_level_icon not in skin_level_icon_temp:  #本地没有，获取
            level_icon = Image.open(io.BytesIO(requests.get(skin_level_icon).content))  # 打开皮肤等级图标
            skin_level_icon_temp[skin_level_icon] = level_icon
        else:  # 本地有，直接用本地的
            level_icon = skin_level_icon_temp[skin_level_icon]
        end = time.perf_counter()  # 结束获取皮肤等级图片的计时
        log_time += f"- [GetIters] {format(end - start, '.4f')} "  # 记录皮肤等级图片用时
        _log.info(log_time)  #打印用时

        # 缩放皮肤等级图标
        level_icon = level_icon.resize((25, 25), Image.Resampling.LANCZOS)
        level_icon = level_icon.convert('RGBA')
        bg.paste(level_icon, (368, 11), level_icon)  # 在指定位置粘贴皮肤等级图标
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
        global weapon_icon_temp_169  #皮肤图片的抽屉，如果uuid不存在，就插入
        if skinuuid not in weapon_icon_temp_169:
            weapon_icon_temp_169[skinuuid] = bg
        return bg # 返回图片
    except:
        _log.exception(f"err in 16-9 img draw | sk_uuid:{skinuuid} sk_img:{skin_img_url} sk_name:{skin_name} price:{price} | sk_lv:{skin_level_icon}")
        return skin_err_169


def sm_comp_11(skin_img_url:str, skin_name:str, price:str|int, skin_level_icon:str, skinuuid:str):
    """1比1的单个武器图片生成"""
    try:
        bg = Image.new(mode='RGBA', size=(standard_length_sm, standard_length_sm))  # 新建一个画布
        # 处理皮肤图片
        start = time.perf_counter()  #开始计时
        layer_icon = get_weapon_img(skinuuid=skinuuid, skin_icon=skin_img_url)
        end = time.perf_counter()
        log_time = f"[GetWeapen] {format(end - start, '.4f')} "

        stardard_icon_x = 300  #图像标准宽（要改大小就改这个
        layer_icon = resize_skin(300, layer_icon)
        # 按缩放比例后的长宽进行resize（resize就是将图像原长宽拉伸到新长宽） Image.Resampling.LANCZOS 是一种处理方式
        left_position = int((standard_length_sm - stardard_icon_x) / 2)
        # 用小图的宽度减去皮肤图片的宽度再除以二 得到皮肤图片x轴坐标  y轴坐标 是固定值 standard_icon_top_blank
        bg.paste(layer_icon, (left_position, standard_icon_top_blank), layer_icon)  # bg.paste代表向bg粘贴一张图片

        # 处理武器level的图片(存到本地dict里面方便调用)
        start = time.perf_counter()  #开始计时
        if skin_level_icon not in skin_level_icon_temp:
            level_icon = Image.open(io.BytesIO(requests.get(skin_level_icon).content))  # 打开武器等级图片
            skin_level_icon_temp[skin_level_icon] = level_icon
        else:
            level_icon = skin_level_icon_temp[skin_level_icon]
        end = time.perf_counter()
        log_time += f"- [GetIters] {format(end - start, '.4f')} "
        _log.info(log_time)  # 打印获取皮肤和皮肤等级用了多久时间

        w, h = level_icon.size  # 读取武器等级图片长宽
        new_w = int(w * standard_level_icon_reszie_ratio)  # 按比例缩放的长
        new_h = int(h * standard_level_icon_reszie_ratio)  # 按比例缩放的宽
        level_icon = level_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
        level_icon = level_icon.convert('RGBA')
        bg.paste(level_icon, standard_level_icon_position, level_icon)

        name = zhconv.convert(skin_name, 'zh-cn')  # 将名字简体化
        name_list = name.split(' ')  # 将武器名字分割换行
        _log.debug(str(name_list))
        if '' in name_list:  # 避免出现返回值后面带空格的情况，如'重力鈾能神經爆破者 制式手槍 '
            name_list.remove('')

        text = ""
        if len(name_list[0]) > 5:
            text = name_list[0] + '\n'  # 如果皮肤名很长就不用加空格
        else:
            text = ' '.join(name_list[0]) + '\n'  # 向皮肤名字添加空格增加字间距
        # 判断皮肤名字有几个分割
        if len(name_list) > 2:
            i = 1
            while i <= len(name_list) - 2:
                name_list[0] = name_list[0] + ' ' + name_list[i]
                _log.debug(name_list[0])
                i += 1
            interval = len(name_list[0])
            name_list[1] = name_list[len(name_list) - 1]
            text = name_list[0] + '\n'
        if len(name_list) > 1:  # 有些刀皮肤只有一个元素
            text += '              '  # 添加固定长度的缩进，12个空格
            if len(name_list[1]) < 4:
                text += ' '.join(name_list[1])  # 插入第二行字符
            else:
                text += name_list[1]  # 单独处理制式手槍（不加空格）

        draw = ImageDraw.Draw(bg)  # 让bg这个图层能被写字
        # 第一个参数 standard_text_position 是固定参数坐标 ， 第二个是文字内容 ， 第三个是字体 ， 第四个是字体颜色
        draw.text(standard_text_position,
                text,
                font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 30),
                fill=font_color)
        text = f"{price}"  # 价格
        draw.text(standard_price_position,
                text,
                font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 30),
                fill=font_color)
        # bg.show() #测试用途，展示图片(linux貌似不可用)
        if not os.path.exists(f'./log/img_temp/comp/{skinuuid}.png'):
            bg.save(f'./log/img_temp/comp/{skinuuid}.png')
        global weapon_icon_temp_11  # 1-1图片的抽屉
        if skinuuid not in weapon_icon_temp_11:
            weapon_icon_temp_11[skinuuid] = bg
        return bg
    except:
        _log.exception(f"err in 1-1 img draw | sk_uuid:{skinuuid} sk_img:{skin_img_url} sk_name:{skin_name} price:{price} | sk_lv:{skin_level_icon}")
        return skin_err_11 


####################################################################################################

def skin_comp_err_handler(ran:int|str,is_169:bool):
    """如果出现了错误，依照16-9或者1-1，插入4个错误的图片"""
    try:
        if is_169:
            global shop_img_temp_169
            shop_img_temp_169[ran].clear() # 清空
            shop_img_temp_169[ran].extend([skin_err_169]*4)
        else:
            global shop_img_temp_11
            shop_img_temp_11[ran].clear()
            shop_img_temp_11[ran].extend([skin_err_11]*4)
        _log.info(f"[skin.comp] add err img | ran:{ran} 169:{is_169}")
    except:
        _log.exception(f"err | ran:{ran} 169:{is_169}")

def skin_uuid_to_comp(skinuuid, ran, is_169=False):
    """在本地文件中查找皮肤的图片，没有图片就执行画图，并插入到temp中
    - skinuuid: 皮肤uuid
    - ran: 用于在全局变量中标识此次画图的key
    - is_169: 是否为16-9的图片画图
    """
    try:
        res_item = Local.lc_fetch_skin(skinuuid)  # 从本地文件中查找皮肤信息
        price = -1 # 价格初始化为-1，代表有错误
        try:
            res_price = Local.lc_fetch_item_price(skinuuid)  # 在本地文件中查找皮肤价格
            price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']  # 取出价格
        except:
            _log.exception(f"Err fetch_price | skin:{skinuuid} ran:{ran} 169:{is_169}")
        # 在本地文件中查找皮肤等级
        res_iters = Local.lc_fetch_skin_iters(skinuuid)  
        # 画单个皮肤的图片
        if is_169:
            img = sm_comp_169(res_item["data"]["displayIcon"], res_item["data"]["displayName"], price,
                            res_iters['data']['displayIcon'], skinuuid)
            global shop_img_temp_169  # 这里是把处理好的图片存到当前执行用户的临时库中
            shop_img_temp_169[ran].append(img)
        else:
            img = sm_comp_11(res_item["data"]["displayIcon"], res_item["data"]["displayName"], price,
                            res_iters['data']['displayIcon'], skinuuid)
            global shop_img_temp_11  #这里是把处理好的图片存到本地
            shop_img_temp_11[ran].append(img)
    except:
        _log.exception(f"err while drawing | skin:{skinuuid} | ran:{ran}")
        skin_comp_err_handler(ran,is_169)


async def get_shop_img_169(list_shop: dict, vp: int, rp: int, bg_img_src="err"):
    """获取16比9的每日商店的图片 
    
    args:
     - list_shop: user daily shop skin dict
     - bg_img_src: background img url

    returns dict:
     - {"status":False,"value":"err_str"}
     - {"status":True,"value":bg}
    """
    bg_img = bg_main_169  # 默认的带框底图
    # 有自定义背景图，背景图缩放后保存
    if bg_img_src != "err":
        try:  #打开图片进行测试
            bg_img = Image.open(io.BytesIO(await img_requestor(bg_img_src)))
        except UnidentifiedImageError as result:
            err_str = f"ERR! [{get_time()}] get_shop_img_169 bg_img check\n```\n{result}\n```"
            _log.exception("Exception in bg_img check")
            return {"status": False, "value": f"当前使用的图片无法获取！请重新上传您的背景图\n{err_str}"}
        # 打开成功
        bg_img = resize_standard(1280, 720, bg_img)  #缩放到720p
        bg_img = bg_img.convert('RGBA')
        # alpha_composite才能处理透明的png。参数1是底图，参数2是需要粘贴的图片
        bg_img = Image.alpha_composite(bg_img, bg_window_169)  #把框粘贴到自定义背景图上
    # 两种情况都需要把背景图图片加载到bg中
    bg = copy.deepcopy(bg_img)
    # 开始画图
    x = 50
    y = 100
    ran = 0  # 设立ran的基准值为0
    global shop_img_temp_169,weapon_icon_temp_169
    #循环判断创建的随机值在不在其中，如果在，那就还需要继续生成，直到产生一个不在其中的
    while (ran in shop_img_temp_169):
        ran = random.randint(1, 9999)  # 创建一个1-9999的随机值
    # 创建键值，用于保存多线程的返回值
    shop_img_temp_169[ran] = []

    # 开始遍历4个皮肤uuid
    for skinuuid in list_shop:
        img_path = f'./log/img_temp_vip/comp/{skinuuid}.png'
        if skinuuid in weapon_icon_temp_169:  # 16-9需要用的全局变量
            shop_img_temp_169[ran].append(weapon_icon_temp_169[skinuuid])
        elif os.path.exists(img_path):  # 全局变量里面没有，要去本地路径里面找
            img_cur = Image.open(img_path)
            shop_img_temp_169[ran].append(img_cur)
            weapon_icon_temp_169[skinuuid] = img_cur # 插入到全局变量中
        else:  # 都没有，画图
            th = threading.Thread(target=skin_uuid_to_comp, args=(skinuuid, ran, True))
            th.start()
        await asyncio.sleep(DRAW_SLEEP_TIME) # 睡眠一会，尝试错开网络请求

    # 开始粘贴获取到的4个皮肤图片
    img_num = 0
    while True:
        img_temp = [i for i in shop_img_temp_169[ran]]
        for i in img_temp:
            shop_img_temp_169[ran].pop(shop_img_temp_169[ran].index(i))
            #i.save(f"./t{x}_{y}.png", format='PNG')
            bg = bg_comp(bg, i, x, y)
            if x == 50:
                x += 780
            elif x == 830:
                x = 50
                y += 279
            img_num += 1
        if img_num >= 4:  # 为4代表处理完毕了
            break  # 退出循环
        await asyncio.sleep(DRAW_WAIT_TIME) 
    # 写入vp和r点
    draw = ImageDraw.Draw(bg)
    # vp
    draw.text((537, 670), str(vp), font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    # rp
    rp_pos = (710, 670)
    if int(rp) < 100:  #改变位置，避免数字覆盖r点的icon
        rp_pos = (722, 670)
    draw.text(rp_pos, str(rp), font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    # 删除用于获取返回值的临时键值
    if ran in shop_img_temp_169:
        del shop_img_temp_169[ran]
    # 画完图之后返回结果
    # bg.save(f"./2222.png",format='PNG')
    return {"status": True, "value": bg}


async def get_shop_img_11(list_shop: dict, bg_img_src="err"):
    """ 1-1商店画图
    
    args:
     - list_shop: user daily shop skin dict
     - bg_img_src: background img url

    returns dict:
     - {"status":False,"value":"err_str"}
     - {"status":True,"value":bg}
    """
    bg_img = bg_main_11
    # 有自定义背景图，背景图缩放后保存
    if bg_img_src != "err":
        try:  #打开图片进行测试
            bg_img = Image.open(io.BytesIO(await img_requestor(bg_img_src)))
        except UnidentifiedImageError as result:
            err_str = f"ERR! [{get_time()}] get_shop_img_169 bg_img check\n```\n{result}\n```"
            _log.exception("Exception in bg_img check") 
            return {"status": False, "value": f"当前使用的图片无法获取！请重新上传您的背景图\n{err_str}"}
        # 打开成功
        bg_img = resize_standard(1000, 1000, bg_img)  #缩放到1000*1000 必须有，否则报错images do not match
        bg_img = bg_img.convert('RGBA')
        # alpha_composite才能处理透明的png。参数1是底图，参数2是需要粘贴的图片
        bg_img = Image.alpha_composite(bg_img, bg_window_11)  #把框粘贴到自定义背景图上
    # 两种情况都需要把背景图图片加载到bg中
    bg = copy.deepcopy(bg_img)
    # 开始画图,初始化变量
    x = 0
    y = 0
    ran = 0  # 随机数基准值
    # 开始后续画图操作
    global shop_img_temp_11, weapon_icon_temp_11
    #循环判断创建的随机值在不在其中，如果在，那就还需要继续生成，直到产生一个不在其中的
    while (ran in shop_img_temp_11):
        ran = random.randint(1, 9999)  # 创建一个1-9999的随机值

    shop_img_temp_11[ran] = []
    # 插入皮肤图片
    for skinuuid in list_shop:
        img_path = f'./log/img_temp/comp/{skinuuid}.png'
        if skinuuid in weapon_icon_temp_11:  # 1-1需要用的抽屉
            shop_img_temp_11[ran].append(weapon_icon_temp_11[skinuuid])
        elif os.path.exists(img_path):
            img_cur = Image.open(img_path)
            shop_img_temp_11[ran].append(img_cur)
            weapon_icon_temp_11[skinuuid] = img_cur # 插入到全局变量中
        else:
            th = threading.Thread(target=skin_uuid_to_comp, args=(skinuuid, ran, False))
            th.start()
        await asyncio.sleep(DRAW_SLEEP_TIME)  #尝试错开网络请求
    # 粘贴到主图上
    img_num = 0
    while True:
        img_temp = copy.deepcopy(shop_img_temp_11)
        for i in img_temp[ran]:
            shop_img_temp_11[ran].pop(shop_img_temp_11[ran].index(i))
            bg = bg_comp(bg, i, x, y)
            if x == 0:
                x += standard_length_sm
            elif x == standard_length_sm:
                x = 0
                y += standard_length_sm
            img_num += 1
        if img_num >= 4:
            break
        await asyncio.sleep(DRAW_WAIT_TIME)
    #循环结束后删除
    if ran in shop_img_temp_11:
        del shop_img_temp_11[ran]
    # 画完图之后返回结果
    # bg.save(f"./11111.png",format='PNG')
    return {"status": True, "value": bg}