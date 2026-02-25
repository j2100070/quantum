import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Qiskit 1.0+ のインポート
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# --- パラメータ設定 ---
num_solutions = 1
num_qubits = 5
N = 2**num_qubits

theta_t = math.asin(math.sqrt(num_solutions / N))
num_repetitions = math.ceil(math.pi / (4 * theta_t))

print(f"θ_t (ラジアン): {theta_t:.4f}")
print(f"Groverの繰り返し回数: {num_repetitions}")

# --- ヘルパー関数定義 ---

def initialize_superposition(qc, q_reg, num_qubits):
    qc.x(q_reg[0])
    qc.h(q_reg[0])
    for i in range(1, num_qubits + 1):
        qc.h(q_reg[i])

def oracle(qc, q_reg, num_qubits):
    # 全ビットが0の状態を解とする
    qc.x(q_reg[1:num_qubits+1])
    qc.mcx(list(range(1, num_qubits + 1)), q_reg[0])
    qc.x(q_reg[1:num_qubits+1])

def diffusion_operator(qc, q_reg, num_qubits):
    for j in range(1, num_qubits + 1):
        qc.h(q_reg[j])
    for j in range(1, num_qubits + 1):
        qc.x(q_reg[j])
    
    qc.h(q_reg[1])
    # 制御ビットのリストを指定
    qc.mcx(list(range(2, num_qubits + 1)), q_reg[1])
    qc.h(q_reg[1])    
        
    for j in range(1, num_qubits + 1):
        qc.x(q_reg[j])
    for j in range(1, num_qubits + 1):
        qc.h(q_reg[j])
        
def apply_depolarizing_noise(qc, q_reg, num_qubits, p):
    """
    回路に直接デポラライジングエラーを挿入します。
    """
    error = depolarizing_error(p, 1)
    for j in range(1, num_qubits + 1):
        # ゲート操作としてエラーを適用
        qc.append(error, [q_reg[j]])

def plot_results(counts, title="Groverのアルゴリズム測定結果"):
    # フォント設定（環境に合わせて変更してください）
    try:
        rcParams['font.family'] = 'Hiragino Sans' 
    except:
        pass 
        
    plt.figure(figsize=(12, 6))
    # Qiskitのcountsからプロット
    keys = list(counts.keys())
    values = list(counts.values())
    plt.bar(keys, values, color='skyblue')
    plt.xlabel("測定結果（ビット列）")
    plt.ylabel("出現回数")
    plt.title(title)
    plt.xticks(rotation=90)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# --- 量子回路の構築 ---

q_reg = QuantumRegister(num_qubits + 1, "q")
c_reg = ClassicalRegister(num_qubits, "c")
qc = QuantumCircuit(q_reg, c_reg)

initialize_superposition(qc, q_reg, num_qubits)

# Groverの繰り返し
error_probability = 0.05
for rep_idx in range(num_repetitions):
    oracle(qc, q_reg, num_qubits)
    diffusion_operator(qc, q_reg, num_qubits)
    # 各反復の終わりにノイズを適用
    apply_depolarizing_noise(qc, q_reg, num_qubits, error_probability)

# 測定
for i in range(num_qubits):
    qc.measure(q_reg[i+1], c_reg[i])

# --- 量子回路の実行 ---

# AerSimulatorを使用
backend = AerSimulator()
# 回路をバックエンドに合わせて最適化
transpiled_qc = transpile(qc, backend)
# 実行
job = backend.run(transpiled_qc, shots=100000)
result = job.result()
counts = result.get_counts()

print("\n--- 測定結果 ---")
print(counts)

# 測定結果をデータフレームに変換
df = pd.DataFrame(list(counts.items()), columns=["状態", "出現回数"])
df = df.sort_values(by="出現回数", ascending=False).reset_index(drop=True)

print("\n--- 測定結果 (ソート済みテーブル) ---")
print(df)

# 結果のプロット
plot_results(counts)
    

