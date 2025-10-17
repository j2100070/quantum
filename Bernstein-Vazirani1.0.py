# Qiskit 1.0以上では、シミュレータは qiskit_aer パッケージからインポートします
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit_aer import AerSimulator

# 求めたい秘密のビット列 (nビット)
s = '101'
n = len(s)

# --- 量子回路の作成 ---
qc = QuantumCircuit(n + 1, n)


def oracle(qc):
    for i, bit in enumerate(reversed(s)):
        if bit == '1':
            qc.cx(i, n)

def Bernstein_Vazirani(qc):
    qc.x(n)
    qc.h(n)
    
    for i in range(n):
        qc.h(i)
        
    qc.barrier()

    # --- オラクルを適用 ---
    oracle(qc)
    
    qc.barrier()

    for i in range(n):
        qc.h(i)

Bernstein_Vazirani(qc)

# --- 測定 ---
# 入力ビット(0からn-1)のみを測定する
for i in range(n):
    qc.measure(i, i)


# --- 量子回路の実行と結果表示 ---
# 1. シミュレータのインスタンスを作成
simulator = AerSimulator()

# 2. シミュレータのrunメソッドで回路を実行
job = simulator.run(qc, shots=1)

# 3. 結果の取得
result = job.result()
counts = result.get_counts(qc)

print("実行結果:", counts)
# 実行結果: {'101': 1} と表示されるはず
      
    
    
