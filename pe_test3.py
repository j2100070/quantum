import numpy as np
from scipy.linalg import expm
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit import BasicAer, execute
from qiskit.circuit.library import UnitaryGate
from qiskit.visualization import plot_histogram # 結果をプロットするためにインポート
import matplotlib.pyplot as plt # プロット表示のためにインポート

# グローバル変数として qc と qrB を定義
m = 4
qrB = QuantumRegister(m, "qrB")
qc = QuantumCircuit() # qc は後でレジスタと共に初期化される

def qft(dag=False):
    global qc, qrB # グローバル変数を使用することを明示
    sign = -1 if dag else 1
    for l in range(m):
        qc.h(qrB[l])
        for k in range(2, m - l + 1):
            qc.cp(sign * 2 * np.pi / (2**k), qrB[l+k-1], qrB[l])



# 行列 A の定義
A = np.array([[1,0],[0,(-1)*1j]])
gate = UnitaryGate(A)
cgate = gate.control(1)
# m, M = 4, 16 # m は既にグローバルで定義済みなのでコメントアウト、Mは未使用
print(gate)

# 量子レジスターの定義
qrA = QuantumRegister(1, "qrA")
# qrB は qft 関数内でアクセスできるようグローバルスコープで定義済み

# クラシカルレジスターの定義
# qrB を測定するためのクラシカルレジスター
crB = ClassicalRegister(m, "crB")
# qrA を測定するためのクラシカルレジスター
crA = ClassicalRegister(1, "crA")

# 量子回路の作成 (クラシカルレジスターも追加)
qc = QuantumCircuit(qrB, qrA, crB, crA)

qc.x(qrA[0])

#HHLの一部（位相推定）を適用
for i in range(m):
    qc.h(qrB[i])

#ユニタリ演算を適用
for i in range(m):
    for _ in range(2**i):
        qc.append(cgate, [qrB[m-1-i], qrA[0]])

# 逆量子フーリエ変換
qft(dag = True)

# --- 測定の追加 ---
# qrB の量子ビットを crB のクラシカルビットに測定
qc.measure(qrB, crB)
# qrA の量子ビットを crA のクラシカルビットに測定
qc.measure(qrA, crA)

# 回路の描画 (任意)
print("\nQuantum Circuit:")
print(qc.draw(output='text'))

# バックエンドの選択 (シミュレーター)
backend = BasicAer.get_backend('qasm_simulator')

# 回路の実行
job = execute(qc, backend, shots=1024) # shots は測定回数
result = job.result()

# 結果の取得と表示
counts = result.get_counts(qc)
print("\nMeasurement results:")
print(counts)

# 結果をヒストグラムで表示 (任意)
plot_histogram(counts)
plt.show()