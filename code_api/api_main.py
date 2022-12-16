import json

import aiofiles
from aiohttp import web
from riot_auth import auth_exceptions, RiotAuth
from img_handler import *
from api_token import token_ck,UserTokenDict,save_token_files

routes = web.RouteTableDef()

# 获取拳头的token
# 此部分代码来自 https://github.com/floxay/python-riot-auth
async def authflow(user: str, passwd: str):
    CREDS = user, passwd
    auth = RiotAuth()
    await auth.authorize(*CREDS)
    return auth

# 检测速率（一分钟只允许5次）
async def check_token_rate(token:str):
    ret = await token_ck(token)
    if ret:
        cur_time = time.time()
        time_diff = cur_time - UserTokenDict['data'][token]['rate_time']
        UserTokenDict['data'][token]['sum']+=1
        if UserTokenDict['data'][token]['rate_nums']==0:#初次使用
            UserTokenDict['data'][token]['rate_time']=cur_time
            UserTokenDict['data'][token]['rate_nums']=1
            save_token_files()
            return {'status':True,'message':'first use','info':'一切正常'}
        elif time_diff <=60:#时间在60s以内
            if UserTokenDict['data'][token]['rate_nums']>10:
                return {'status':False,'message': 'token rate limited!','info':'速率限制，请稍后再试'}
            else:#没有引发速率限制
                UserTokenDict['data'][token]['rate_nums']+=1
                return {'status':True,'message':'time_diff <= 60, in rate','info':'一切正常'}
        else:#时间超过60
            save_token_files()
            UserTokenDict['data'][token]['rate_time']=cur_time
            UserTokenDict['data'][token]['rate_nums']=0
            return {'status':True,'message':'time_diff > 60','info':'一切正常'}
    else:
        return {'status':False,'message':'token not in dict','info':'无效token'}
        


# 基本操作
async def base_img_request(request):
    params = request.rel_url.query
    if 'account' not in params or 'passwd' not in params or 'token' not in params:
        print(f"ERR! [{GetTime()}] params needed: token/account/passwd")
        return {'code': 400, 'message': 'params needed: account/passwd','info':'缺少参数！示例: /shop-img?token=你购买的api凭证&account=Riot账户&passwd=Riot密码&img_src=可选参数，自定义背景图'}

    account=params['account']
    passwd=params['passwd']
    token = params['token']
    ck_ret = await check_token_rate(token)
    if not ck_ret['status']: 
        return {'code': 200, 'message': ck_ret['message'],'info':ck_ret['info']}
    
    #默认背景
    img_src = 'https://img.kookapp.cn/assets/2022-10/KcN5YoR5hC0zk0k0.jpg'
    if 'img_src' in params:
        img_src = params['img_src']
    try:
        auth = await authflow(account,passwd)
    except auth_exceptions.RiotAuthenticationError as result:
        print(f"ERR! [{GetTime()}] login - {result}")
        text = f"账户密码错误 {result}"
        return {'code': 200, 'message': 'riot_auth.auth_exceptions.RiotAuthenticationError','info':text}
    except auth_exceptions.RiotMultifactorError as result:
        print(f"ERR! [{GetTime()}] login - {result}")
        text = f"当前不支持开启了`邮箱双重验证`的账户  {result}"
        return {'code': 200, 'message':'riot_auth.auth_exceptions.RiotMultifactorError','info': text}
    except auth_exceptions.RiotRatelimitError as result:
        print(f"ERR! [{GetTime()}] login - riot_auth.riot_auth.auth_exceptions.RiotRatelimitError")
        return {'code': 200, 'message': "riot_auth.auth_exceptions.RiotRatelimitError",'info':'riot登录api超速，请稍后重试'}
    
    print(f'[{GetTime()}] [riot_auth] user auth success')
    userdict = {
        'auth_user_id': auth.user_id,
        'access_token': auth.access_token,
        'entitlements_token': auth.entitlements_token
    }
    resp = await fetch_daily_shop(userdict)  #获取每日商店
    print(f'[{GetTime()}] [Api] fetch_daily_shop success')
    list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
    ret = await get_daily_shop_vip_img(list_shop, userdict,account,img_src)
    if ret['status']:
        bg = ret['value']
        img_src_ret = await kook_create_asset(bg)  # 上传图片
        if img_src_ret['code']==0:
            print(f'[{GetTime()}] [Api] kook_create_asset success')
            dailyshop_img_src = img_src_ret['data']['url']
            print(f'[{GetTime()}] [img-url] {dailyshop_img_src}')
            return {'code':0,'message':dailyshop_img_src,'info':'商店图片获取成功'}     
        else:
            print(f'[{GetTime()}] [Api] kook_create_asset failed')
            return {'code':200,'message': 'img upload err','info':'图片上传错误'}
    else:  #出现图片违规或者url无法获取
        err_str = ret['value']
        print(f'[{GetTime()}] [ERR]',err_str)
        return {'code':200,'message': 'img src err','info':'自定义图片获取失败'}
    
    
# 基础返回  
@routes.get('/')
def hello_world(request):  # put application's code here
    print(f"[{GetTime()}] [request] /")
    return web.Response(body=json.dumps({'code':0,'message': 'Hello! Use path /shop-url or /shop-img to get valorant daily shop','info':'在path后添加/shop-img或者/shop-url来获取每日商店，前者会直接跳转，后者返回一个带图片url的json。示例: /shop-url?account=Riot账户&passwd=Riot密码&img_src=可选参数，自定义背景图'},ensure_ascii=False), status=200, content_type='application/json')


# 直接跳转图片
@routes.get('/shop-img')
async def get_dailshop_img(request):
    print(f"[{GetTime()}] [request] /shop-img")
    try:
        ret = await base_img_request(request)
        if ret['code']==0:
            return web.Response(headers={'Location': ret['message']},status=303)
        else:
            return web.Response(body=json.dumps(ret,ensure_ascii=False), content_type='application/json')
    except:
        return web.Response(body=json.dumps({'code':200,'message': 'unkown err','info':'未知错误'},ensure_ascii=False), content_type='application/json')
    
# 获取图片url
@routes.get('/shop-url')
async def get_dailshop_img(request):
    print(f"[{GetTime()}] [request] /shop-url")
    try:
        ret = await base_img_request(request)
        return web.Response(body=json.dumps(ret,ensure_ascii=False), content_type='application/json')
    except:
        return web.Response(body=json.dumps({'code':200,'message': 'unkown err','info':'未知错误'},ensure_ascii=False), content_type='application/json')

@routes.get('/log_bot_img')
async def get_bot_log_img(request):
    print(f"[{GetTime()}] [request] /log_bot_img")
    try:
        async with aiofiles.open(f'../screenshot/log.png','rb') as f:
            return web.Response(body=await f.read(),status=200, content_type=f'image/png')
    except:
        return web.Response(body=json.dumps({'code':200,'message': 'unkown err','info':'未知错误'},ensure_ascii=False), content_type='application/json')




if __name__ == '__main__':
    print(f"[Start] starting at {GetTime()}")
    fetch_data()#获取变量
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host='127.0.0.1', port=14725)