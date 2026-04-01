from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(1, 1)
    qc.reset(1)
    qc.cx(1, 2)
    qc.measure([0, 2], [0, 2])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())