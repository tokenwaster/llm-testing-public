from collkit import *
assert chunk([1,2,3,4,5],2)==[[1,2],[3,4],[5]]
assert chunk([],3)==[]
try: chunk([1],0); assert False
except ValueError: pass
assert flatten([1,[2,3],[4],5])==[1,2,3,4,5]
assert flatten(['ab',['c']])==['ab','c']
assert group_by([1,2,3,4],lambda x:x%2)=={1:[1,3],0:[2,4]}
assert take_while([2,4,5,6],lambda x:x%2==0)==[2,4]
assert take_while([1,2],lambda x:x>5)==[]
assert sorted(unique([3,1,3,2,1]))==[1,2,3]
y,n=partition([1,2,3,4],lambda x:x>2)
assert sorted(y+n)==[1,2,3,4]
assert windows([1,2,3,4],2)[0]==[1,2]
assert unique([3,1,3,2,1])==[3,1,2]
y,n=partition([1,2,3,4],lambda x:x>2)
assert y==[3,4] and n==[1,2]
assert windows([1,2,3,4],2)==[[1,2],[2,3],[3,4]]
print('10 tests verified')
