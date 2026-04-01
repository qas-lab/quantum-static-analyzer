from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(pi / 4, 2)
    qc.cx(2, 3)
    qc.measure(1, 1)
    qc.cx(3, 4)
    qc.reset(1)
    qc.h(1)
    qc.cx(1, 4)
    qc.cx(1, 4)
    qc.swap(0, 4)
    qc.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())