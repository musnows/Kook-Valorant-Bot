import asyncio
from aiohttp import web
from main import bot
from api import app

# 屏蔽报错
# ignore warning 'DeprecationWarning: There is no current event loop'
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(asyncio.gather(web._run_app(app, host='127.0.0.1', port=14725),bot.start()))