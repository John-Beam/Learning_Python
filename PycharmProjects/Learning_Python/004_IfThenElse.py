# -*- coding: UTF-8 -*-
######"оператор if "
print("оператор if\n")
company="example.net"
if "my" in company or company.endswith(".net"):
    print("Условие выполнено!")

#####"if-else"
print("Пример if-else\n")
company="example.net"
if "my" in company or company.endswith(".com"):
    print("Условие выполнено!")
else:
    print("условие не выполнилось. Сработал Else")
print("\n if-elif-else\n")
### if-elif-else

company="example.test.net"
if "my" in company:
    print("Условие выполнено!")
elif "test" in company:
     print("Сработал Elif")
else:
    print("Ничего не найдено!!")
######print("Пример тернарного оператора")

print("Пример тернарного оператора")
score=[0,5]
print(type(score))
winner = "Argentina" if score[0]>score[1] else "Jamaica"
print(winner)
####print("Пример While")
print("\n\nПример While")
i = 0
while True:
    i = i + 1
    if i == 2:
        print("scipping 2")
        continue
        if  i == 5:
            print("breaking")
            break
        print (i)
    print("Finish!")
    break

#цекл for

