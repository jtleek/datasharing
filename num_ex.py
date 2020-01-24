#core datatypes
#Numbers
#Strings
'''
LIST
TUPLE
'''
"""
Dictionary
Set
"""
a=10#int
b=12.5#float
c=0b1010#bin
d=0x12#hex
e=0o12#oct
print('Hello',"Hello",'''Hello''')
print('RESULT=',a,b,c,d,e,sep='.\n',end='.\n')#file=,flush
print('TEST')
print(a)
print(id(a))
print(type(a))
print(type(a).__name__)
print(bin(c))
a=100
print(id(a))
#Garbage Collection
b=a#reference copy
a=200
