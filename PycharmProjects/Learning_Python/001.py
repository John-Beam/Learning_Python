x=bin(3)
y=bin(4)
print(x)
print(y)
# print ("Побитовое или:",x|y)
# print ("Побитовое исключающее или:",x^y)
# print ("Побитовое и:",x&y)
# print ("Битовый сдвиг влево",x<<y)
# print ("Битовый сдвиг вправо",x>>y)
# print ("Инверсия битов",~x)


print ("----------------------------------------------------")
example_string='Мышка сушек насушила. Мышка "мышек" пригласила'
print(example_string)
print(type(example_string ))

raw_string=r'Мышка сушек насушила. Мышка \\мышек\\ пригласила'
print(type(raw_string))
print(id(example_string))
print(id(example_string*2))
print(id(example_string*3))
# срезы строк
# срез[start:stop:step]
print(example_string[3:])
print(example_string[::3])
a="0123456789"
print(a[::3])


# multi_raw="""Синтаксис срезов лучше всего посмотреть на примере.
# Давайте посмотрим пример, это всё та же строка курс про Python'a на Coursera.
# Далее мы берем от нее срез. Срез это-- квадратные скобки и внутри три параметра, start, stop, step.
# То есть, начиная с какого символа мы хотим получить подстроку, до какого символа и какой шаг.
# На примере мы видим, что мы берем из строки срез начиная с девятого символа и до конца.
# Отсутствие параметров stop, step говорит как раз, что нам нужно брать срез до конца.
# На втором примере мы берем срез с 9 по 15 символы.
# Также в срезе можно использовать отрицательные значения.
# Если вы посмотрите на пример, где берется срез -8:.
# Это означает что срез начнется с восьмого символа с конца строки"""
# print(multi_raw)
# print(type(multi_raw))
# # print(multi_raw*3)