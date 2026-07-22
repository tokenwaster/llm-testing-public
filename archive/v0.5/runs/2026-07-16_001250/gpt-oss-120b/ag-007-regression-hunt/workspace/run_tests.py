import pytest, sys
ret = pytest.main(['-q', 'tests'])
print('exit', ret)
