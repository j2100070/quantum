import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister, execute, BasicAer

# --- パラメータ設定 ---
num_solutions = 1  # オラクルが持つ解の個数
num_qubits = 5     # 解を表現する量子ビットの数
N = 2**num_qubits  # 全探索空間のサイズ

# Groverの繰り返し回数計算
theta_t = math.asin(math.sqrt(num_solutions / N))
num_repetitions = math.ceil(math.pi / (4 * theta_t))

print(f"θ_t (ラジアン): {theta_t:.4f}")
print(f"Groverの繰り返し回数: {num_repetitions}")

# --- ヘルパー関数定義 ---

def initialize_superposition(qc, q_reg, num_qubits):
    """
    量子ビットを均一な重ね合わせ状態に初期化します。
    補助量子ビットq[0]は|->状態に、q[1]以降は|0>からHゲートで重ね合わせにします。
    """
    qc.x(q_reg[0]) # 補助量子ビットを|1>に
    qc.h(q_reg[0]) # 補助量子ビットを|->状態に

    # 解を表現する量子ビットを均一な重ね合わせ状態に
    for i in range(1, num_qubits + 1):
        qc.h(q_reg[i])

def oracle(qc, q_reg, num_qubits):
    """
    オラクルゲートを適用します。
    この例では、解を表現する全ての量子ビットが0の状態を「解」とし、
    その状態の位相を反転させます。
    """
    # 全ビットが0の状態を識別するオラクル
    # Xゲートで反転 -> MCX -> Xゲートで元に戻す
    qc.x(q_reg[1:num_qubits+1]) # 制御ビットを反転
    qc.mcx(q_reg[1:num_qubits+1], q_reg[0]) # MCXゲート適用 (q[0]がターゲット)
    qc.x(q_reg[1:num_qubits+1]) # 制御ビットを元に戻す

def diffusion_operator(qc, q_reg, num_qubits):
    """
    Grover拡散演算子を適用します。
    |s>に対する反転操作 (平均値周りの反転) を行います。
    """
    # Hadamardゲート
    for j in range(1, num_qubits + 1):
        qc.h(q_reg[j])
    
    # Xゲート
    for j in range(1, num_qubits + 1):
        qc.x(q_reg[j])
        
    # マルチ制御Zゲート (H -> MCX -> H で実装)
    # ここでは q[1] をターゲットとし、q[2]からq[num_qubits]を制御とします。
    qc.h(q_reg[1])
    qc.mcx(q_reg[2:num_qubits+1], q_reg[1]) # q[2]から末尾までが制御ビット
    qc.h(q_reg[1])    
        
    # Xゲート (元に戻す)
    for j in range(1, num_qubits + 1):
        qc.x(q_reg[j])
    
    # Hadamardゲート (元に戻す)
    for j in range(1, num_qubits + 1):
        qc.h(q_reg[j])

def plot_results(counts, title="Groverのアルゴリズム測定結果"):
    """
    測定結果を棒グラフでプロットします。
    """
    rcParams['font.family'] = 'Hiragino Sans' # macOSの場合のフォント設定
    plt.figure(figsize=(12, 6))
    plt.bar(counts.keys(), counts.values(), color='skyblue')
    plt.xlabel("測定結果（ビット列）")
    plt.ylabel("出現回数")
    plt.title(title)
    plt.xticks(rotation=90)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# --- 量子回路の構築 ---

# レジスタの定義
q_reg = QuantumRegister(num_qubits + 1, "q")
c_reg = ClassicalRegister(num_qubits, "c")
qc = QuantumCircuit(q_reg, c_reg)

# 初期化
initialize_superposition(qc, q_reg, num_qubits)

# Groverの繰り返し
for rep_idx in range(num_repetitions):
    oracle(qc, q_reg, num_qubits)
    diffusion_operator(qc, q_reg, num_qubits)

# 測定
for i in range(num_qubits):
    qc.measure(q_reg[i+1], c_reg[i])

# --- 量子回路の実行と結果表示 ---
backend = BasicAer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()
counts = result.get_counts(qc)

print("\n--- 測定結果 ---")
print(counts)

print("\n--- 量子回路図 (テキスト形式) ---")
print(qc.draw(output='text', fold=-1))

# 測定結果をデータフレームに変換してソート
df = pd.DataFrame(list(counts.items()), columns=["状態", "出現回数"])
df = df.sort_values(by="出現回数", ascending=False).reset_index(drop=True)

print("\n--- 測定結果 (ソート済みテーブル) ---")
print(df)

# 結果のプロット
plot_results(counts)