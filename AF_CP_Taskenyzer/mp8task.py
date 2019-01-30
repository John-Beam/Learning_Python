# -*- coding: utf-8 -*-
import random
import json
import time
import sys
import zipfile
import hashlib
import os
import win32com.client
# c:\Python27\Scripts\pip.exe install pypiwin32

# Загружаем конфигурационный json
task = json.load(open("task.json"),"utf-8")
mpstands = json.load(open("PT03-MP8.json"),"utf-8")

for stand in mpstands["WIN2K12"].keys():
	dic = {"WIN2K12": mpstands["WIN2K12"][stand]}

	# Формируем текст задания
	outtask = open(task["tasks"]["name"],"w")
	outtask.write(task["tasks"]["intro"]["name"].encode("utf-8")+"\n")
	outtask.write((task["tasks"]["intro"]["text"][0]%dic).encode("utf-8")+"\n\n")
	outtask.write(task["tasks"]["level-one"]["name"].encode("utf-8")+"\n")
	outtask.write(random.choice(task["tasks"]["level-one"]["text"]).encode("utf-8")+"\n\n")
	outtask.write(task["tasks"]["level-two"]["name"].encode("utf-8")+"\n")
	outtask.write(random.choice(task["tasks"]["level-two"]["text"]).encode("utf-8")+"\n\n")
	outtask.close()


	# Создаем архив с заданием
	if task["tasks"]["archive"]["deflate"]:
		compress_type = zipfile.ZIP_DEFLATED
	else:
		compress_type = zipfile.ZIP_STORED
	z = zipfile.ZipFile(task["tasks"]["archive"]["name"],"w",compress_type)
	z.write(task["tasks"]["name"])
	z.close()

	mailbody = u"Смело товарищи в топку!\n"#.encode("cp1251")

	print "===> Please, send %s to user"%task["tasks"]["archive"]["name"]
	zdata = open(task["tasks"]["archive"]["name"],"rb").read()
	md5sum = hashlib.md5(zdata).hexdigest()
	print "md5 =", md5sum
	#mailbody += "md5 = " + md5sum + "\r\n"
	#mailbody += "FIXME: I'll be more informative in next letter\r\n"

	# Отправляем задание по почте
	# app = win32com.client.Dispatch("Outlook.Application")
	# mess = app.CreateItem(0)
	# mess.To = ",".join(task["mail"]["TO"])
	# mess.CC = ",".join(task["mail"]["CC"])
	# mess.Subject = u"Задания по экзамену Positive Technologies Application Firewall CP"
	# mess.Body = mailbody
	# print "!!!!! Please, go to Outlook and give me permissions to send email with task."
	# qqq = os.getcwd().decode("cp866") + os.sep + task["tasks"]["archive"]["name"]
	# for i in os.getcwd().split('\\'):
	# 	print i,map(ord,i)
	# sys.exit()
	# mess.Attachments.Add(qqq)
	# mess.Send()
	# print "Task sent"



		# Отправляем задание по почте
	app = win32com.client.Dispatch("Outlook.Application")
	mess = app.CreateItem(0)
	mess.To = ",".join(task["mail"]["TO"])
	mess.CC = ",".join(task["mail"]["CC"])
	mess.Subject = u"Task for MaxPatrol-8-CP exam"
	mess.Body = mailbody
	print "!!!!! Please, go to Outlook and give me permissions to send email with task."
	mess.Attachments.Add(os.getcwd().decode("cp1251") + os.sep + task["tasks"]["archive"]["name"])
	mess.Send()
	print "Task sent"