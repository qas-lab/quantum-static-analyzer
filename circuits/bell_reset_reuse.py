from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    qc.reset(0)
    qc.h(0)
    qc.measure(1, 1)
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())