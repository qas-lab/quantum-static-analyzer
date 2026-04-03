from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.swap(0, 4)
    qc.cx(4, 2)
    qc.swap(4, 1)
    qc.cz(1, 3)
    qc.swap(3, 0)
    qc.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())