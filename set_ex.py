#set=>class
#unordered collection
#only hold immutable objects
#mutable
#no index
#no key
#unique values

S={10,10,'py','py'}  #unique
print(S)

#mutable=> add, remove,update
#add
S.add(20)
S.add(20)
print('S=',S)

#orderedDict
#remove
r1=S.remove(20)
r2=S.pop()
print(r1,r2,S)

#set operations

S1={10,20,30,40}
S2={30,40,50,60}
S3=S1.union(S2)   #OR operation
print('union=',S3)
S4=S1.intersection(S2)   #AND operation
print('intersection=',S4)
S5=S1.difference(S2)
print('differnce=',S5)


L=[10,20,30]
S6=set(L)
L2=list(S6)
print(S6,L2)

D={'A':10,'B':20}
L1=list(D)
L2=list(D.keys())
L3=list(D.values())
L4=list(D.items())
print(L1,L2,L3,L4,sep='\n')


#frozen set

S7={10,20,30}
S8=frozenset(S7)
print('S8=',S8)




























