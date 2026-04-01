from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    qc.cp(pi / 2, 1, 0)
    qc.cp(pi / 4, 2, 0)
    qc.cp(pi / 8, 3, 0)
    qc.h(1)
    qc.cp(pi / 2, 2, 1)
    qc.cp(pi / 4, 3, 1)
    qc.h(2)
    qc.cp(pi / 2, 3, 2)
    qc.h(3)
    qc.swap(0, 3)
    qc.swap(1, 2)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())