import numpy as np
from scipy.linalg import expm
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit import BasicAer, execute
from qiskit.circuit.library import UnitaryGate

# 行列 A と時間 t の定義
A, t = np.array([[3, 1], [1, -3]]) / 16, 2.53 * np.pi
b = np.array([0, 1])
gate = UnitaryGate(expm(1j * A * t))
cgate = gate.control(1)
m, M = 4, 16

# 量子レジスターの定義
qrA = QuantumRegister(1, "qrA")
qrB = QuantumRegister(m, "qrB")
qrC = QuantumRegister(1, "qrC")
crA = ClassicalRegister(1, "crA")  # 測定用古典レジスター

# 量子回路の作成
qc = QuantumCircuit(qrC, qrB, qrA, crA)

# 初期状態作成: 3/5|0> + 4/5|1>
theta = 2 * np.arcsin(4 / 5)
qc.ry(theta, qrA[0])  # Ryゲートで状態作成

# 測定操作の追加 (qrAの状態確認用)
qc.measure(qrA[0], crA[0])

# シミュレーションと結果取得
backend = BasicAer.get_backend("qasm_simulator")
result = execute(qc, backend, shots=1000).result()
counts = result.get_counts(qc)

# 結果の表示
print(counts)