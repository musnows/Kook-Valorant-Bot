import json
import traceback
from aiohttp import web, web_request
from pkg.utils.Gtime import get_time
from pkg.utils.api import ApiHandler
from pkg.utils.log.Logging import _log

# 初始化节点
routes = web.RouteTableDef()


# 基础返回
@routes.get('/')
async def hello_world(request:web_request.Request):  # put application's code here
    _log.info(f"request | root-url")
    return web.Response(body=json.dumps(
        {
            'code': 0,
            'message': 'Hello! Use path /shop or /shop-img to get valorant daily shop',
            'info':
            '在path后添加/shop-img或者/shop来获取每日商店，前者会直接跳转，后者返回一个带图片url的json。示例: /shop?account=Riot账户&passwd=Riot密码&img_src=可选参数，自定义背景图',
            'docs': 'https://github.com/Valorant-Shop-CN/Kook-Valorant-Bot/blob/main/docs/valorant-shop-img-api.md'
        },
        indent=2,
        sort_keys=True,
        ensure_ascii=False),
                        status=200,
                        content_type='application/json')


# 提供4个皮肤uuid，返回图片
@routes.get('/shop-draw')
async def get_shop_draw(request:web_request.Request):
    _log.info(f"request | /shop-draw")
    try:
        ret = await ApiHandler.img_draw_request(request)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        _log.exception("Exception in /shop-draw")
        return web.Response(body=json.dumps(
            {
                'code': 200,
                'message': 'unkown err',
                'info': f'未知错误',
                'except': f'{err_cur}'
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False),
                            status=503,
                            content_type='application/json')


# 直接跳转图片
@routes.get('/shop-img')
async def get_shop_img(request:web_request.Request):
    _log.info(f"request | /shop-img")
    try:
        params = request.rel_url.query
        ret = await ApiHandler.login_request(request,"GET")
        if ret['code'] == 0:
            # 如果url不在，或者值不为1，则303跳转图片
            if 'url' not in params or str(params['url']) != '1':
                return web.Response(headers={'Location': ret['message']}, status=303)  # 303是直接跳转到图片
            else:
                return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                        content_type='application/json',status=200)
        else: # 出错误了
            return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                                content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        _log.exception("Exception in /shop-img")
        return web.Response(body=json.dumps(
            {
                'code': 200,
                'message': 'unkown err',
                'info': f'未知错误',
                'except': f'{err_cur}'
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False),
                            status=503,
                            content_type='application/json')


# 登录接口
@routes.post('/login')
async def post_login(request:web_request.Request):
    _log.info(f"request | /login")
    try:
        ret = await ApiHandler.login_request(request,"POST")
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        _log.exception("Exception in /login")
        return web.Response(body=json.dumps(
            {
                'code': 200,
                'message': 'unkown err',
                'info': f'未知错误',
                'except': f'{err_cur}'
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False),
                            status=503,
                            content_type='application/json')

# 邮箱验证登录
@routes.post('/tfa')
async def post_tfa_code(request:web_request.Request):
    _log.info(f"request | /tfa")
    try:
        ret = await ApiHandler.tfa_code_requeset(request)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        _log.exception("Exception in /tfa")
        return web.Response(body=json.dumps(
            {
                'code': 200,
                'message': 'unkown err',
                'info': f'未知错误',
                'except': f'{err_cur}'
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False),
                            status=503,
                            content_type='application/json')
    
@routes.post('/shop')
async def post_shop(request:web_request.Request):
    _log.info(f"request | /shop")
    try:
        body = await request.content.read()
        params = json.loads(body.decode('UTF8'))
        # 判断必须要的参数是否齐全
        if 'account' not in params or 'token' not in params: # 不全，报错
            _log.error(f"params needed: token/account")
            ret = {
                'code': 400,
                'message': 'params needed: token/account',
                'info': '缺少参数！请参考docs文档里面的参数表',
                'docs': 'https://github.com/Valorant-Shop-CN/Kook-Valorant-Bot/blob/main/docs/valorant-shop-img-api.md'
            }
            return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
        # 画图请求，不需要检测token速率
        ret = await ApiHandler.shop_get_request(params,params['account'])
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        _log.exception("Exception in /shop")
        return web.Response(body=json.dumps(
            {
                'code': 200,
                'message': 'unkown err',
                'info': f'未知错误',
                'except': f'{err_cur}'
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False),
                            status=503,
                            content_type='application/json')

# 用于控制db中ShopCmp的更新
@routes.post('/shop-cmp')
async def post_shop_cmp(request:web_request.Request):
    _log.info(f"request | /shop-cmp")
    try:
        ret = await ApiHandler.shop_cmp_request(request)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        _log.exception("Exception in /shop-cmp")
        return web.Response(body=json.dumps(
            {
                'code': 200,
                'message': 'unkown err',
                'info': f'未知错误',
                'except': f'{err_cur}'
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False),
                            status=503,
                            content_type='application/json')



# 爱发电的wh
from pkg.utils.file.Files import bot
@routes.post('/afd')
async def aifadian_webhook(request:web_request.Request):
    _log.info(f"request | /afd")
    try:
        ret = await ApiHandler.afd_request(request, bot)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json')
    except:
        _log.exception("Exception in /afd")
        return web.Response(body=json.dumps({
            "ec": 0,
            "em": "err ouccer"
        }, indent=2, sort_keys=True, ensure_ascii=False),
                            status=503,
                            content_type='application/json')


# 机器人加入的服务器/命令总数等等信息
from pkg.utils.log.BotLog import log_bot_list
WEB_ROOT = "./web/ahri"
async def html_response(path:str):
    try:
        with open(f'{WEB_ROOT}{path}','r') as f:
            return web.Response(body=f.read(),content_type='text/html')
    except:
        _log.exception(f"Exception in /bot | {path}")
        return web.Response(status=503)

@routes.get('/bot')
async def bot_log_html1(request:web_request.Request):
    _log.info(f"request | /bot")
    return await html_response("/index.html")
@routes.get('/bot/gu')
async def bot_log_html2(request:web_request.Request):
    _log.info(f"request | /bot")
    return await html_response("/gu/index.html")
@routes.get('/bot/ngu')
async def bot_log_html3(request:web_request.Request):
    _log.info(f"request | /bot")
    return await html_response("/ngu/index.html")
# 机器人命令使用情况json
@routes.get('/bot/log')
async def bot_log_get(request:web_request.Request):
    _log.info(f"request | /bot/log")
    try:
        ret_dict = await log_bot_list(log_img_draw=False) # 不画图
        ret = {
            "guild_total":ret_dict["guild"]["guild_total"],
            "guild_active":ret_dict["guild"]["guild_active"],
            "user_total":ret_dict["user"]["user_total"],
            "cmd_total":ret_dict["cmd_total"]
        }
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                    content_type='application/json')
    except:
        _log.exception("Exception in /bot/log")
        return web.Response(status=503)


app = web.Application()
app.add_routes(routes)
if __name__ == '__main__':
    try: # host需要设置成0.0.0.0，否则只有本地才能访问
        HOST,PORT = '0.0.0.0',14726
        _log.info(f"API Service Start at {HOST}:{PORT}")
        web.run_app(app, host=HOST, port=PORT)
    except:
        _log.exception("Exception occur")