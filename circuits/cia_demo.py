from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(3, 3)

   
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(1, 1)

    # Reuse measured qubit WITHOUT reset
    qc.cx(1, 2)   # <-- R1 + R2 trigger
    qc.x(0)
    qc.x(0)       # cancels → R5 trigger
    qc.cx(0, 2)   # requires routing if coupling is linear
    qc.measure([0,1,2], [0,1,2])

    return qc