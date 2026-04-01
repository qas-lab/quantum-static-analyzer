from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(4, 4)

    qc.h(0)

    # excessive entanglement chain
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.cx(3, 0)  # loop back (unusual)

    qc.cx(0, 2)
    qc.cx(1, 3)  # redundant cross entanglement

    qc.measure(range(4), range(4))
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())