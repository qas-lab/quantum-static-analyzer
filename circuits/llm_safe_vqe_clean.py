from qiskit import QuantumCircuit
import numpy as np

def build_circuit():
    qc = QuantumCircuit(2, 2)

    # simple ansatz (clean VQE-style circuit)
    theta = np.pi / 3

    qc.ry(theta, 0)
    qc.ry(theta, 1)

    qc.cx(0, 1)

    qc.ry(theta, 0)
    qc.ry(theta, 1)

    qc.measure([0, 1], [0, 1])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())