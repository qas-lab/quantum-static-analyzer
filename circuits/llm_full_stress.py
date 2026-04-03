# full_stress.py
from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(3, 3)

    qc.h(0)
    qc.cx(0, 2)   # non-adjacent → routing

    qc.measure(0, 0)

    qc.x(0)       # R1 violation
    qc.h(0)       # R2 violation

    qc.x(1)
    qc.x(1)       # R5 redundant

    qc.cx(2, 1)

    return qc