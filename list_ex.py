#list-> class
L1=list([10,20,30])
print('L1=',L1)
L2=[10,12.5,'python',['a','b']]
print(L2)
print(L2[-2][-2])
#indexed -> all type of s;icing will work
print(L2[-1:1:-1])
#mutable->add, remove, update
#add
L2.append(20)
print('append=',L2)
L2.insert(2,300)
print('insert=',L2)
L3=[10,20]
L4=['a','b']
L5=L3+L4
L6=L3*10
print(L5,L6,sep='\n')
L3.extend(L4)
print('L3=',L3)
print(L3.append(L4))

#remove
print('L2=',L2)
r1=L2.pop()
print('pop',r1,L2, sep='\n')
r3=L2.remove('python')
print('remove=',L2,r3)

#update
L2[0]='java'
print('update=',L2)

#some other methods (inside ithe class it is method, outside the class it is function)
L7=[20,10,30]
L7.sort() #Asc
L8=['z','a','b']
L8.sort(reverse=True) #desc
print(L7,L8, sep='\n')
L9=[10,'a',20,'b']
L9.reverse()
print('reverse=',L9)
L9.clear()
print('clear=',L9)

L10=[10,['a','b']]
L11=L10  #reference copy
L12=L10.copy() #shallow copy
print(L11,L12,sep='\n')

import copy
L13=copy.deepcopy(L10)
print('deepcopy',L13)

print(id(L10[0]),id(L13[0])) #immutable object so ids are same
print(id(L10[1]),id(L13[1])) #mutable object so ids are different














