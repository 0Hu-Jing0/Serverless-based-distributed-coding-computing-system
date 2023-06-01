import numpy as np
import json
import requests
import time

A = np.random.randint(0, 10, (2000, 1000))
B = np.random.randint(0, 10, (1000, 2000))

values = {}
values['is_add'] = 0
values['column'] = 0
values['group'] = 0
values['code'] = 0
values['matrix1'] = A.tolist()
values['matrix2'] = B.tolist()
data = json.dumps(values)
url = 'http://172.27.196.13:31112/function/blockcode2'

T1 = time.time()
req = requests.post(url,data=data)
T2 = time.time()

print(req.status_code)
print('运行时间:%s毫秒' % ((T2 - T1)*1000))