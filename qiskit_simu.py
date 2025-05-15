from qiskit import QuantumRegister,QuantumCircuit
from qiskit import BasicAer,execute
qr=QuantumRegister(2,"qr")
qc=QuantumCircuit(qr)
#量子回路の部分
qc.h(qr[0])
qc.cx(qr[0],qr[1])
#状態ベクトルを取得する
svsim=BasicAer.get_backend("statevector_simulator")
result=execute(qc,svsim).result()
statevector=result.get_statevector(qc)
#10.707+0.30.+0.30.+0.30.707+0.j1と表示される
print(statevector)