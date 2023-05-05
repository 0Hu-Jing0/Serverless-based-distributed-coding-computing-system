import numpy as np
import asyncio
import json
import requests
import time

# 生成post请求的data
def generate_data(column,group,code,vector1,vector2):
    values = {}
    values['column'] = column
    values['group'] = group
    values['code'] = code
    values['vector1'] = vector1.tolist()
    values['vector2'] = vector2.tolist()
    return json.dumps(values)

# 调用OpenFaaS函数
async def run_function(column,group,code,vector1,vector2):
    url = 'http://172.27.20.221:31112/function/codecompt'
    data = generate_data(column,group,code,vector1,vector2)
    req = requests.post(url,data=data)
    return req.json()

def basic_data(row_A,column_A,MIN,MAX,column_B):
    row_B = column_A

    # 生成随机矩阵A&B
    A = np.random.randint(MIN, MAX, (row_A, column_A))
    B = np.random.randint(MIN, MAX, (row_B, column_B))
    B_trans = B.T

    A_is_odd = 0 # 0偶数行 1奇数行
    # 若随机矩阵A为奇数行，则为其补一行0
    if(row_A % 2 != 0):# 奇
        temp_array = np.zeros((1, column_A), dtype=np.int16)
        A = np.r_[A, temp_array]
        row_A = row_A + 1
        A_is_odd = 1
    else:# 偶
        A_is_odd = 0
    
    return row_B,A_is_odd,A,B,B_trans

# 编码
def codecomputing_encode(A,B_trans,row_A,column_B):
    tasks = []
    for j in range(column_B):
        # 将随机矩阵B的每列分开A*bj
        for i in range(row_A // 2):
            # 将随机矩阵A的每两行视为一组进行编码&分配任务
            tasks.append(run_function(j, i, 0, A[2 * i], B_trans[j].T))
            tasks.append(run_function(j, i, 1, A[2 * i + 1], B_trans[j].T))
            tasks.append(run_function(j, i, 2, A[2 * i] + A[2 * i + 1], B_trans[j].T))
    return tasks

# 解码
def codecomputing_decode(row_A,column_B,tasks,A_is_odd):
    # 未完成接收任务的列
    column_not_done = [i for i in range(column_B)]
    # column_B × row_A/2，每一行看作一个list，list中存储没有接收完全部（2个）result的组id,为空时说明这列的计算全部完成
    group_not_done = [[i for i in range(row_A // 2)] for j in range (column_B)]
    # column_B × row_A/2 × 4，第一列是收到result的数量（0/1/2），后三列是有无收到某code，收到为1.没有为0
    visit = np.zeros((column_B,row_A // 2, 4), dtype=np.int16)
    # 暂存所有返回结果
    temp_answer = np.zeros((column_B,row_A // 2, 3), dtype=np.int16) 
    # 解码得到的最终结果
    answer = np.zeros((row_A, column_B), dtype=np.int16) 
    
    loop = asyncio.get_event_loop()
    done, _ = loop.run_until_complete(asyncio.wait(tasks))

    for fut in done:
        result = fut.result()
        column = result['column']
        group = result['group']
        code = result['code']
        num = result['answer']
        if group in group_not_done[column]:# 该group还需要接收返回数据
            # if(visit[column][group][code + 1] == 1): print("WARNING，收到重复任务")
            visit[column][group][code + 1] = 1
            visit[column][group][0] = visit[column][group][0] + 1
            temp_answer[column][group][code] = num

            if(visit[column][group][0] == 2):# 该group已经接收了2个数据
                group_not_done[column].remove(group)
                if(visit[column][group][1] == 0):# code1&code2
                    answer[group * 2 + 0][column] = temp_answer[column][group][2] - temp_answer[column][group][1]
                    answer[group * 2 + 1][column] = temp_answer[column][group][1]
                elif(visit[column][group][2] == 0):# code0&code2
                    answer[group * 2 + 0][column] = temp_answer[column][group][0]
                    answer[group * 2 + 1][column] = temp_answer[column][group][2] - temp_answer[column][group][0]
                elif(visit[column][group][3] == 0):# code0&code1
                    answer[group * 2 + 0][column] = temp_answer[column][group][0]
                    answer[group * 2 + 1][column] = temp_answer[column][group][1]

                if(len(group_not_done[column]) == 0): column_not_done.remove(column)
                if(len(column_not_done) == 0): break                
    loop.close()
    if(A_is_odd == 1):
        answer = np.delete(answer,row_A - 1,axis=0)
        row_A = row_A - 1
    return answer

def run():
    ################ 生成数据 ################
    row_A = 1000
    column_A = 1029
    column_B = 1058
    MIN = 0
    MAX = 10
    row_B,A_is_odd,A,B,B_trans = basic_data(row_A,column_A,MIN,MAX,column_B)
    ################# 直接计算 ###############
    # T1 = time.time()
    # C = np.dot(A,B)
    # T2 = time.time()
    # print('直接计算运行时间:%s毫秒' % ((T2 - T1)*1000))
    ############## codecomputing #############
    T3 = time.time()
    tasks = codecomputing_encode(A,B_trans,row_A,column_B)
    answer = codecomputing_decode(row_A,column_B,tasks,A_is_odd)
    T4 = time.time()
    print('程序运行时间:%s毫秒' % ((T4 - T3)*1000))

    print(C)
    print(answer)

if __name__=="__main__":
    run()