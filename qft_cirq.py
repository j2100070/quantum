
import cirq
import random
import matplotlib.pyplot as plt
import numpy as np
    
    
def make_qft(qubits):
    """Generator for the QFT on a list of qubits."""
    qreg = list(qubits)
    while len(qreg) > 0:
        q_head = qreg.pop(0)
        yield cirq.H(q_head)
        for i, qubit in enumerate(qreg):
            yield (cirq.CZ ** (1 / 2 ** (i + 1)))(qubit, q_head)

"""Visually check the QFT circuit."""
qubits = cirq.LineQubit.range(4)
qft = cirq.Circuit(make_qft(qubits))
print(qft)            