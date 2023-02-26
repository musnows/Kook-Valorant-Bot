import json
import traceback
from aiohttp import web
from utils.Gtime import GetTime
from utils.api.ApiHandler import tfa_code_requeset, afd_request, login_img_request, img_draw_request,shop_cmp_request

# 初始化节点
routes = web.RouteTableDef()


# 基础返回
@routes.get('/')
def hello_world(request):  # put application's code here
    print(f"[{GetTime()}] [request] /")
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
async def get_dailshop_img(request):
    print(f"[{GetTime()}] [request] /shop-draw")
    try:
        ret = await img_draw_request(request)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        print(f"[{GetTime()}] [Api] ERR in /shop\n{err_cur}")
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
async def get_dailshop_img(request):
    print(f"[{GetTime()}] [request] /shop-img")
    try:
        ret = await login_img_request(request)
        if ret['code'] == 0:
            return web.Response(headers={'Location': ret['message']}, status=303)  # 303是直接跳转到图片
        else:
            return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                                content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        print(f"[{GetTime()}] [Api] ERR in /shop-img\n{err_cur}")
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


# 获取图片url
@routes.post('/shop')
async def get_dailshop_img(request):
    print(f"[{GetTime()}] [request] /shop")
    try:
        ret = await login_img_request(request,"POST")
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        print(f"[{GetTime()}] [Api] ERR in /shop\n{err_cur}")
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


@routes.post('/tfa')
async def post_tfa_code(request):
    print(f"[{GetTime()}] [request] /tfa")
    try:
        ret = await tfa_code_requeset(request)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        print(f"[{GetTime()}] [Api] ERR in /tfa\n{err_cur}")
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
    print(f"[{GetTime()}] [request] /shop-cmp")
    try:
        ret = await shop_cmp_request(request)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json',status=200)
    except:
        err_cur = traceback.format_exc()
        print(f"[{GetTime()}] [Api] ERR in /shop-cmp\n{err_cur}")
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
from main import bot
@routes.post('/afd')
async def aifadian_webhook(request):
    print(f"[{GetTime()}] [request] /afd")
    try:
        ret = await afd_request(request, bot)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json')
    except:
        err_cur = traceback.format_exc()
        print(f"[{GetTime()}] [Api] ERR in /afd\n{err_cur}")
        return web.Response(body=json.dumps({
            "ec": 0,
            "em": "err ouccer"
        }, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json')


app = web.Application()
app.add_routes(routes)
if __name__ == '__main__':
    try: # host需要设置成0.0.0.0，否则只有本地才能访问
        print(f"[API Start] starting at {GetTime()}")
        web.run_app(app, host='0.0.0.0', port=14726)
    except:
        print(traceback.format_exc())