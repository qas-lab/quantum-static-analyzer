from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(1, 1)

    qc.h(0)
    qc.z(0)
    qc.z(0)  # cancels out (dead effect)

    qc.x(0)
    qc.x(0)  # cancels out (dead effect)

    qc.measure(0, 0)
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())