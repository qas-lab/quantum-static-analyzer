from qiskit import QuantumCircuit
from qiskit.opflow import Z, I, StateFn, CircuitStateFn

def build_circuit():
    qc = QuantumCircuit(1)
    qc.h(0)
    return qc

def legacy_expectation():
    qc = build_circuit()
    psi = CircuitStateFn(qc)
    observable = StateFn(Z ^ I)
    return (~observable @ psi)

if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())