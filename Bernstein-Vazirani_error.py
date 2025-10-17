import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
# NoiseModelとエラーを定義するためにインポート
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
# 結果をプロットするためにインポート
from qiskit.visualization import plot_histogram

# --- ここからノイズモデルの構築 ---

# 1. 空のノイズモデルを作成
noise_model = NoiseModel()

# 2. ゲートエラーを定義: 1量子ビットの脱分極エラー
# error_probability = 1%
error_prob = 0.01 
gate_error = depolarizing_error(error_prob, 1)

# 3. ノイズモデルにゲートエラーを追加
# 単一量子ビットゲートである 'h' と 'x' にこのエラーを適用する
noise_model.add_all_qubit_quantum_error(gate_error, ['h', 'x'])


print("--- 作成したノイズモデル ---")
print(noise_model)
print("--------------------------\n")

# --- ここまでノイズモデルの構築 ---


# 求めたい秘密のビット列 (nビット)
# NOTE: 回路図が見やすいようにビット数を8に減らしています
s = '10110101'
n = len(s)
print(f"秘密のビット列 (s): {s}")
print(f"ビット数 (n): {n}\n")


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
    oracle(qc)
    qc.barrier()
    for i in range(n):
        qc.h(i)

Bernstein_Vazirani(qc)

for i in range(n):
    qc.measure(i, i)

# --- ★★★ 追加部分1: 量子回路図を描画 ★★★ ---
print("--- 量子回路図 ---")
# 'mpl'を指定するとmatplotlibを使って綺麗に描画できる
qc.draw('mpl')
plt.show() # ← これで描画ウィンドウが表示されます
print("------------------\n")


# --- 量子回路の実行と結果表示 ---
# 1. ノイズモデルを使ってシミュレータのインスタンスを作成
simulator = AerSimulator(noise_model=noise_model)

# 2. ショット数を増やして実行
job = simulator.run(qc, shots=1024)

# 3. 結果の取得
result = job.result()
counts = result.get_counts(qc)

print("ノイズありの実行結果:", counts)

# --- ★★★ 追加部分2: 結果をヒストグラムで描画 ★★★ ---
print("\n--- 実行結果のヒストグラム ---")
# countsを引数にしてヒストグラムを作成
plot_histogram(counts, title='ノイズモデルありの実行結果')
plt.show() # ← これで描画ウィンドウが表示されます
print("--------------------------")
