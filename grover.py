#解の個数が既知の場合のGroverのアルゴリズム

import numpy as np
import math
import pandas as pd
from scipy.linalg import expm
import matplotlib.pyplot as plt
from matplotlib import rcParams
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit import BasicAer, execute
from qiskit.circuit.library import UnitaryGate

t = 1 # オラクルの解の個数
n = 5 # 量子ビットの数
N = 2**n 

theta_t = math.asin(math.sqrt(t/N))
print(theta_t)
repetition = math.ceil(math.pi/(4*theta_t)) # 繰り返し回数
print(repetition)

# groverのコード    

q = QuantumRegister(n+1, "q")

c = ClassicalRegister(n+1, "c")
# 量子回路の作成
qc = QuantumCircuit(q, c)


qc.x(q[0])


for i in range(n+1):
    # スーパーポジションを作成
    qc.h(q[i])
    
for i in range(repetition):    
    qc.mcx([q[i+1] for i in range(n-1)], q[0]) # オラクルのゲート

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
job = execute(qc, backend, shots=1024)
result = job.result()
# 結果の取得と表示
counts = result.get_counts(qc)
print("\nMeasurement results:")
print(counts)
# 回路の描画 (任意)
print("\nQuantum Circuit:")
print(qc.draw(output='text'))
# 測定結果をデータフレームに変換してソート
df = pd.DataFrame(list(counts.items()), columns=["状態", "出現回数"])
df = df.sort_values(by="出現回数", ascending=False).reset_index(drop=True)

# 表形式で表示
print(df)
# 回路の画像を保存
#qc.draw(output='mpl', filename='grover_circuit.png')

# 棒グラフで視覚化
rcParams['font.family'] = 'Hiragino Sans' #macの場合記述
plt.figure(figsize=(12,6))
plt.bar(counts.keys(), counts.values(), color='skyblue')
plt.xlabel("測定結果（ビット列）")
plt.ylabel("出現回数")
plt.title("Grover測定結果")
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()