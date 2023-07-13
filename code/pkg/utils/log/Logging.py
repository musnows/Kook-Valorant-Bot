import logging # 采用logging来替换所有print
from logging.handlers import TimedRotatingFileHandler

LOGGER_NAME = "botlog"
LOGGER_FILE = "bot.log"

# 只打印info以上的日志（debug低于info）
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
                    datefmt="%y-%m-%d %H:%M:%S")
# 获取一个logger对象
_log = logging.getLogger(LOGGER_NAME)
"""自定义的logger对象"""
# 实例化控制台handler和文件handler，同时输出到控制台和文件
# cmd_handler = logging.StreamHandler() # 默认设置里面，就会往控制台打印信息;自己又加一个，导致打印俩次
file_handler = logging.FileHandler(LOGGER_FILE, mode="a", encoding="utf-8")
fmt = logging.Formatter(fmt="[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
                    datefmt="%y-%m-%d %H:%M:%S")
file_handler.setFormatter(fmt)
# 每天新生成一个
log_handler = TimedRotatingFileHandler(LOGGER_FILE, when='D')
log_handler.setFormatter(fmt)

# _log.addHandler(file_handler)
_log.addHandler(log_handler)