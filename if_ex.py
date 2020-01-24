#if condition:
      #S1
      #S1
      #S1
#with equal indentations

a=9
if a==10:
    print('a eq 10')

if a>10:
    print('a greater than 10')

if a<10:
    print('a less than 10')


if a==10:
    print('a eq 10')

elif a>10:
    print('a greater than 10')

elif a<10:
    print('a less than 10')


if a==10:
    print('a eq 10')

elif a>10:
    print('a greater than 10')

else:
    print('a less than 10')



s='python'
if s!='java':
    print('not java')

if not s.startswith('C++'):
    print('Not C++')

if 'th' in s:
    print('substring found')


#and, or

L1=[10,20]
L2=L1
L3=L1.copy()
if 20 in L1:
    print('20 found')
if L1 is L2: #id(L1)==id(L2)
    print('Both refers same object')
if L3==L1:
    print('Contents are same')

D={'A':10,'B':20}
if 'B' in D:
    print('Key B found')
if 20 in D.values():
    print('20 found in values')
if ('B',20) in D.items():
    print('item found')



















