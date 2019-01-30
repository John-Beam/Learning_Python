# #!/usr/bin/python
# -*- encoding: utf-8 -*-
####УРОК1 - В ПИТОНЕ ВСЕ ОТСТУПЫ ДОЛЖНЫ БЫТЬ ВЫВЕРЕНЫ С ТОЧНОСТЬЮ ДО ПРОБЕЛА\
####ТРАХАЛСЯ ДО 2х НОЧИ С ЭТИМ ФАЙЛОМ ЧТОБЫ ЗАПУСТИТЬ\
####НЕ ЗАПУСКАЛСЯ ИЗ ЗА ПРОБЕЛОВ, КОТОРЫЕ ТРАКТОВАЛИСЬ ИНТЕРПРЕТАТОРОМ КАК КОМАНДЫ ИЗ ДРУГОГО УРОВНЯ\
#####Я ФИГ ЕГО ЗНАЕТ ПОЧЕМУ С ПИТОНОМ ТАКАЯ ЛАЖА, НО ЭТО РЕАЛЬНО ВЗЫВ МОЗГА.
# И ЕЩЁ НЕМНОГО- ЕСЛИ ПИСАТЬ КОММЕНТЫ НА РУССКОМ, ТО НУЖНО ВО ВТОРОЙ СТРОКЕ УКАЗЫВАТЬ ОБЯЗАТЕЛЬНО КОДИРОВКУ!
import sys
# import argparse все советуют разобраться с этим парсером аргументов. 
import getopt
# def usage():
#     print 'test.py -i <inputfile> -j <jfile> -o <outputfile>'
# def main(argv):
#     inputfile = '123'
#     outputfile = '456'
#     jfile = '789'
#     try:
#         opts, args = getopt.getopt(argv,"hi:j:o:",["ifile=","jfile=","ofile="])
#     except getopt.getopterror, e:
#         print e
#         usage()
#         sys.exit(2)
#     for opt, arg in opts:
#         if opt == '-h':
#             usage()
#             sys.exit()
#         elif opt in ("-i", "--ifile"):
#             inputfile = arg 
#         elif opt in ("-j", "--jfile"):
#             jfile = arg 
#         elif opt in ("-o", "--ofile"):
#             outputfile = arg
#     print 'input file is "', inputfile
#     print 'j file is "', jfile
#     print 'output file is "', outputfile
# if __name__ == "__main__":
#     main(sys.argv[1:])
import argparse
