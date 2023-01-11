import json
import time
import aiofiles
from endpoints.EzAuth import RiotAuth,EzAuth,auth_exceptions,auth2fa
from endpoints.ApiToken import token_ck,ApiTokenDict,save_token_files
from endpoints.Gtime import GetTime
from endpoints.KookApi import kook_create_asset
from endpoints.Val import fetch_daily_shop,fetch_vp_rp_dict
from endpoints.ShopImg import get_shop_img_11,get_shop_img_169


# 检测速率（一分钟只允许10次）
async def check_token_rate(token:str):
    ret = await token_ck(token)
    if ret:
        cur_time = time.time()
        time_diff = cur_time - ApiTokenDict['data'][token]['rate_time']
        ApiTokenDict['data'][token]['sum']+=1
        if ApiTokenDict['data'][token]['rate_nums']==0:#初次使用
            ApiTokenDict['data'][token]['rate_time']=cur_time
            ApiTokenDict['data'][token]['rate_nums']=1
            save_token_files()
            return {'status':True,'message':'first use','info':'一切正常'}
        elif time_diff <=60:#时间在60s以内
            if ApiTokenDict['data'][token]['rate_nums']>10:
                return {'status':False,'message': 'token rate limited!','info':'速率限制，请稍后再试'}
            else:#没有引发速率限制
                ApiTokenDict['data'][token]['rate_nums']+=1
                return {'status':True,'message':'time_diff <= 60, in rate','info':'一切正常'}
        else:#时间超过60
            save_token_files()
            ApiTokenDict['data'][token]['rate_time']=cur_time
            ApiTokenDict['data'][token]['rate_nums']=0
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
        auth = await auth2fa(account,passwd)
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
    res_vprp = await fetch_vp_rp_dict(userdict)
    vp = res_vprp['vp']
    rp = res_vprp['rp']
    ret = await get_shop_img_169(list_shop,vp=vp,rp=rp,bg_img_src=img_src)
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