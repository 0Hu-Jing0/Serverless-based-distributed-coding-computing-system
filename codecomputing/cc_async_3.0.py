# 按块划分矩阵，然后进行编码计算
import numpy as np
import asyncio
import json
import requests
import time
import math

# 生成post请求的data
def generate_data(is_add,column,group,code,matrix1,matrix2):
    values = {}
    values['is_add'] = is_add
    values['column'] = column
    values['group'] = group
    values['code'] = code
    values['matrix1'] = matrix1.tolist()
    values['matrix2'] = matrix2.tolist()
    return json.dumps(values)

# 调用OpenFaaS函数
async def run_function(is_add,column,group,code,matrix1,matrix2):
    url = 'http://172.27.196.13:31112/function/blockcode2'
    data = generate_data(is_add,column,group,code,matrix1,matrix2)
    req = requests.post(url,data=data)
    return req.json()

def basic_data(row_A,column_A,column_B,MIN,MAX):
    # 生成随机矩阵A&B
    A = np.random.randint(MIN, MAX, (row_A, column_A))
    B = np.random.randint(MIN, MAX, (column_A, column_B))
    return A,B,B.T

# 编码
def codecomputing_encode(A,B_trans,row_A,column_B,block):
    tasks = []
    B_block_up = 0
    B_block_down = block
    column = 0
    # 对B分块
    while B_block_up < column_B:
        A_up = 0
        A_down = 2 * block
        group = 0
        # A：完整的2块block
        while A_down <= row_A:  
            # 编码，分配任务
            tasks.append(run_function(0, column, group, 0, A[A_up:A_up+block], B_trans[B_block_up:B_block_down].T))
            tasks.append(run_function(0, column, group, 1, A[A_up+block:A_up+2*block], B_trans[B_block_up:B_block_down].T))
            tasks.append(run_function(0, column, group, 2, A[A_up:A_up+block] + A[A_up+block:A_up+2*block], B_trans[B_block_up:B_block_down].T))
            # 更新A块
            group = group + 1
            A_up = A_down
            A_down = A_up + 2 * block
        # A：按照剩余行数继续分块
        if(A_up < row_A):
            A_down = row_A
            is_add = 0
            A_odd = A[A_up:A_down]
            if((A_down - A_up) % 2 != 0):# 奇数行
                is_add = 1
                temp_array = np.zeros((1, A_odd.shape[1]), dtype=np.int16)
                A_odd = np.r_[A_odd, temp_array]
                A_down = A_down + 1
            A_down = A_down - A_up
            A_up = 0
            A_block = (A_down - A_up) // 2
            tasks.append(run_function(is_add, column, group, 0, A_odd[A_up:A_up + A_block], B_trans[B_block_up:B_block_down].T))
            tasks.append(run_function(is_add, column, group, 1, A_odd[A_up + A_block:A_down], B_trans[B_block_up:B_block_down].T))
            tasks.append(run_function(is_add, column, group, 2, A_odd[A_up:A_up + A_block]+A_odd[A_up + A_block:A_down], B_trans[B_block_up:B_block_down].T))
        # 更新B块
        column = column + 1
        B_block_up = B_block_down
        B_block_down = B_block_up + block
        if(B_block_up >= column_B): break
        if(B_block_down > column_B): B_block_down = column_B
    return tasks

