from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(2, 2)
    qc.ry(pi / 7, 0)
    qc.rz(pi / 5, 0)
    qc.ry(pi / 3, 1)
    qc.rz(pi / 4, 1)
    qc.cx(0, 1)
    qc.ry(pi / 9, 0)
    qc.ry(pi / 8, 1)
    qc.measure([0, 1], [0, 1])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())
