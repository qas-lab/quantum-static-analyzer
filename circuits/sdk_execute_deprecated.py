from qiskit import QuantumCircuit, Aer, execute

def build_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def run_circuit():
    qc = build_circuit()
    backend = Aer.get_backend("qasm_simulator")
    job = execute(qc, backend=backend, shots=1024)
    return job.result()

if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())