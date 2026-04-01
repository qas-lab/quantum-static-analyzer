from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(4, 4)
    qc.h(range(4))
    qc.cz(0, 1)
    qc.cz(0, 2)
    qc.cz(0, 3)
    qc.cz(1, 2)
    qc.cz(1, 3)
    qc.cz(2, 3)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())