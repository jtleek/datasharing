S='python'
for a in S:
    print('a=',a)

b='java'
L=[10,20,30]
for b in L:
    print('b=',b)

print('Now a & b=',a,b)
D={'A':10,'B':20}
for c in D: #d.keys() will iterate on keys only
    print('Key=',c,' val=',D[c])

for i in D.items(): #[('A',10),('B',20)]
    print(i,i[0],i[1])
    val=20
    if 200==i[1]:
        print('key for val 20=',i[0])

for i,j in D.items():
    print(i,j)

hosts=['h1','h2','h3']
ips=['ip1','ip2','ip3']
z=zip(hosts,ips)
print(z)
print(list(z))
print(list(z)) # use the generator to create object.only one time generation.
#generator does not create objects untill ot unless it it called.

for h,i in zip(hosts,ips):
    print(h,i)
#for(i=2;i<10;i+2)

r1=range(10)
print(list(r1))
r2=range(1,10)
print(list(r2))
r3=range(1,10,2)
print(list(r3))
r4=range(10,1,-1)
print(list(r4))


for i in range(2,20,2):
    print('i=',i)

for h in range(len(hosts)):
    print('h=',hosts[h])

comp=['IBM','BOE1','SAP','BOE2']
for c in comp:
    if c.startswith('BOE'):
        print('FOUND')
        break  #else will not execute
else:   # it will always execute after the for loop is completed
    print('Not found')


for c in comp:
    if not c.startswith('BOE'):
        continue
    if c.startswith('BOE'):
        print('Some logic')
    print('last stmt of FOR')


a=0
while a<10:
    print('a=',a)
    a=a+1
#break, continue, else

# to achieve do while
#  while true:
    # if a==10;
        #break;


i=input('Enter name')
print('i=',i)
j=input('Enter number')
print('j=',j)
k=int(j)
l=eval(j)  #eval executes whwtever is in its single code
print(k,l)



a=10
b=10
r1=eval('a+b')
print(r1,type(r1))
r2=eval('[10,20]')
print(r2,type(r2))


























