#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import requests
import hashlib
import logging
from datetime import datetime

#curl "https://jira.infowatch.ru/rest/gadget/1.0/login" -H "Accept: application/json, text/javascript, */*; q=0.01" -H "Referer: https://jira.infowatch.ru/plugins/servlet/gadgets/ifr?container=atlassian&mid=0&country=US&lang=en&view=default&view-params="%"7B"%"22writable"%"22"%"3A"%"22false"%"22"%"7D&st=atlassian"%"3A38TDp4p7pVjXCUHqHwv20e5Xyb6zJujA0KCqYS4J7WzovWtdOrhwhZN0hjjNHJJGW5VQDbKM"%"2F"%"2Brt1Fp7DpE9zUGfK"%"2BXhf4PSDCHJd31IKma9ci5G1sTaE0AO3ssrSi4ssc1IPar3GJRKO"%"2BoRbD4r"%"2FizPmCFbWBvPzUOcKEfyhT0lJYF0crtPtYsBR85g"%"2BZNttsh45nIfRyoWRERtIvoLX8KNVwA"%"3D&up_isPublicMode=false&up_isElevatedSecurityCheckShown=false&up_loginFailedByPermissions=false&up_externalUserManagement=false&up_loginSucceeded=false&up_allowCookies=true&up_externalPasswordManagement=&up_captchaFailure=false&up_isAdminFormOn=false&url=https"%"3A"%"2F"%"2Fjira.infowatch.ru"%"2Frest"%"2Fgadgets"%"2F1.0"%"2Fg"%"2Fcom.atlassian.jira.gadgets"%"2Fgadgets"%"2Flogin.xml&libs=auth-refresh" -H "Origin: https://jira.infowatch.ru" -H "X-Requested-With: XMLHttpRequest" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" --data "os_username=pavlov&os_password=R!kit!kit"%"40v!&os_captcha=" --compressed
#curl "https://jira.infowatch.ru/rest/helptips/1.0/tips" -H "Cookie: _ga=GA1.2.1490886059.1438614502; JSESSIONID=ADB1ED80D6DFC120B524575C1ACB79A4; atlassian.xsrf.token=BZ7P-20ZD-NTAE-ZLHW|9386da4a151750d8a1a85aedb581116d4b73bbaa|lin" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Content-Type: application/json" -H "Accept: application/json, text/javascript, */*; q=0.01" -H "Referer: https://jira.infowatch.ru/secure/Dashboard.jspa" -H "X-Requested-With: XMLHttpRequest" -H "Connection: keep-alive" --compressed
print("hello world")
CurTime = datetime.now()
print CurTime;
CurTime=datetime.utcnow()
print CurTime
s=requests.session( )
GetStatus=s.post("https://jira.infowatch.ru/rest/gadget/1.0/login")
print(GtStatus)
s.cookies
print s.cookies