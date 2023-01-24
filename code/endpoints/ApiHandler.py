import json
import time
import threading
import traceback
from endpoints.EzAuth import auth_exceptions, auth2fa, auth2faWait, Get2faWait_Key, User2faCode
from endpoints.ApiToken import token_ck, ApiTokenDict, save_token_files
from endpoints.Gtime import GetTime
from endpoints.KookApi import kook_create_asset
from endpoints.Val import fetch_daily_shop, fetch_vp_rp_dict
from endpoints.ShopImg import get_shop_img_11, get_shop_img_169

TOKEN_RATE_LIMITED = 10
# bot的token文件
from endpoints.FileManage import config
# 用来给kook上传文件的bot token
api_bot_token = config['api_bot_token']
Api2faDict = {'data': {}}  # 保存2fa用户登录的过程信息
# 默认的背景图
img_bak_169 = 'https://img.kookapp.cn/assets/2022-10/KcN5YoR5hC0zk0k0.jpg'
img_bak_11 = 'https://img.kookapp.cn/assets/2023-01/lzRKEApuEP0rs0rs.jpg'


# 检测速率（一分钟只允许10次）
async def check_token_rate(token: str):
    ret = await token_ck(token)
    if ret:
        cur_time = time.time()
        time_diff = cur_time - ApiTokenDict['data'][token]['rate_time']
        ApiTokenDict['data'][token]['sum'] += 1
        if ApiTokenDict['data'][token]['rate_nums'] == 0:  #初次使用
            ApiTokenDict['data'][token]['rate_time'] = cur_time
            ApiTokenDict['data'][token]['rate_nums'] = 1
            save_token_files("token init use")
            return {'status': True, 'message': 'first use', 'info': '一切正常'}
        elif time_diff <= 60:  #时间在60s以内
            if ApiTokenDict['data'][token]['rate_nums'] > TOKEN_RATE_LIMITED:
                return {'status': False, 'message': 'token rate limited!', 'info': '速率限制，请稍后再试'}
            else:  #没有引发速率限制
                ApiTokenDict['data'][token]['rate_nums'] += 1
                return {'status': True, 'message': 'time_diff <= 60, in rate', 'info': '一切正常'}
        else:  #时间超过60
            save_token_files("rate check")
            ApiTokenDict['data'][token]['rate_time'] = cur_time
            ApiTokenDict['data'][token]['rate_nums'] = 0
            return {'status': True, 'message': 'time_diff > 60', 'info': '一切正常'}
    else:
        return {'status': False, 'message': 'token not in dict', 'info': '无效token'}


# 基本画图操作
async def base_img_request(params, list_shop, vp1='0', rp1='0'):
    # 自定义背景
    if 'img_src' in params:
        img_src = params['img_src']
    else:
        img_src = img_bak_169  # 默认背景16-9
        if 'img_ratio' in params and params['img_ratio'] == '1':
            img_src = img_bak_11  # 默认背景1-1

    # 开始画图
    start = time.perf_counter()
    if 'img_ratio' in params and params['img_ratio'] == '1':
        ret = await get_shop_img_11(list_shop, bg_img_src=img_src)
    else:  # 只有16-9的图片需获取vp和r点
        ret = await get_shop_img_169(list_shop, vp=vp1, rp=rp1, bg_img_src=img_src)
    # 打印计时
    print(f"[{GetTime()}] [IMGdraw]", format(time.perf_counter() - start, '.2f'))  # 结果为浮点数，保留两位小数

    start = time.perf_counter()
    if ret['status']:
        bg = ret['value']
        img_src_ret = await kook_create_asset(api_bot_token, bg)  # 上传图片
        if img_src_ret['code'] == 0:
            print(f"[{GetTime()}] [Api] kook_create_asset success {format(time.perf_counter() - start, '.2f')}")
            dailyshop_img_src = img_src_ret['data']['url']
            print(f'[{GetTime()}] [img-url] {dailyshop_img_src}')
            return {'code': 0, 'message': dailyshop_img_src, 'info': '商店图片获取成功'}
        else:
            print(f'[{GetTime()}] [Api] kook_create_asset failed')
            return {'code': 200, 'message': 'img upload err', 'info': '图片上传错误'}
    else:  #出现图片违规或者url无法获取
        err_str = ret['value']
        print(f'[{GetTime()}] [ERR]', err_str)
        return {'code': 200, 'message': 'img src err', 'info': '自定义图片获取失败'}


# 画图接口(仅画图)
async def img_draw_request(request):
    params = request.rel_url.query
    if "list_shop" not in params or 'token' not in params:
        print(f"ERR! [{GetTime()}] params needed: token/list_shop")
        return {
            'code': 400,
            'message': 'params needed: token/list_shop',
            'info': '缺少参数！示例: /shop-draw?token=api凭证&list_shop=四个皮肤uuid的list&vp=vp（可选）&rp=rp（可选）&img_src=自定义背景图（可选）',
            'docs': 'https://github.com/Aewait/Kook-Valorant-Bot/blob/main/docs/valorant-shop-img-api.md'
        }

    list_shop = params['list_shop']
    token = params['token']
    ck_ret = await check_token_rate(token)
    if not ck_ret['status']:
        return {'code': 200, 'message': ck_ret['message'], 'info': ck_ret['info']}
    # vp和rp必须同时给予，只给一个不算
    if 'vp' not in params or 'rp' not in params:
        return await base_img_request(params, list_shop)
    else:
        return await base_img_request(params, list_shop, params['vp'], params['rp'])


