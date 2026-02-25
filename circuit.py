from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

# --- 量子回路の作成 ---
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

# --- 元の量子回路 ---
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.x(1)
qc.measure([0, 1], [0, 1])

# --- 古典ビットを除いた回路を作成 ---
qc_no_clbits = QuantumCircuit(2)
qc_no_clbits.h(0)
qc_no_clbits.cx(0, 1)
qc_no_clbits.x(1)
qc_no_clbits.measure_all()

# --- 描画と保存 ---
fig = qc_no_clbits.draw(output='mpl')
fig.savefig("quantum_circuit_no_clbits.png", dpi=300, bbox_inches='tight')

print("古典ビット線を除いた回路図を 'quantum_circuit_no_clbits.png' に保存しました。")
