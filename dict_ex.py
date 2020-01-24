#dict=>class

L=['python',5,'blr']
print(L[0])
D={'course':'python','dur':5,'loc':'Blr'}
print(D)
#print(D['course'])
print(D.get('dur','No such key'))

#mutable-add, remove, update
D['course']=['python','C']

print(D)
E=D.copy()
r1=D.pop('course')
x=10
del x
del D['dur']

print('After delete=',D)
r2=D.popitem();
print('r2=',r2)

K=E.keys()
V=E.values()
I=E.items()

print(K,V,I, sep='\n')
