import time
import numpy as np
import json
import requests

url = 'http://172.27.196.13:31112/function/blockcode2'
row_A = 2000
column_A = 1000
column_B = 2000
A = np.random.randint(0, 10, (row_A, column_A))
B = np.random.randint(0, 10, (column_A, column_B))

# 冷启动
values1 = {}
values1['is_add'] = 0
values1['column'] = 0
values1['group'] = 0
values1['code'] = 0
values1['matrix1'] = A.tolist()
values1['matrix2'] = B.tolist()
data1 = json.dumps(values1)

T1 = time.time()
req = requests.post(url,data=data1)
T2 = time.time()
print('冷启动耗时:%s毫秒' % ((T2 - T1)*1000))

# 热启动
values2 = {}
values2['is_add'] = 0
values2['column'] = 0
values2['group'] = 0
values2['code'] = 0
values2['matrix1'] = A.tolist()
values2['matrix2'] = B.tolist()
data2 = json.dumps(values2)

T3 = time.time()
req = requests.post(url,data=data2)
T4 = time.time()
print('热启动耗时:%s毫秒' % ((T4 - T3)*1000))