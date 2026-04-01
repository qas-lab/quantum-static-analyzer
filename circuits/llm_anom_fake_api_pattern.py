from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(2, 2)

    qc.h(0)

    #  fake / suspicious pattern (looks plausible but meaningless)
    for _ in range(2):
        qc.cx(0, 1)
        qc.cx(1, 0)  # oscillating pattern (no real benefit)

    qc.barrier()

    qc.measure([0, 1], [0, 1])
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())