from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.cx(0, 4)
    qc.measure(4, 4)
    qc.reset(4)
    qc.swap(4, 1)
    qc.cz(1, 3)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())