from qiskit import QuantumCircuit
from qiskit.providers.ibmq import IBMQ

def build_circuit():
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)
    return qc

def get_backend():
    IBMQ.load_account()
    provider = IBMQ.get_provider(hub="ibm-q")
    return provider.get_backend("ibmq_qasm_simulator")

if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())