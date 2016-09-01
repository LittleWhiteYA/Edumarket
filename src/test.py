from datetime import datetime

'''
def createGenerator():
	print "hi"
	yield 10
	print "hi2"
	yield 20
	print "hi3"
	yield 30

mygenerator = createGenerator()
print type(mygenerator)
myg2 = createGenerator().next()
print type(myg2)
print myg2
for i in range(3):
	print mygenerator.next()

def gener2():
	a = yield
	if a == 20:
		yield "hi"
	else:
		yield "qq"
		print "..."
		a = yield
		yield a

print "====="
ge2 = gener2()
ge2.next()
print ge2.send(10)
ge2.next()
print ge2.send(100)
'''

'''
def createGenerator():
	a = 3
	b = 2
	yield a
	b = yield
	print "hi"
	yield b
ge = createGenerator()
print ge.next()
ge.next()
print ge.send(10)

ge.close()
'''

'''
def isDate(date_txt):
	try:
		print date_txt
		datetime.strptime(date_txt, '%Y-%m-%d')
		return True
	except:
		return False


#str1 = '2015-01-14'
#print isDate(str1)

if datetime(2014,11,26) >= datetime(2014,10,25):
	test = datetime(2014,11,26) - datetime(2014,10,25)
	print test
	print test.days
'''

'''
nums = [1,2,3,4,5,1,2,3]

dict1 = {}

for num in nums:
	dict1.setdefault(num, 0)
	dict1[num] += 1
print dict1
'''

'''
from datetime import datetime

list1 = [i for i in range(1000000)]
set1 = set(list1)

start = datetime.now()

num = 999999
if num in list1:
	print "hi"

print datetime.now()-start

start = datetime.now()

if num in set1:
	print "hi2"

print datetime.now()-start
'''

'''
from collections import defaultdict
dict1 = defaultdict(dict)
dict1['a']['b'] = 1
print dict1
'''

'''
from collections import OrderedDict

d = OrderedDict()
d['a'] = 1
d['c'] = 2
d['b'] = 3
print d
'''

'''
from collections import Counter

dict1 = {}
list1 = [-1,-1,1,2,3,4,1,2,3,4,5,2,5,5,1,1]
dict1 = Counter(list1)
print dict1
print type(dict1)
a = sorted(dict1.items(), key = lambda pair:pair[0])
print len(dict1)
print a
print dict1[-1]
'''

'''
list1 = [i for i in range(100000)]
dict1 = {}

for l in list1:
	dict1[l] = l

start = datetime.now()

for l in list1:
	pass
print "list1: {}".format(datetime.now()-start)
start = datetime.now()

for k in dict1.keys():
	pass
print "dict1: {}".format(datetime.now()-start)
'''

'''
import cPickle as pickle

obj = {1:'a', 2:'b', 3:'c'}

with open('abc', 'wb') as fp:
	pickle.dump(obj, fp)


with open('abc', 'rb') as fp:
	print "hi"
	print pickle.load(fp)

'''

'''
import time
list1 = [x for x in range(100)]
t1 = time.time()
index = 2
for idx, item in enumerate(list1[index:], start=index):
	print idx, item
	pass

t1 = time.time()-t1
print t1
'''

'''
import time

ls = range(10000000)

# for statement
lr = []
t1 = time.time()
for i in ls: lr.append(abs(i))
t1 = time.time() - t1

# list compreh3nsion
lr = []
t2 = time.time()
lr = [abs(i) for i in ls]
t2 = time.time() - t2

# map() function
lr = []
t3 = time.time()
lr = map(abs,ls)
t3 = time.time() - t3

print 'for statement:    ', t1
print 'list comprehesion:', t2
print 'map() function:   ', t3
'''

'''
from itertools import groupby

list1 = [ {'a':1, 'b':1}, {'a':1, 'b':1}, {'a':1, 'b':2} ]

for key, value in groupby(list1):
	print key, value 
	for v in value:
		print v

print "==="
test = groupby(list1)
for t in test:
	print t
'''

'''
import itertools

list1 = [{'a':1, 'b':1}, {'a':1, 'b':1}, {'a':1, 'b':2} ]

for i in itertools.combinations(list1, 2):
	print i
'''

'''
start = datetime.now()
list1 = [x for x in range(1000000)]
for a in list1:
	a = str(a)
	pass


import timeit

print timeit.timeit('a = "123"; a = int(a)')	
print timeit.timeit('a = 123; a = str(a)')
'''

'''
test = 'a'
def outer(test):
	test = 'b'
	def inner():
		# nonlocal only used in Python3
		# nonlocal test
		
		print test
	
	inner()

outer(test)
'''

'''
# keyword-only parameter only used in Python3
def func(a, b, *, c):
	print(a,b,c)


func(1, 2, 3)	# TypeError
func(a=1,b=2,c=3)	# OK
'''

'''
date1 = datetime(2015, 12, 16, 19, 48, 44, 621000)
date2 = datetime.now()

print date1
print date2
print date2 - date1
print (date2 - date1).days
'''

# Quality Control
def average(values):
	"""
	# This is the key.
	>>> print(average([20, 30, 70]))
	40
	"""
	return sum(values) / len(values)

import doctest
doctest.testmod()



