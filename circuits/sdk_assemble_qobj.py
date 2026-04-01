from qiskit import QuantumCircuit, Aer, transpile, assemble

def build_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def run_qobj():
    qc = build_circuit()
    backend = Aer.get_backend("qasm_simulator")
    tqc = transpile(qc, backend)
    qobj = assemble(tqc, backend=backend, shots=512)
    return backend.run(qobj).result()

if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())