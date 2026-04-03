from qiskit import QuantumCircuit, Aer

def build_circuit():
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc

def get_counts():
    qc = build_circuit()
    backend = Aer.get_backend("qasm_simulator")
    job = backend.run(qc, shots=256)
    return job.result().get_counts()

if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())