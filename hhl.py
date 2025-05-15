import numpy as np
from scipy.linalg import expm
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit import BasicAer, execute
from qiskit.circuit.library import UnitaryGate

# 行列 A と時間 t の定義
A, t = np.array([[3,-1],[-1,3]]) /3, 3/4*np.pi
# ラムダ1 = 2/3, 4/3
gate = UnitaryGate(expm(1j*A*t))
cgate = gate.control(1)
m, M = 4, 16

# 量子レジスターの定義
qrA = QuantumRegister(1, "qrA")
qrB = QuantumRegister(m, "qrB")
qrC = QuantumRegister(1, "qrC")


# 量子回路の作成
qc = QuantumCircuit(qrC, qrB, qrA, )

# Step 0: 値の補正
# theta = 2*np.arccos(3/5)  # 回転角を計算
# qc.ry(theta, qrA[0])

def qft(dag=False):
    sign = -1 if dag else 1
    for l in range(m):
        qc.h(qrB[l])
        for k in range(2, m - l + 1):
            qc.cp(sign * 2 * np.pi / (2**k), qrB[l+k-1], qrB[l])
    for l in range(m // 2):
        qc.swap(qrB[l], qrB[m-l-1])

# Step 1: 量子フーリエ変換
for j in range(m):
    qc.h(qrB[j])


# コントロールユニタリ演算
for j in range(m):
    for _ in range(2**j):
        qc.append(cgate, [qrB[m-1-j], qrA[0]])


# 逆量子フーリエ変換
qft(dag=True)

# Hamiltonian Eigenvalue Inverse Step
kbar = 3
C = 2 * np.pi * kbar / M / t
for k in range(kbar, M - (kbar - 1)):
    if k <= M // 2:
        lambda_k = 2 * np.pi * k / M / t
    else:
        lambda_k = 2 * np.pi * (k - M) / M / t
    theta = 2 * np.arcsin(C / lambda_k)

    k_bin = format(k, "0" + str(m) + "b")
    for i in range(m):
        if k_bin[i] == "0":
            qc.x(qrB[i])
    qc.mcry(theta, qrB, qrC)
    for i in range(m):
        if k_bin[i] == "0":
            qc.x(qrB[i])



# 量子フーリエ変換
qft()

# ユニタリ逆変換
for j in range(m):
    for _ in range(2**j):
        qc.append(cgate.inverse(), [qrB[m-1-j], qrA[0]])

# 再度アダマール演算を適用
for j in range(m):
    qc.h(qrB[j])

plt=qc.draw(output='mpl', style="clifford")

#plt.show()

# 画像を保存
plt.savefig('quantum_circuit.png')


svsim=BasicAer.get_backend("statevector_simulator")
result=execute(qc,svsim).result()
statevector=result.get_statevector(qc)
# 測定結果を表示
print(statevector)