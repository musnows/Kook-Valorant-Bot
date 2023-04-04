import time
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo

def getTime():
    """获取当前时间，格式为 `23-01-01 00:00:00`"""
    a = datetime.now(ZoneInfo('Asia/Shanghai')) # 返回北京时间
    return a.strftime('%y-%m-%d %H:%M:%S')
    # use time.loacltime if you aren't using BeiJing Time
    # return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())


def getDate():
    """获取当前日期，格式为 `23-01-01`"""
    a = datetime.now(ZoneInfo('Asia/Shanghai')) # 返回北京时间
    return a.strftime('%y-%m-%d')
    # use time.loacltime if you aren't using BeiJing Time
    # return time.strftime("%y-%m-%d", time.localtime())


def getTimeStampOf8AM():
    """获取UTC+8（北京时间）当日早上8点的时间戳（用于计算用户的商店图片是否过期）"""
    return time.mktime(time.strptime(f"{getDate()} 08:00:00", "%y-%m-%d %H:%M:%S"))

def getTimeFromStamp(timestamp:float|int):
    """通过时间戳获取当前的本地时间，格式 23-01-01 00:00:00"""
    # localtime = time.localtime(timestamp)
    # localtime_str = time.strftime("%y-%m-%d %H:%M:%S", localtime)
    a = datetime.fromtimestamp(timestamp,tz=ZoneInfo('Asia/Shanghai'))
    return a.strftime("%y-%m-%d %H:%M:%S")


def getTimeStampFromStr(time_str):
    """从可读时间转为时间戳,格式 23-01-01 00:00:00
    - 如果传入的只有日期，如23-01-01，则会自动获取当日0点的时间戳
    """
    if len(time_str) == 8:
        time_str+=" 00:00:00"
    dt = datetime.strptime(time_str, '%y-%m-%d %H:%M:%S')
    tz = timezone(timedelta(hours=8))
    dt = dt.astimezone(tz)
    return dt.timestamp()

def getDateFromStamp(time_stamp):
    """从时间戳转为可读日期，格式%y-%m-%d"""
    dt = datetime.fromtimestamp(time_stamp)
    tz = timezone(timedelta(hours=8))
    dt = dt.astimezone(tz)
    return dt.strftime("%y-%m-%d") #转换成可读时间


def shop_time_remain():
    """计算当前时间和明天早上8点的差值，返回值为可读时间 08:00:00"""
    now = datetime.now(ZoneInfo('Asia/Shanghai')) # 当前的北京时间
    today = now.strftime("%y-%m-%d %H:%M:%S")  #今天日期+时间
    tomorow = (now + timedelta(days=1)).strftime("%y-%m-%d")  #明天日期
    times_tomorow = time.mktime(time.strptime(f"{tomorow} 08:00:00", "%y-%m-%d %H:%M:%S"))  #明天早上8点时间戳
    times_now = time.mktime(time.strptime(f"{today}", "%y-%m-%d %H:%M:%S"))  #现在的时间戳
    timeout = times_tomorow - times_now  #计算差值
    timeout = time.strftime("%H:%M:%S", time.gmtime(timeout))  #转换成可读时间
    return timeout