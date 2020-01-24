#str->class collection of characters
a='PERSON'
b="PERSON'S"
c='''Person's Height XYZ"'''
d="""PERSON"""
print(a,b,c,d,sep='\n')
e='PERSON\'S' #use of escape sequence
print(e)
f='c:\newfolder\test.py'
print(f)
g='c:\\newfolder\\test.py'
print(g);
h=r'c:\newfolder\test.py' #raw string: no meaning for any special character
print(h)
i='WEL COME' #one space is equal to 1 character
print(i)
print(len(i)) #length of string
print(i[3])
print(i[1:4]) #slicing-> includes starting parameter and excludes last parameter
print(i[1:])  #starting index to end
print(i[:6])  # beginning to mentioned index
print(i[:])   # includes start to end
j=i[:]
print(id(i),id(j)) # since strings are immutable, it will show the same refernce, no need to make the new object as it cannnot be changed dynamically

#step
print(i[1:6:1]) #by default step value is 1
print(i[1:6:2])

#Reverse
print(i[7::-1])
print(i[6:1:-2])

#Negative Index
print(i[len(i)-1])
print(i[-1])  #-1 indicates last letter of string
print(i[-4:])#for getting last 4 chars
r1=i.startswith('WEL') #true/false
print('r1=',r1)
print(i.isupper()) #check if string is in upper
print(i.lower())  #converts in to lower case

#isalpha(),isdigit(),isalnum()
#istitle(),title()
#capitalize() -> capitalixe first letter of sentence

r4=i.count('E')
r5=i.replace('E','e')
r6=i.index('E') #first occurence
r7=i.find('E')
print(r4,r5,r6,r7,sep='\n')

#index('E',3) between 3 to last find index of E
#index('E',3,8) between 3 to 8 find index of E


r8=i.rindex('E') #reverse index
print('r8=',r8)
j=' wel come '
print(j.strip(),j.lstrip(),j.rstrip(),sep='\n')
k='[wel[come][]'
print(k)
print(k.strip(']w[e')) #lstrip,rstrip
r15=i.split()
print('r15=',r15)
print(i.split('E'))
x=10
y=20
z=x+y
print('add of {} and {} is {}'.format(x,y,z))

print('add of {0} and {1} is {2}'.format(x,y,z))


#py ver >3.5
r20=f'add of {x} and {y} is {z}'
print(r20)
line='-'*40
print(line)


#join any collection

print('-'.join(i))
print('and'.join(r15))










