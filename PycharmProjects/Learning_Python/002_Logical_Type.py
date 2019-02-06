# -*- coding: UTF-8 -*-
import datetime
import calendar
year = datetime.date.today().year
print(year)
year=2020
print(year)
is_leap=year%4 == 0 and (year%100!=0 or year%400==0)
print(is_leap)

print(calendar.isleap(2020))

########################
#Строки и операции с ними

quote="а роза упала на лапу азора"
print(quote[::-1])
print(quote.count("а"))
print(quote.swapcase())
print(quote.capitalize())
for a in quote:
    print("-->",a)
print(type(quote))
#Форматирование строк
#плейсхолдеры
two_quote = "%s - главное достоинство программиста. (%s)"
print(two_quote % ("Лень","Larry Wall"))

#метод format
print("{} Then do not squander time, for that is the stuff life is made of. ({})" .format("Dost thou love life?","Benjamin Franklin"))
#именные плейсхолдеры
print("{num}K ought to be enough for anybody ({name})".format(num=640,name="Bill Gates"))

#F-strings  ( c версии 3.6)
subject="оптимизация"
author="Donald Knuth"
print(f"Преждевременная {subject} - корень всех зол ({author})")

# модификаторы форматирования
num = 8
print(f"Binary: {num:#b}")

num=2/3
print(num)
print(f"{num:.3f}")
#https://docs.python.org/3/library/string.html


#ВВОД С КЛАВИАТУРЫ

#name = input("Введите ваше имя:")
#print(f"Привет,{name}!")

# БАЙТОВЫЕ СТРОКИ
example_bytes =b"hello"
print(type(example_bytes))

print("ВЫВОДИМ ПОБАЙТОВО Byte-String:\n")
for i in example_bytes:
    print(i)


"""
Но, если попробовать взять преобразовать в байтовую строку не-ASCII символы - буквы русского алфавита,
то возникнет ошибка
 
example_bytes = b"ыва"

   example_bytes = b"ыва"
                   ^
SyntaxError: bytes can only contain ASCII literal characters."""

#кодировка строк
example_string="Привет"
print(type(example_string))

encoded_string = example_string.encode(encoding="utf-8")
print(encoded_string)
print(type(encoded_string))

#Декодируем байты в Строку
decoded_string = encoded_string.decode()
print(decoded_string)
