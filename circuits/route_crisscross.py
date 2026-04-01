from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(6, 6)
    qc.h(0)
    qc.h(5)
    qc.cx(0, 5)
    qc.cx(1, 4)
    qc.cx(2, 3)
    qc.cz(0, 3)
    qc.cz(2, 5)
    qc.measure(range(6), range(6))
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())