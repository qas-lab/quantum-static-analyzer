from qiskit import QuantumCircuit
import numpy as np

def build_circuit():
    qc = QuantumCircuit(3, 3)

    # QFT (clean, no misuse)
    qc.h(0)
    qc.cp(np.pi/2, 1, 0)
    qc.cp(np.pi/4, 2, 0)

    qc.h(1)
    qc.cp(np.pi/2, 2, 1)

    qc.h(2)

    # swap qubits (standard QFT output ordering)
    qc.swap(0, 2)

    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())