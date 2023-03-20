由于本项目在重构后，新增了很多文件，在此说明各个文件的作用

```
code
  - config          # 配置文件路径（参考config.exp.json）
  - log             # 日志、资源文件路径（参考log.example）
  - pkg
    - plugins       # 命令拆分文件（从main中剥离），部分命令在此文件内
        - BotStatus.py   # 机器人在玩状态
        - Funny.py       # 娱乐功能
        - GameHelper.py  # 游戏助手（保存用户id，valorant错误码查询）
        - GrantRoles.py  # 给用户上角色（服务器管理相关）
        - Match.py       # 查询战绩
        - Translate.py   # 翻译
        - ValFileUpd.py  # 更新本地valorant资源文件
        - Vip.py         # vip相关功能
    - utils         # 处理函数
        - api       # valorant-shop-api
          - ApiHandler.py # api各个接口的处理函数
          - ApiToken.py   # api token 生成和检查
        - log       # 日志相关
          - BotLog.py     # 机器人用户记录和异常处理
          - Logging.py    # 实例化的logger
        - valorant  # valorant相关
          - api     # valorant的api
            - Assets.py   # 第三方api，来自valorant-api.com，用于获取游戏内元素信息
            - Local.py    # 本地查找以节省时间，数据原自valorant-api.com
            - Riot.py     # Riot官方api，查询商店、战绩、用户信息等等
          - AuthCache.py  # 用户登录信息的缓存
          - Reauth.py     # 重新登录的处理
          - EzAuthExp.py  # EzAuth的自定义Exception
          - EzAuth.py     # 用于使用账户密码获取Riot的access-token
        - file      # 文件相关
          - Files.py      # 所有本地文件预加载
          - FileManage.py # 文件处理类，封装了save方法，方便保存到本地
        
        - BotVip.py       # 机器人vip处理函数
        - Gtime.py        # 时间相关函数
        - Help.py         # 机器人帮助命令
        - KookApi.py      # kook api
        - ShopImg.py      # 商店画图处理
        - ShopRate.py     # 皮肤评论系统

  - api.py         # valorant-shop-api main-file
  - main.py        # bot main-file
  - start.py       # start bot/api at once
```