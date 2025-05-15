from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.swap(0, 1)  # 量子ビット0と1を入れ替える
qc.draw('mpl')