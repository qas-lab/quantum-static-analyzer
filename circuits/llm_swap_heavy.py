from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(4, 4)

    qc.h(0)
    qc.cx(0, 3)

    # artificial swap-heavy pattern
    qc.swap(0, 1)
    qc.swap(1, 2)
    qc.swap(2, 3)

    qc.cx(3, 0)

    qc.measure(range(4), range(4))
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())