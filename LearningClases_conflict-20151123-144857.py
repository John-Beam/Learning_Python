#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import requests
import lxml
import hashlib
import logging
from datetime import datetime
URL="http://www.tutu.ru/rasp.php?st1=79310&st2=80710"

response = requests.get(URL)

# Ответ
print response.status_code # Код ответа
print response.headers # Заголовки ответа
#print response.content # Тело ответа

# Запрос
print response.request.headers # Заголовки отправленные с запросом