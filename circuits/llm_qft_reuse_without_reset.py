from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cp(pi / 2, 1, 0)
    qc.h(1)
    qc.measure(2, 2)
    qc.x(2)
    qc.cp(pi / 4, 2, 0)
    qc.measure([0, 1], [0, 1])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())