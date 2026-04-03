from qiskit import QuantumCircuit
from math import pi


def build_circuit():
    qc = QuantumCircuit(4, 4)
    for q in range(4):
        qc.ry((q + 1) * pi / 9, q)
        qc.rz((q + 2) * pi / 11, q)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.cx(3, 0)
    for q in range(4):
        qc.rx((q + 1) * pi / 13, q)
    qc.cz(0, 2)
    qc.cz(1, 3)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw()) 