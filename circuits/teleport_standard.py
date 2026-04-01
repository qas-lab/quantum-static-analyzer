from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(3, 3)
    qc.h(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    qc.z(2)
    qc.x(2)
    qc.measure(2, 2)
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())