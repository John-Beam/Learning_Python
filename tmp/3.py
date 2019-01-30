#!/usr/bin/env python
#попытка отправить авторизацию на сайт через Ajax
import sys
import json
import cgi
import requests
url='https://files.infowatch.ru/?module=fileman&page=login&action=ajax_login'
payloads={'username':'QnT','password':'Pass55word!','otp':'','redirectAfterLogin':'','two_step_secret':'','language':'russian'}
headers={'content-type':'application/x-www-form-urlencoded; charset=UTF-8'}
