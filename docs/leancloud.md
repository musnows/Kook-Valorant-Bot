## 介绍

在一位社区开发者的建议下，再加上本身就有在 kook-valorant-bot和 qq-valorant-bot 之间同步皮肤评论数据库的需求，在此设立一个valorant国内社区的公共皮肤评论数据库！

您可以选择将您的项目接入数据库；也可只读数据库，获取公共皮肤评论！

>数据库基于leancloud的结构化数据存储。leancloud提供了多语言sdk，参考 [官方文档](https://docs.leancloud.cn/sdk/storage/overview/)

所有皮肤uuid都需要统一为拳头商店返回值的皮肤uuid，即 [valorant-api.com/v1/weapons/skins](https://valorant-api.com/v1/weapons/skins) 皮肤数据列表中的 `["level"][0]["uuid"]` ;

皮肤评分采用**100分制**。

----

目前设置了多个class，字段如下：

## 1.SkinRate

皮肤评分数据

| 字段 | 类型 | 含义 | 是否必填 | 
| --- | --- | --- | ------- |
| rating | NUMBER | 该皮肤的平均分 |  是 |
| skinUuid | STRING | 皮肤 uuid |   是 | 
| skinName | STRING | 皮肤名字（繁体中文） |  是 |

更新皮肤评分时，直接和原有rating加起来计算平均数即可；为保险起见，请先搜索数据库中是否已有该皮肤uuid，避免出现冗余键值。

## 2.UserRate

用户发送的皮肤评论

| 字段 | 类型 | 含义 | 是否必填 | 
| --- | --- | --- | ------- | 
| rating | NUMBER | 皮肤评论的用户评分 | 是 | 
| skinUuid | STRING | 皮肤 uuid | 是 |
| skinName | STRING | 皮肤名字（繁体中文） | 是 | 
| comment | STRING | 用户皮肤评论 | 是 | 
| platform | STRING | 平台 | 是  |
| rateAt | NUMBER | 用户评论时间戳  | 是 |
| userId | STRING | 用户平台id | 否 |
| msgId | STRING | 评论消息id | 否  |

* 若平台有用户id和消息id（如kook、qq频道），则需要设置；
* 强烈建议设置用户评论时间戳（秒级）方便后续查看日志；
* `platform` 字段指代该评论来自什么平台，比如kook和qq频道；若您是小程序/app开发者，请给您的平台起一个名字，并将来自您平台的所有用户评价的`platform` 字段设置成该名字。

## 3.ShopCmp

昨日商店最高分/最低分，请修改原有object（先搜索获取到原有obj，在其基础上修改），不要新建object

| 字段 | 类型 | 含义 | 是否必填 | 
| --- | --- | --- | ------- | 
| best | BOOLEAN | 当日最佳True/最差False | 是 | 
| rating | NUMBER | 商店4个皮肤的平均分 | 是 | 
| skinList | ARRAY | 商店4个皮肤 uuid | 是 |
| platform | STRING | 平台 | 是  |
| userId | STRING | 用户平台id | 否 |

建议在本地维护一个当天（8am之后）的用户最好/最差商店信息，并在次日8am更新到数据库。数据库中维护的是**昨日商店**的最高分/最低分。

由于leancloud的结构化数据存储并不是[线程安全](https://docs.leancloud.cn/sdk/storage/guide/python/#%E7%BA%BF%E7%A8%8B%E5%AE%89%E5%85%A8)的，为了避免多个项目同时在8am访问并更新ShopCmp，请加入开发者频道和我确认，约定一个时间（不同项目错开）来更新数据!

## 4.UserCmt

用户user_id和其评论过的皮肤uuid的对照表

| 字段 | 类型 | 含义 | 是否必填 | 
| --- | --- | --- | ------- | 
| skinList | ARRAY | 用户评价过的所有皮肤uuid | 是 |
| platform | STRING | 平台 | 是  |
| userId | STRING | 用户平台id | 是 |

此字段是采用“以空间换时间的”思路，如果不维护此表，则需要**遍历**UserRate中的所有评论，找到该用户已评论皮肤，并不是很友好。

如果你的平台并没有用户id，也不需要获取某一用户已评论皮肤列表，则可以不维护此class。