import asyncio
from aiohttp import web
from main import bot,_log
from api import app

# 屏蔽报错
# ignore warning 'DeprecationWarning: There is no current event loop'
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == '__main__':
    HOST,PORT = '0.0.0.0',14725
    _log.info(f"[START] service start at {HOST}:{PORT}")
    # asyncio.get_event_loop().run_until_complete(
    #     asyncio.gather(web._run_app(app, host=HOST, port=PORT), bot.start()))
    bot.run()
