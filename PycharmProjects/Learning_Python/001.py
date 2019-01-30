x=bin(255)
y=bin(240)
# # z=int(0b11110000)
print(x)
print(y)
x,y = y,x #Можно менять значения переменных вот так вот
print(x)
print(y)

# print(x.__len__(),"бит занимает переменная x")
# print(type(x),"<--такой тип переменной x")
w = 0b11110000
print(w)
print("0b0000&0b0000=", bin(0b0000 & 0b0000))
print("0b000|0b1111=", bin(0b000 | 0b1111))
print("0b000^0b010=", bin(0b000 ^ 0b010))
print("0b01000<<1=", bin(0b01000 << 1))
print("0b01000>>2=", bin(0b01000 >> 2))

"""
& Binary AND	Operator copies a bit to the result if it exists in both operands	(a & b) (means 0000 1100)
| Binary OR	It copies a bit if it exists in either operand.	(a | b) = 61 (means 0011 1101)
^ Binary XOR	It copies the bit if it is set in one operand but not both.	(a ^ b) = 49 (means 0011 0001)
~ Binary Ones Complement	It is unary and has the effect of 'flipping' bits.	(~a ) = -61 (means 1100 0011 in 2's complement form due to a signed binary number.
<< Binary Left Shift	The left operands value is moved left by the number of bits specified by the right operand.	a << 2 = 240 (means 1111 0000)
>> Binary Right Shift	The left operands value is moved right by the number of bits specified by the right operand.	a >> 2 = 15 (means 0000 1111)"""

# print(int.bit_len(w),"бит занимает переменная x")
# print(type(w), "<--такой тип переменной x")
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
# print(multi_raw*3)