# Grover's algorithm
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit import BasicAer, execute
# 状態重ね合わせ
def superposition(nqubits):
    for qubit in range(nqubits):
        qc.h(qubit)

    
# オラクル    
def oracle(nqubits):
    #qc.cz(0, 1)
    qc.x(2)
    qc.x(0)
    # マルチ制御Zゲートをかけます
    qc.h(nqubits-1)
    qc.mct(list(range(nqubits-1)), nqubits-1)  # マルチ制御トフォリ
    qc.h(nqubits-1)
    qc.x(2)
    qc.x(0)

    
def diffuser(nqubits):
    for qubit in range(nqubits):
        qc.h(qubit)
        qc.x(qubit)
        
    # マルチ制御Zゲートをかけます
    qc.h(nqubits-1)
    qc.mct(list(range(nqubits-1)), nqubits-1)  # マルチ制御トフォリ
    qc.h(nqubits-1)
    
    for qubit in range(nqubits):
        qc.x(qubit)
        qc.h(qubit)

        
# 測定
def measure(nqubits):
    for qubit in range(nqubits):
        qc.measure(qubit, qubit)
    
    
nqubits = 4
qc = QuantumCircuit(nqubits, nqubits)

superposition(nqubits)
qc.barrier(list(range(nqubits)))

for num in range(2):
    oracle(nqubits)
    qc.barrier(list(range(nqubits)))
    diffuser(nqubits)
    qc.barrier(list(range(nqubits)))

measure(nqubits)

    
plt=qc.draw(output='mpl', style="nicely")

#plt.show()

# 画像を保存
plt.savefig('grover.png')
svsim=BasicAer.get_backend("statevector_simulator")
result=execute(qc,svsim).result()
statevector=result.get_statevector(qc)
# 測定結果を表示
print(statevector)
