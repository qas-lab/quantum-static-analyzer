from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(3, 3)
    qc.h([0, 1, 2])
    qc.cz(0, 2)
    qc.x(1)
    qc.ccx(0, 1, 2)
    qc.x(1)
    qc.h([0, 1, 2])
    qc.x([0, 1, 2])
    qc.h(2)
    qc.ccx(0, 1, 2)
    qc.h(2)
    qc.x([0, 1, 2])
    qc.h([0, 1, 2])
    qc.measure(0, 0)
    qc.x(0)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())