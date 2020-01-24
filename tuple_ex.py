#tuple =>class () are used for tuples and [] is used for list
T1=tuple([10,20,30])
T2=(10,12.5,'python',['a','b'],(10,20))
print(T2)
print(T2[1])
print(T2[2][1])
print(T2[-4-1:4:2])
i=T2.index('python')
c=T2.count('python')
print('T2=',i,c)

#if want to change the tuple, then convert it to list and change

T3=(10,20,30)
L3=list(T3)
print('l3=',L3)
S='WELCOME'
T=tuple(S)
print(T)
