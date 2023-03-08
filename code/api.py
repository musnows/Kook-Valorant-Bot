import json
import traceback
from aiohttp import web
from utils.Gtime import getTime
from utils.api import ApiHandler
from utils.log.Logging import _log

# 初始化节点
routes = web.RouteTableDef()


# 基础返回
@routes.get('/')
async def hello_world(request):  # put application's code here
    _log.info(f"request | root-url")
    return web.Response(body=json.dumps(
        {
            'code': 0,
            'message': 'Hello! Use path /shop or /shop-img to get valorant daily shop',
            'info':
            '在path后添加/shop-img或者/shop来获取每日商店，前者会直接跳转，后者返回一个带图片url的json。示例: /shop?account=Riot账户&passwd=Riot密码&img_src=可选参数，自定义背景图',
            'docs': 'https://github.com/Aewait/Kook-Valorant-Bot/blob/main/docs/valorant-shop-img-api.md'
        },
        indent=2,
        sort_keys=True,
        ensure_ascii=False),
                        status=200,
                        content_type='application/json')


# 提供4个皮肤uuid，返回图片
@routes.get('/shop-draw')
async def get_shop_draw(request):
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
                            status=200,
                            content_type='application/json')


# 直接跳转图片（浏览器访问，get方法不安全）
@routes.get('/shop-img')
async def get_shop_img(request):
    _log.info(f"request | /shop-img")
    try:
        ret = await ApiHandler.login_request(request,"GET")
        if ret['code'] == 0:
            return web.Response(headers={'Location': ret['message']}, status=303)  # 303是直接跳转到图片
        else:
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
                            status=200,
                            content_type='application/json')


# 登录接口
@routes.post('/login')
async def post_login(request):
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
                            status=200,
                            content_type='application/json')

# 邮箱验证登录
@routes.post('/tfa')
async def post_tfa_code(request):
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
                            status=200,
                            content_type='application/json')
    
@routes.post('/shop')
async def post_shop(request):
    _log.info(f"request | /shop")
    try:
        body = await request.content.read()
        params = json.loads(body.decode('UTF8'))
        # 判断必须要的参数是否齐全
        if 'account' not in params or 'token' not in params: # 不全，报错
            _log.error(f"params needed: token/account/passwd")
            ret = {
                'code': 400,
                'message': 'params needed: token/account/passwd',
                'info': '缺少参数！示例: /shop-img?token=api凭证&account=Riot账户&passwd=Riot密码&img_src=自定义背景图（可选）',
                'docs': 'https://github.com/Aewait/Kook-Valorant-Bot/blob/main/docs/valorant-shop-img-api.md'
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
                            status=200,
                            content_type='application/json')

# 用于控制db中ShopCmp的更新
@routes.post('/shop-cmp')
async def post_shop_cmp(request):
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
                            status=200,
                            content_type='application/json')



# 爱发电的wh
from utils.FileManage import bot
@routes.post('/afd')
async def aifadian_webhook(request):
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
                            content_type='application/json')


app = web.Application()
app.add_routes(routes)
if __name__ == '__main__':
    try: # host需要设置成0.0.0.0，否则只有本地才能访问
        _log.info(f"API Service Start")
        web.run_app(app, host='0.0.0.0', port=14726)
    except:
        _log.exception("Exception occur")