from qiskit import QuantumCircuit

qc = QuantumCircuit(4, 4)

qc.h(0)
qc.cx(0, 3)
qc.cx(0, 3)
qc.cx(0, 3)   # repeated far interaction → forces swaps

qc.measure([0,1,2,3], [0,1,2,3])