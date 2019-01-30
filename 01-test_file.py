import datetime
txtdate = "09.01.2018"
mydate = datetime.datetime.strptime(txtdate, "%d.%m.%Y")



print (mydate)