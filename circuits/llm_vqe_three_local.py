from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(3, 3)
    qc.ry(pi / 7, 0)
    qc.ry(pi / 5, 1)
    qc.ry(pi / 3, 2)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.rz(pi / 6, 0)
    qc.rz(pi / 8, 1)
    qc.rz(pi / 10, 2)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())
