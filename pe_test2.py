import numpy as np
from scipy.linalg import expm
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit import BasicAer, execute
from qiskit.circuit.library import UnitaryGate


def qft(dag=False):
    sign = -1 if dag else 1
    for l in range(m):
        qc.h(qrB[l])
        for k in range(2, m - l + 1):
            qc.cp(sign * 2 * np.pi / (2**k), qrB[l+k-1], qrB[l])
    for l in range(m // 2):
        qc.swap(qrB[l], qrB[m-l-1])


# 行列 A と時間 t の定義
A = np.array([[1,0],[0,1j]]) 
gate = UnitaryGate(A)
cgate = gate.control(1)
m, M = 4, 16
print(gate)
# 量子レジスターの定義
qrA = QuantumRegister(1, "qrA")
qrB = QuantumRegister(m, "qrB")



# 量子回路の作成
qc = QuantumCircuit(qrB, qrA, )

qc.x(qrA[0])

#HHLを適用
for i in range(m):
    qc.h(qrB[i])
    
#ユニタリ演算を適用    
for i in range(m):
    for _ in range(2**i):
        qc.append(cgate, [qrB[m-1-i], qrA[0]])

# 量子フーリエ変換
qft(dag = True)


plt=qc.draw(output='mpl', style="nicely")

#plt.show()

# 画像を保存
plt.savefig('easy_phase_estimation.png')


svsim=BasicAer.get_backend("statevector_simulator")
result=execute(qc,svsim).result()
statevector=result.get_statevector(qc)
# 測定結果を表示
print(statevector)