import json

def handle(req):
    json_req = json.loads(req)
    result = {}
    result['is_add'] = json_req['is_add']
    result['column'] = json_req['column']
    result['group'] = json_req['group']
    result['code'] = json_req['code']

    if(json_req['is_add'] != 2):
        matrix1 = json_req['matrix1']
        matrix2 = json_req['matrix2']
        answer = [[ 0 for j in range(len(matrix2[0]))] for i in range(len(matrix1))]

        for i in range(len(matrix1)):
            for j in range(len(matrix2[0])):
                for k in range(len(matrix1[0])):
                    answer[i][j] = answer[i][j] + matrix1[i][k] * matrix2[k][j]
        
        result['answer'] = answer

    return json.dumps(result)