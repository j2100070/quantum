# 解の個数が未知の場合のgroverのアルゴリズム


import numpy as np
import math
import pandas as pd
from scipy.linalg import expm
import matplotlib.pyplot as plt
from matplotlib import rcParams
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit import BasicAer, execute
from qiskit.circuit.library import UnitaryGate


def str_to_list(bit_str, reverse=False):
    """ビット列の文字列をリストに変換する関数"""
    if reverse:
        return [int(bit) for bit in bit_str[::-1]] # 逆順にしてリスト化
    else:
        return [int(bit) for bit in bit_str]



def oracle_gate(qc):
    qc.mcx([q[i+1] for i in range(n-1)], q[0]) # オラクルのゲート
    
def check_oracle_solution(ans_bit): # 出力されたビット列がオラクルのゲートで解が正しいか確認する関数
    q = QuantumRegister(n+1, "q")


    c = ClassicalRegister(n+1, "c")
    # 量子回路の作成
    qc = QuantumCircuit(q, c)
    # ans_bitをリストにする
    
    ans_list = str_to_list(ans_bit, reverse=True)
    print(ans_list)
    
    #1であればビット反転を行う
    for i in range(n):
        if ans_list[i+1] == 1:
            qc.x(q[i+1])
    
    oracle_gate(qc)
    qc.measure(q[0], c[0])
    backend = BasicAer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1)
    result = job.result()
    # 結果の取得と表示
    counts = result.get_counts(qc)
    
    ans_list = str_to_list(list(counts.keys())[0], reverse=True)

    if ans_list[0] == 1:
        print("解あり")
        return True
    else:
        print("解なし")
        return False
     
n = 10 # 量子ビットの数
N = 2**n 
r = 0
# groverのコード    
while True:
    q = QuantumRegister(n+1, "q")


    c = ClassicalRegister(n+1, "c")
    # 量子回路の作成
    qc = QuantumCircuit(q, c)


    qc.x(q[0])


    for i in range(n+1):
        # スーパーポジションを作成
        qc.h(q[i])
        
    for i in range(2**(r)):    
        # オラクルゲートの適用
        oracle_gate(qc)

        #groveroperator
        for j in range(n):
            qc.h(q[j+1])
        for j in range(n):
            qc.x(q[j+1])
            
        qc.h(q[1])
        qc.mcx([q[i+1] for i in range(1, n)], q[1])   
        qc.h(q[1])    
            
        for j in range(n):
            qc.x(q[j+1])
        for j in range(n):
            qc.h(q[j+1])
            
    #測定        
    for i in range(n):
        qc.measure(q[i+1], c[i+1])                    


    # 量子回路の実行
    backend = BasicAer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1)
    result = job.result()
    # 結果の取得と表示
    counts = result.get_counts(qc)
    print("\nMeasurement results:")
    print(counts)
    # 解の確認
    if check_oracle_solution((list(counts.keys())[0])):
        print(f"Solution found after {2**r} iterations: {list(counts.keys())[0]}")
        break
    else:
        print(f"No solution found after {2**r} iterations, continue...")
        r += 1
    