# 登录+画图
async def login_img_request(request):
    params = request.rel_url.query
    if 'account' not in params or 'passwd' not in params or 'token' not in params:
        print(f"ERR! [{GetTime()}] params needed: token/account/passwd")
        return {
            'code': 400,
            'message': 'params needed: token/account/passwd',
            'info': '缺少参数！示例: /shop-img?token=api凭证&account=Riot账户&passwd=Riot密码&img_src=自定义背景图（可选）',
            'docs': 'https://github.com/Aewait/Kook-Valorant-Bot/blob/main/docs/valorant-shop-img-api.md'
        }

    account = params['account']
    passwd = params['passwd']
    token = params['token']
    ck_ret = await check_token_rate(token)
    if not ck_ret['status']:
        return {'code': 200, 'message': ck_ret['message'], 'info': ck_ret['info']}

    try:
        key = await Get2faWait_Key()
        Api2faDict['data'][account] = key
        # 因为如果使用异步，该执行流会被阻塞住等待，应该使用线程来操作
        th = threading.Thread(target=auth2fa, args=(account, passwd, key))
        th.start()
        resw = await auth2faWait(key=key)  # 随后主执行流来这里等待
        res_auth = resw['auth']
        del Api2faDict['data'][account]  # 登录成功，删除账户键值
    except auth_exceptions.RiotRatelimitError as result:
        print(f"ERR! [{GetTime()}] login - riot_auth.riot_auth.auth_exceptions.RiotRatelimitError")
        return {'code': 200, 'message': "riot_auth.auth_exceptions.RiotRatelimitError", 'info': 'riot登录api超速，请稍后重试'}
    except Exception as result:
        print(f"ERR! [{GetTime()}] login\n{traceback.format_exc()}")
        return {'code': 200, 'message': f"{result}", 'info': 'riot登录错误，详见message'}

    print(f'[{GetTime()}] [Api] k:{key} - user auth success')
    userdict = {
        'auth_user_id': res_auth.user_id,
        'access_token': res_auth.access_token,
        'entitlements_token': res_auth.entitlements_token
    }
    resp = await fetch_daily_shop(userdict)  #获取每日商店
    print(f'[{GetTime()}] [Api] fetch_daily_shop success')
    list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
    res_vprp = {'vp': '0', 'rp': '0'}  # 先初始化为0
    if 'img_ratio' not in params or params['img_ratio'] != '1':
        res_vprp = await fetch_vp_rp_dict(userdict)  # 只有16-9的图片需获取vp和r点
    # 不管什么情况，都请求这个
    return await base_img_request(params, list_shop, res_vprp['vp'], res_vprp['rp'])


# 邮箱验证的post
async def tfa_code_requeset(request):
    params = request.rel_url.query
    if 'account' not in params or 'vcode' not in params or 'token' not in params:
        print(f"ERR! [{GetTime()}] params needed: token/account/vcode")
        return {
            'code': 400,
            'message': 'params needed: token/account/vcode',
            'info': '缺少参数！示例: /tfa?token=api凭证&account=Riot账户&vcode=邮箱验证码',
            'docs': 'https://github.com/Aewait/Kook-Valorant-Bot/blob/main/docs/valorant-shop-img-api.md'
        }

    account = params['account']
    vcode = params['vcode']
    token = params['token']

    global Api2faDict
    if account not in Api2faDict['data']:
        return {
            'code': 200,
            'message': 'Riot account not in Api2faDict',
            'info': '拳头账户不在dict中，请先请求/shop-img或/shop-url接口'
        }

    key = Api2faDict['data'][account]
    User2faCode[key]['vcode'] = vcode
    User2faCode[key]['2fa_status'] = True
    return {
        'code': 0,
        'message': 'email verify code post success,wait for shop img return',
        'info': '两步验证码获取成功，请等待主接口返回',
        'vcode': vcode
    }


from endpoints.FileManage import AfdWebhook
from khl.card import CardMessage, Card, Module, Types, Element


# 爱发电webhook
async def afd_request(request, bot):
    body = await request.content.read()
    params = json.loads(body.decode('UTF8'))
    global AfdWebhook
    AfdWebhook.append(params)

    text = ""
    if 'plan_title' in params['data']['order']:
        text = f"商品 {params['data']['order']['plan_title']}\n"
    user_id = params['data']['order']['user_id']
    user_id = user_id[0:6]
    text += f"用户 {user_id}\n"
    for i in params['data']['order']['sku_detail']:
        text += f"发电了{i['count']}个 {i['name']}\n"
    text += f"共计 {params['data']['order']['total_amount']} 猿"

    trno = params['data']['order']['out_trade_no']
    trno_f = trno[0:8]
    trno_b = trno[-4:]
    trno_f += "####"
    trno_f += trno_b

    cm = CardMessage()
    c = Card(Module.Header(f"爱发电有新动态啦！"), Module.Context(Element.Text(f"订单号: {trno_f}")), Module.Divider(),
             Module.Section(Element.Text(text, Types.Text.KMD)))
    cm.append(c)
    #print(json.dumps(cm))
    debug_ch = await bot.client.fetch_public_channel(config['debug_ch'])
    await bot.client.send(debug_ch, cm)
    print(f"[{GetTime()}] trno:{params['data']['order']['out_trade_no']} afd-cm-send")
    return {"ec": 200, "em": "success"}
