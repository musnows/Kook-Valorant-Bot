import json
import aiofiles
import asyncio
from ..log.Logging import _log

FileList:list['FileManage'] = []
"""files need to write into storage"""
FlieSaveLock = asyncio.Lock()
"""files save lock, using in save_all_file"""

def open_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    return tmp


async def write_file_aio(path: str, value):
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def write_file(path: str, value):
    with open(path, 'w', encoding='utf-8') as fw2:
        json.dump(value, fw2, indent=2, sort_keys=True, ensure_ascii=False)


async def save_all_file(is_Aio=True):
    """save all file in FileList
    """
    # 加锁，避免数据写入错误
    global FlieSaveLock
    async with FlieSaveLock:
        for i in FileList:
            try:
                if is_Aio:
                    await i.save_aio()
                else:
                    i.save()
            except:
                _log.exception(f"save.all.file | {i.path}")

    _log.info(f"save.all.file | save finished")


# 文件管理类
class FileManage:
    # 初始化构造
    def __init__(self, path: str, read_only: bool = False) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            tmp = json.load(f)
        self.value = tmp  # 值
        self.type = type(tmp)  # 值的类型
        self.path = path  # 值的文件路径
        self.Ronly = read_only  # 是否只读
        #将自己存全局变量里面
        if not read_only:
            global FileList  # 如果不是只读，那就存list里面
            FileList.append(self)

    # []操作符重载
    def __getitem__(self, index):
        return self.value[index]

    # 打印重载
    def __str__(self) -> str:
        return str(self.value)

    # 删除成员
    def __delitem__(self, index):
        del self.value[index]

    # 长度
    def __len__(self):
        return len(self.value)

    # 索引赋值 x[i] = 1
    def __setitem__(self, index, value):
        self.value[index] = value

    # 迭代
    def __iter__(self):
        return self.value.__iter__()

    def __next__(self):
        return self.value.__next__()

    # 比较==
    def __eq__(self, i):
        if isinstance(i, FileManage):
            return self.value.__eq__(i.value)
        else:
            return self.value.__eq__(i)

    # 比较!=
    def __ne__(self, i):
        if isinstance(i, FileManage):
            return self.value.__ne__(i.value)
        else:
            return self.value.__ne__(i)

    # 获取成员
    def get_instance(self):
        return self.value

    # 遍历dict
    def items(self):
        return self.value.items()

    # 追加
    def append(self, i):
        self.value.append(i)

    # list的删除
    def remove(self, i):
        self.value.remove(i)

    def keys(self):
        return self.value.keys()

    # 保存
    def save(self):
        with open(self.path, 'w', encoding='utf-8') as fw:
            json.dump(self.value, fw, indent=2, sort_keys=True, ensure_ascii=False)

    # 异步保存
    async def save_aio(self):
        async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:  #这里必须用dumps
            await f.write(json.dumps(self.value, indent=2, sort_keys=True, ensure_ascii=False))