import json
from typing import Union
from khl import Bot, ChannelPrivacyTypes

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])


# 图标
class icon_cm:
    val_logo = "https://img.kookapp.cn/assets/2022-09/gVBtXI0ZSg03n03n.png"
    val_logo_gif = "https://img.kookapp.cn/assets/2022-09/5skrwZcjGJ0dc07i.gif"
    whats_that = "https://img.kookapp.cn/assets/2022-09/uhm2AewC1i0e80e8.png"
    dont_do_that = "https://img.kookapp.cn/assets/2022-09/wUNDAfzBlr0e80e8.png"
    lagging = "https://img.kookapp.cn/assets/2022-09/D1nqrTszjQ0e80e8.png"
    correct = "https://img.kookapp.cn/assets/2022-09/DknXSpwrlQ0e80e8.gif"
    duck = "https://img.kookapp.cn/assets/2022-09/qARsaxW6lp0e80e8.gif"
    that_it = "https://img.kookapp.cn/assets/2022-09/LqD0pQY2P70e80e8.png"
    to_much_money = "https://img.kookapp.cn/assets/2022-09/y17ZhjjaVf0e80e8.png"
    shaka = "https://img.kookapp.cn/assets/2022-09/kMWT5AoEic0e80e8.png"
    say_hello_to_camera = "https://img.kookapp.cn/assets/2022-09/sHh8VJrMp20e80e8.png"
    crying_crab = "https://img.kookapp.cn/assets/2022-09/DfveorD0lS0e80e8.png"
    im_good_phoniex = "https://img.kookapp.cn/assets/2022-09/RdiFsx16Aw0e80e8.png"
    rgx_card = "https://img.kookapp.cn/assets/2022-09/p1VwoNZZWD0e80e8.gif"
    rgx_broken = "https://img.kookapp.cn/assets/2022-09/A8wPGOtJmz0e80e8.gif"
    shot_on_fire = "https://img.kookapp.cn/assets/2022-09/L5EeqS3GDC0e80e8.png"
    powder = "https://img.kookapp.cn/assets/2022-09/nwXm6aNzj20e80e8.png"
    ahri1 = "https://img.kookapp.cn/assets/2022-09/TU9bVQdHiz08c08c.jpg"
    ahri2 = "https://img.kookapp.cn/assets/2022-09/bK1v7R6D7j08c08c.jpg"
    ahri3 = "https://img.kookapp.cn/assets/2022-09/zS5B2wkBvG08c08c.jpg"
    ahri_kda1 = "https://img.kookapp.cn/assets/2022-09/kOwzlg7x6M0rs0rs.jpg"
    ahri_kda2 = "https://img.kookapp.cn/assets/2022-09/OMcQuhcrXo0sc0sc.jpg"
    ahri_kda3 = "https://img.kookapp.cn/assets/2022-09/JHUxBavOeC0xg0xg.jpg"
    ahri_star = "https://img.kookapp.cn/assets/2022-09/NY1m6182Ae0v80v8.jpg"
    ahri_dark = "https://img.kookapp.cn/assets/2022-09/HJJJPrYxUo14w14w.jpg"
    ahri_sour = "https://img.kookapp.cn/assets/2022-09/bnPK4GhBfc0x40x4.jpg"
    ahri_forest = "https://img.kookapp.cn/assets/2022-09/9ObV0banuE1ew1ew.jpg"
    ahri_game = "https://img.kookapp.cn/assets/2022-09/Rp6bnjsLnZ0cg0cg.jpg"


#更新卡片消息
async def upd_card(msg_id: str,
                   content,
                   target_id='',
                   channel_type: Union[ChannelPrivacyTypes, str] = 'public',
                   bot=bot):
    content = json.dumps(content)
    data = {'msg_id': msg_id, 'content': content}
    if target_id != '':
        data['temp_target_id'] = target_id
    if channel_type == 'public' or channel_type == ChannelPrivacyTypes.GROUP:
        result = await bot.client.gate.request('POST', 'message/update', data=data)
    else:
        result = await bot.client.gate.request('POST', 'direct-message/update', data=data)
    return result