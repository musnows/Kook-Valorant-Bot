<h1 align="center">Valorant-kaiheila-bot</h1>


<h4 align="center">this is a Valorant bot for KOOK platform</h4>


<div align="center">

English | [简体中文](./README.md)

![python](https://img.shields.io/badge/Python-3.8%2B-green) ![commit](https://img.shields.io/github/last-commit/Aewait/Valorant-kaiheila-bot) ![release](https://img.shields.io/github/v/release/Aewait/Valorant-kaiheila-bot)
[![khl server](https://www.kaiheila.cn/api/v3/badge/guild?guild_id=3566823018281801&style=3)](https://kaihei.co/oqz7Xg) ![githubstars](https://img.shields.io/github/stars/Aewait/Valorant-kaiheila-bot?style=social)

</div>

KOOK(once called kaiheila) is a Chinese voice communication software.

>Because this bot are only used in Chinese platform,so I didn't write a more detailed Readme in English.Sorry for that

This robot is still at an extremely early stage, and many of the functions I want have not yet been realized.

~~For safety reason, the development of /store and /nightmarket has been canceled~~

I just develop basic `/login` and `/shop` to fetch daily shop, hoping it's save for using 

----

## Command

Here is the Command List for bot:

| Help        | Function                                                     |
| --------------- | ------------------------------------------------------------ |
| `/Ahri`         | help command（Because `/help`conflicts with other bots, `/Ahri`is used instead,who is an hero in League of Legends） |
| `/vhelp`         | help command for Valorant serch fuction |

| Valorant        | Function                                                     |
| --------------- | ------------------------------------------------------------ |
| `/val err_code` | help with the err_code of valorant                           |
| `/saveid`       | save or change user's game ID                                |
| `/myid`         | show user's game ID                                          |
| `/skin name`    | search for skins                                             |
| `/lead 30 20`   | show leaderboard of `ap`.the top 30 gamers more than 20 wins |
| `/login account passwd` | login your riot_account to fetch auth_token |
| `/logout` | logout your riot_account |
| `/shop` | fetch skin at daily shop |
| `/point` | fetch remaining `Vp` and `Rp` |

Recommended to use after the Valorant_Function is stable.

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

for more guild and information,check out [wiki pages](https://github.com/Aewait/Valorant-kaiheila-bot/wiki)


## About
Since I have not studied python, many codes in this repo are modified and used according to others' tutorials
* KOOK_api base on [khl.py](https://github.com/TWT233/khl.py)
* ValorantGameApi base on [frissyn/valorant.py](https://github.com/frissyn/valorant.py/)
* Main fetch_code base on [ValorantClientAPI](https://github.com/HeyM1ke/ValorantClientAPI)



### Thanks🎁
* [@DeeChael](https://github.com/DeeChael) for helping me debug
* [@Edint386](https://github.com/Edint386) for adding PIL_code for `/shop` 
* [@staciax](https://github.com/staciax) for [Valorant-DiscordBot/issues/74](https://github.com/staciax/Valorant-DiscordBot/issues/74)


If you like this project,please hit a star!✨
> sorry for my poor English
