from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.cp(0.5, 0, 1)  # 制御位相ゲートを0番目の量子ビットを制御ビット、1番目の量子ビットをターゲットにして適用
qc.draw('mpl')