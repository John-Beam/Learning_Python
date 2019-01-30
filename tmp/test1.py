#!/usr/bin/python

# Open a file
fo = open("w", "w+")
fo.write( "Python is a great language.\nYeah its great!!\n");
print "Name of the file: ", fo.name
print "Closed or not : ", fo.closed
print "Opening mode : ", fo.mode
print "Softspace flag : ", fo.softspace
fo.close();



