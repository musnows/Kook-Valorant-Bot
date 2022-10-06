<h1 align="center">
Kook-Valorant-Bot</h1>


<h4 align="center">this is a Valorant bot for KOOK platform</h4>


<div align="center">

English | [简体中文](./README.md)

![python](https://img.shields.io/badge/Python-3.8%2B-green) ![commit](https://img.shields.io/github/last-commit/Aewait/Valorant-kaiheila-bot) ![release](https://img.shields.io/github/v/release/Aewait/Valorant-kaiheila-bot)
[![khl server](https://www.kaiheila.cn/api/v3/badge/guild?guild_id=3566823018281801&style=3)](https://kaihei.co/oqz7Xg) ![githubstars](https://img.shields.io/github/stars/Aewait/Valorant-kaiheila-bot?style=social)

<img src="./screenshot/log.png" height="55px">
</div>

KOOK(once called kaiheila) is a Chinese voice communication software.

>Because this bot are only used in Chinese platform,so I didn't write a more detail Readme in English.Sorry for that

I just develop basic `/login` and `/shop` to fetch daily shop, hoping it's save for using 

* night market check as `/night` command was publish at `v0.2.4`

----

## Command

Here is the Command List for bot:

| Help        | Function                                                     |
| --------------- | ------------------------------------------------------------ |
| `/Ahri`         | help command（Because `/help`conflicts with other bots, `/Ahri`is used instead,who is an hero in League of Legends） |
| `/vhelp`         | help command for Valorant serch fuction |

Recommended to use after the Valorant_Function is stable.

| Valorant        | Function                                                     |
| --------------- | ------------------------------------------------------------ |
| `/val err_code` | help with the err_code of valorant                           |
| `/saveid`       | save or change user's game ID                                |
| `/myid`         | show user's game ID                                          |
| `/bundle name`    | search for skin bundles                                            |
| `/lead 30 20`   | show leaderboard of `ap`.the top 30 gamers more than 20 wins |
| `/login account passwd` | login your `riot_account` to fetch `auth_token` |
| `/logout` | logout your riot_account |
| `/shop` | fetch skin at daily shop |
| `/uinfo`或`/point` | fetch player `card` & `title`,remaining `Vp` and `Rp` |
| `/notify-a skin_name` |search for skin name,providing NO for add it into notification |
| `/notify-l` | show current notify skin |
| `/vip-u uuid` | get vip from uuid |
| `/vip-c` | check remaining time for vip |
| `/vip-shop` | check current vip-shop background img |
| `/vip-shop img-url` | add vip-shop background img  |
| `/vip-shop-s NO.` | switch vip-shop background img using `NO.`,  `NO.` will show at `/vip-shop` |
| `/vip-shop-d NO.` | delete vip-shop background img using `NO.` |

notify function require user to stay `login`, bot wil fetch your daily shop at `08:02 am GMT+8` .If the skin is in daily shop,bot will send a private message to user.

Because the bot is using in Chinese platform, the skin `name` only support `zh-TW`

| Other        | Function                                                     |
| --------------- | ------------------------------------------------------------ |
| `/hello`        | reply "world!"                                               |
| `/roll 1 100`   | return a number in `1~100`                                   |
| `/countdown 30` | set a countdown for 30s,which default is 60s                 |
| `/TL context`   | traslate context. from `ZH to EN` & `Other languages to ZH` |
| `/TLON`         | turn on real-time translation at current channel             |
| `/TLOFF`        | turn off real-time translation                               |
| `/we city`      | weather of the `city` in 3 days                                       |
| `/hs`           | history of today (now deleted)                                            |
| -               | Automatically grant roles to users                           |
| -               | When someone sponsor the server, send a thanks message on the notification channel |

You can find image examples for the functions in [screenshot](./screenshot) floder.

![image](./screenshot/daily_shop.png)

![image](./screenshot/points.png)

<details>
<summary>More Screenshot</summary>
<img src="./screenshot/bundle.png" alt="bundle">
<img src="./screenshot/lead.png" alt="leaderborad">
<img src="./screenshot/uinfo.png" alt="uinfo">
<img src="./screenshot/weather.png" alt="we">
</details>
For more guild and information, check out [wiki pages](https://github.com/Aewait/Valorant-kaiheila-bot/wiki)

----

## Breaking Changes at `V0.2.0`
First Breaking Changes for bot
## 1. publish vip!
### 1.1 add vip daily shop reply 
vip user will get different daily shop reply from bot.
* normal user get `1000*1000` img
* vip user get `1280*720` img

this background can be modified by vip-user,using picture they liked!

<img src="./screenshot/vip_daily_shop.png" alt="vip_shop">

### 1.2 add special command for vip user
* `vip-u`: get vip from uuid
* `vip-c`: check remaining time for vip
* `vip-l`: list vip user
* `vip-shop`: vip user can modify their background of daily shop

### 1.3 more great fuctions!
* vip user will get automatic daily shop reply at `8AM BJS`
* bot will log vip user daily shop img, next time when vip user use `/shop` command, bot will upload it from local path instead of drawing the img,which will save `2-3s` of response time
* using `aiohttp cookie_jar` to save vip user cookie, don't need to login again when bot restart because of maintenance。

## 2. other changes
* `add_date` will fetch `debug_channel` at start,don't need to fetch every time when exception
* change err reply to card message, bot will update msg instead of replying a new one when using `/shop` or `/uinfo`
* add `class icon` for easy manage icon-url

---

## About

Since I have not studied python, many codes in this repo are modified and used according to others' tutorials
* KOOK_api base on [khl.py](https://github.com/TWT233/khl.py)
* ValorantGameApi base on [frissyn/valorant.py](https://github.com/frissyn/valorant.py/)
* Main fetch_code base on [ValorantClientAPI](https://github.com/HeyM1ke/ValorantClientAPI)
* Fetch riot_auth_token base on [floxay/python-riot-auth](https://github.com/floxay/python-riot-auth)


### Thanks🎁
* [@DeeChael](https://github.com/DeeChael) for helping me debug
* [@Edint386](https://github.com/Edint386) for adding PIL_code for `/shop` 
* [@staciax](https://github.com/staciax) for [Valorant-DiscordBot/issues/74](https://github.com/staciax/Valorant-DiscordBot/issues/74)


If you like this project,please hit a star!✨
> sorry for my poor English
