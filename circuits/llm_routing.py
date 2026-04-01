from qiskit import QuantumCircuit


def build_circuit():
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.h(4)
    qc.cx(0, 4)
    qc.cx(4, 0)
    qc.cx(1, 3)
    qc.swap(0, 2)
    qc.swap(2, 4)
    qc.cz(0, 4)
    qc.cx(0, 4)
    qc.cx(4, 2)
    qc.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())