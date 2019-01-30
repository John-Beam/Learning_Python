# -*- coding: utf-8 -*-
import random
import json
import time
import sys
import zipfile
import hashlib
import os
#import win32com.client
# c:\Python27\Scripts\pip.exe install pypiwin32

# Загружаем конфигурационный json
#task = json.loads(open("task.json"),"utf-8")
#mpstands = json.load(open("PT03-MP8.json"), "utf-8")
from builtins import print

from pip._internal.utils import encoding

#with open(C:\Users\ipavlov\YandexDisk\Работа\Scripts\python\AF_CP_Taskenyzer\task.json, encoding='utf-8') as jsn:
with open('task.json', encoding='utf-8') as jsn:
    task = json.load(jsn)
    print(task)