from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(4, 4)

    # Create entanglement across non-adjacent qubits
    qc.h(0)
    qc.cx(0, 3)   # ❗ requires routing in linear topology

    qc.h(1)
    qc.cx(1, 3)   # ❗ again non-adjacent

    qc.h(2)
    qc.cx(2, 0)   # ❗ reverse direction stress

    # Add more pressure
    qc.cx(3, 1)
    qc.cx(0, 2)

    # Final measurements
    qc.measure_all()

    return qc