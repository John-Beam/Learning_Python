# -*- coding: UTF-8 -*-
answer = None
print(type(None))
#<class 'NoneType'>
print(bool(None))
#преборазование к тииу bool всегда даёт False
#Можно попробовать и так ( всё равно будет преобразование)
answer = None
if not answer:
    print("ответ не получен")
    #на экране будет "ответ не получен"

