#groverのアルゴリズムでノイズが発生した場合の計算を行うプログラム
import math
import numpy as np
import random
#事前に決める変数
n = 10
sigma = 0 # ノイズの強さ



N = 2**n
phi = math.acos(1 - (1 / N)) 
reception = math.ceil(math.pi * math.sqrt(N) / 4)

A = [float(0)] * (reception + 1) 
B = [float(0)] * (reception + 1)


for m in range(1, (reception)):
    print("iteration:", m)
    x1 = random.random()
    x2 = random.random()
    print(x1, x2)
    # ノイズの影響を受ける量子ビットの状態を計算
    if m == 1:
        A[m] = (math.cos(phi * m) + math.sqrt(N-1) * math.sin(phi * m))/math.sqrt(N)
        B[m] = (math.cos(phi * m) - (math.sqrt(N-1) * math.sin(phi * m) / math.sqrt(N-1)))/math.sqrt(N)
    
    matrix = np.array([[1 - 2 / N, 2 - 2 / N], [-2 / N, 1 - 2 / N]], dtype=float)
    vector = np.array([A[m], B[m]], dtype=float)

    # 行列計算
    result = np.dot(matrix, vector)  # 行列とベクトルの積
    
    #ノイズを追加
    noise_a = math.sqrt((-2) * sigma * math.log(x1)) * math.sin(2 * math.pi * x2)
    noise_b = math.sqrt((-2) * sigma * math.log(x1)) * math.cos(2 * math.pi * x2)
    
    A[m + 1] = result[0] + noise_a
    B[m + 1] = result[1] + noise_b
    
    correction_N = math.sqrt(A[m + 1]**2 + (N-1) * (B[m + 1] ** 2))
    
    A[m + 1] /= correction_N 
    B[m + 1] /= correction_N 
    
# 結果の表示
print("A:", A)
print("B:", B)   
print(A[1]**2 + (N-1) * (B[1]**2))  # A[1]とB[1]の二乗和を計算して表示s
    