# 解码
def codecomputing_decode(row_A,column_B,block,tasks):
    column_num = math.ceil(column_B / block)
    group_num = math.ceil((row_A / block)/2)
    # 未完成接收任务的列块
    column_not_done = [i for i in range(column_num)]
    # column_B × row_A/2，每一行块看作一个list，list中存储没有接收完全部（2个）result的组id,为空时说明这列的计算全部完成
    group_not_done = [[i for i in range(group_num)] for j in range(column_num)]
    # column_B × row_A/2 × 4，第一列是收到result的数量（0/1/2），后三列是有无收到某code，收到为1.没有为0
    visit = np.zeros((column_num,group_num, 4), dtype=np.int16)
    # 暂存所有冗余返回结果
    temp_answer = np.zeros((3,row_A + 1,column_B), dtype=np.int16) 
    # 解码得到的最终结果
    computing_answer = np.zeros((row_A, column_B), dtype=np.int64) 
  
    loop = asyncio.get_event_loop()
    done, _ = loop.run_until_complete(asyncio.wait(tasks))

    for fut in done:
        result = fut.result()
        is_add=  result['is_add'] 
        column = result['column']
        group = result['group']
        code = result['code']
        answer = result['answer']
        # is_add, column, group, code, answer = fut.result()
        if group in group_not_done[column]:# 该group还需要接收返回数据
            visit[column][group][code + 1] = 1
            visit[column][group][0] = visit[column][group][0] + 1
            temp_answer[code][group*block:group*block+len(answer),column*block:column*block+len(answer[0])] = answer
            if(visit[column][group][0] == 2):# 该group已经接收了2个数据
                group_not_done[column].remove(group)
                if(is_add == 1):
                    if(visit[column][group][1] == 0):# code1&code2
                        computing_answer[group*2*block:group*2*block+len(answer),column*block:column*block+len(answer[0])] = temp_answer[2][group*block:group*block+len(answer),column*block:column*block+len(answer[0])] - temp_answer[1][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
                        computing_answer[group*2*block+len(answer):group*2*block+2*len(answer)-1,column*block:column*block+len(answer[0])] = temp_answer[1][group*block:group*block+len(answer)-1,column*block:column*block+len(answer[0])]
                    elif(visit[column][group][2] == 0):# code0&code2
                        computing_answer[group*2*block:group*2*block+len(answer),column*block:column*block+len(answer[0])] = temp_answer[0][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
                        computing_answer[group*2*block+len(answer):group*2*block+2*len(answer)-1,column*block:column*block+len(answer[0])] = temp_answer[2][group*block:group*block+len(answer)-1,column*block:column*block+len(answer[0])] - temp_answer[0][group*block:group*block+len(answer)-1,column*block:column*block+len(answer[0])]
                    elif(visit[column][group][3] == 0):# code0&code1
                        computing_answer[group*2*block:group*2*block+len(answer),column*block:column*block+len(answer[0])] = temp_answer[0][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
                        computing_answer[group*2*block+len(answer):group*2*block+2*len(answer)-1,column*block:column*block+len(answer[0])] = temp_answer[1][group*block:group*block+len(answer)-1,column*block:column*block+len(answer[0])]
                else:
                    if(visit[column][group][1] == 0):# code1&code2
                        computing_answer[group*2*block:group*2*block+len(answer),column*block:column*block+len(answer[0])] = temp_answer[2][group*block:group*block+len(answer),column*block:column*block+len(answer[0])] - temp_answer[1][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
                        computing_answer[group*2*block+len(answer):group*2*block+2*len(answer),column*block:column*block+len(answer[0])] = temp_answer[1][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
                    elif(visit[column][group][2] == 0):# code0&code2
                        computing_answer[group*2*block:group*2*block+len(answer),column*block:column*block+len(answer[0])] = temp_answer[0][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
                        computing_answer[group*2*block+len(answer):group*2*block+2*len(answer),column*block:column*block+len(answer[0])] = temp_answer[2][group*block:group*block+len(answer),column*block:column*block+len(answer[0])] - temp_answer[0][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
                    elif(visit[column][group][3] == 0):# code0&code1
                        computing_answer[group*2*block:group*2*block+len(answer),column*block:column*block+len(answer[0])] = temp_answer[0][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
                        computing_answer[group*2*block+len(answer):group*2*block+2*len(answer),column*block:column*block+len(answer[0])] = temp_answer[1][group*block:group*block+len(answer),column*block:column*block+len(answer[0])]
            
            if(len(group_not_done[column]) == 0): 
                column_not_done.remove(column)
            if(len(column_not_done) == 0): 
                break     
    loop.close()
    return computing_answer

def hot_start(number):
    values = {}
    values['is_add'] = 2
    data = json.dumps(values)
    url = 'http://172.27.196.13:31112/function/blockcode2'
    for _ in range(number):
        req = requests.post(url,data=data)

def run():
    ################ 生成数据 ################
    row_A = 400
    column_A = 400
    column_B = 400
    MIN = 0
    MAX = 10
    block = 400
    A,B,B_trans = basic_data(row_A,column_A,column_B,MIN,MAX)
    print(str(row_A)+"x"+str(column_A)+"*"+str(column_A)+"x"+str(column_B))
    ############## codecomputing #############
    hot_start(4)
    T3 = time.time()
    tasks = codecomputing_encode(A,B_trans,row_A,column_B,block)
    answer = codecomputing_decode(row_A,column_B,block,tasks)
    T4 = time.time()
    print('编码计算后运行时间:%s毫秒' % (4049.49946975708))

    ################# 直接计算 ###############
    url = 'http://172.27.196.13:31112/function/blockcode2'
    data = generate_data(0,0,0,0,A,B)
    T1 = time.time()
    req = requests.post(url,data=data)
    T2 = time.time()
    C = np.array(req.json()['answer'])
    print('直接计算运行时间:%s毫秒' % ((T2 - T1)*1000))

    ################# 比较结果 ###############
    print('计算结果是否一致:')
    if(C.all() == answer.all()): print("yes")
    else: print("no")

if __name__=="__main__":
    run()
