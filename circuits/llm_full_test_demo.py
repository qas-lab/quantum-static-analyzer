from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(4, 4)

    # --- Entanglement (normal behavior)
    qc.h(0)
    qc.cx(0, 3)   # long-range → will force routing under coupling map

    # --- R5: redundant gates
    qc.x(1)
    qc.x(1)

    # --- R1: measurement misuse
    qc.measure(0, 0)
    qc.h(0)   # operation AFTER measurement

    # --- R2: reuse without reset
    qc.measure(1, 1)
    qc.cx(1, 2)  # reuse measured qubit

    # --- More structure to increase depth
    qc.cx(3, 2)
    qc.cx(2, 1)
    qc.cx(1, 0)

    # Final measurements
    qc.measure_all()

    return qc