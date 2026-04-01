from qiskit import QuantumCircuit

def build_circuit():
    qc = QuantumCircuit(2, 1)  # only 1 classical bit

    qc.h(0)
    qc.cx(0, 1)

    qc.measure(0, 0)
    qc.measure(1, 0)  #  overwrite same classical bit

    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc.draw())