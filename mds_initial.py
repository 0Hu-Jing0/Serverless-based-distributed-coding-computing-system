import numpy as np
import asyncio

MIN = 0
MAX = 10
row_A = 4
column_A = 2
row_B = column_A
column_B = 3
A_is_odd = 0 # 0偶数行 1奇数行

def generate_matrix(row, column, min, max):
    return np.random.randint(min, max, (row, column))

# 生成随机矩阵A&B
A = generate_matrix(row_A, column_A, MIN, MAX)
B = generate_matrix(row_B, column_B, MIN, MAX)

print(A)
print(B)
print(np.dot(A,B))

# 若随机矩阵A为奇数行，则为其补一行0
if(row_A % 2 != 0):
    temp_array = np.zeros((1, column_A), dtype=np.int16)
    A = np.r_[A, temp_array]
    row_A = row_A + 1
    A_is_odd = 1
else:
    A_is_odd = 0

# run
async def matrix_multipl(group, code, matrix1, matrix2):
    return group, code, np.dot(matrix1,matrix2)

loop = asyncio.get_event_loop()

tasks = []
for i in range(row_A // 2):
    # 将随机矩阵A的每两行视为一组进行编码&分配任务
    tasks.append(matrix_multipl(i, 0, A[2 * i], B))
    tasks.append(matrix_multipl(i, 1, A[2 * i + 1], B))
    tasks.append(matrix_multipl(i, 2, A[2 * i] + A[2 * i + 1], B))

decode = np.zeros((row_A // 2, 4), dtype=np.int16) # 该group收到的result数量[0/1/2] 
temp_answer = np.zeros(((row_A // 2) * 3, column_B), dtype=np.int16)
answer = np.zeros((row_A, column_B), dtype=np.int16)
group_not_done = [i for i in range(row_A // 2)]

done, _ = loop.run_until_complete(asyncio.wait(tasks))
for fut in done:
    group, code, matrix = fut.result()
    if group in group_not_done:
        decode[group][code + 1] = 1
        decode[group][0] = decode[group][0] + 1
        temp_answer[group * 3 + code] = matrix

        if(decode[group][0] == 2):
            group_not_done.remove(group)
            if(decode[group][1] == 0):
                answer[group * 2 + 0] = temp_answer[group * 3 + 2] - temp_answer[group * 3 + 1]
                answer[group * 2 + 1] = temp_answer[group * 3 + 1]
            elif(decode[group][2] == 0):
                answer[group * 2 + 0] = temp_answer[group * 3 + 0]
                answer[group * 2 + 1] = temp_answer[group * 3 + 2] - temp_answer[group * 3 + 0]
            elif(decode[group][3] == 0):
                answer[group * 2 + 0] = temp_answer[group * 3 + 0]
                answer[group * 2 + 1] = temp_answer[group * 3 + 1]
                
loop.close()

if(A_is_odd == 1):
    answer = np.delete(answer,row_A - 1,axis=0)
    row_A = row_A - 1
print(answer)
