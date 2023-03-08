import time
from datetime import datetime,timedelta


def getTime():
    """获取当前时间，格式为 23-01-01 00:00:00"""
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())


def getDate():
    """获取当前日期，格式为 23-01-01"""
    return time.strftime("%y-%m-%d", time.localtime())


def getTimeStampOf8AM():
    """获取当日早上8点的时间戳（用于计算用户的商店图片是否过期）"""
    return time.mktime(time.strptime(f"{getDate()} 08:00:00", "%y-%m-%d %H:%M:%S"))

def getTimeFromStamp(timestamp:float|int):
    """通过时间戳获取当前的本地时间，格式 23-01-01 00:00:00"""
    localtime = time.localtime(timestamp)
    localtime_str = time.strftime("%y-%m-%d %H:%M:%S", localtime)
    return localtime_str

def shop_time_remain():
    """计算当前时间和明天早上8点的差值，返回值为可读时间 08:00:00"""
    today = datetime.today().strftime("%y-%m-%d %H:%M:%S")  #今天日期+时间
    tomorow = (datetime.today() + timedelta(days=1)).strftime("%y-%m-%d")  #明天日期
    times_tomorow = time.mktime(time.strptime(f"{tomorow} 08:00:00", "%y-%m-%d %H:%M:%S"))  #明天早上8点时间戳
    times_now = time.mktime(time.strptime(f"{today}", "%y-%m-%d %H:%M:%S"))  #现在的时间戳
    timeout = times_tomorow - times_now  #计算差值
    timeout = time.strftime("%H:%M:%S", time.gmtime(timeout))  #转换成可读时间
    return timeout
