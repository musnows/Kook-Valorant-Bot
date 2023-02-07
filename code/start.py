import asyncio
from aiohttp import web
from main import bot,GetTime
from api import app

# 屏蔽报错
# ignore warning 'DeprecationWarning: There is no current event loop'
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == '__main__':
    print(f"[START] service start at {GetTime()}")
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(web._run_app(app, host='0.0.0.0', port=14725), bot.start()))
