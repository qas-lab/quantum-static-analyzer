from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    qc.ry(pi / 3, 1)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.rz(pi / 7, 0)
    qc.rz(pi / 7, 0)
    qc.cx(3, 0)
    qc.cx(0, 2)
    qc.cx(2, 1)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())
