# Quantum Static Analyzer – Feature Overview

This project introduces a static analysis framework for detecting security vulnerabilities in quantum programs, particularly in hybrid quantum–classical environments.

The tool focuses on analyzing Qiskit-based circuits to identify structural and compilation-induced risks before execution on simulators or quantum hardware.

---

## Features Implemented

### 1. Static Vulnerability Detection

The analyzer inspects quantum circuits at the structural level to identify security-relevant patterns.

The system parses Qiskit circuit representations and applies rule-based analysis to detect vulnerabilities that may not produce compilation errors but can lead to unintended or unsafe behavior during execution.

---

### 2. Measurement Misuse Detection

The tool identifies unsafe measurement patterns, including:

- Operations applied after measurement  
- Incorrect or inconsistent measurement ordering  
- Improper use of classical feedback  

These issues can introduce information leakage or unintended circuit behavior in hybrid workflows.

---

### 3. Qubit Reuse Analysis

The analyzer detects cases where qubits are reused without proper reset or initialization.

Such patterns may result in residual state leakage, especially in shared or multi-tenant quantum environments.

---

### 4. Compilation-Aware Analysis

The system compares circuits before and after transpilation to identify structural changes introduced during compilation.

This includes:

- Increased circuit depth  
- Additional two-qubit gates  
- SWAP gate insertion due to routing constraints  

These transformations may expose circuits to noise, crosstalk, or other security risks.

---

### 5. Detection of LLM-Generated Code Anomalies

The analyzer identifies structural anomalies commonly found in AI-generated quantum code, including:

- Redundant or ineffective gate sequences  
- Inconsistent circuit construction  
- Use of invalid or hallucinated APIs  

This supports analysis of quantum programs generated using large language models.

---

### 6. Security Report Generation

The system produces structured reports summarizing detected vulnerabilities.

Each report includes:

- Vulnerability type  
- Security impact (Confidentiality, Integrity, Availability)  
- Evidence from the circuit  
- Suggested mitigation strategies  

---

## Project Structure
```
├── analyzer/             # Core analysis logic
│ └── quantum_security_analyzer.py
├── circuits/            # Example and test circuits
├── reports/             # Generated reports
├── analyze_results.py   # Result analysis
├── report_generator.py  # Report generation
├── make_table.py        # Summary generation
├── run_all.sh.          # Pipeline execution script
└── README.md
```
--- 

# Create virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
```
## Install dependencies

```
pip install -r requirements.txt
```

---

## Usage

### Run full analysis pipeline

```bash
./run_all.sh
```

## Run analyzer directly

```
python analyzer/quantum_security_analyzer.py

```

##  Run result analysis
```
python analyze_results.py
```

## Generate summary table
```
python make_table.py
```

## Output

The system generates:

- Structured vulnerability reports
- Analysis summaries
- CSV output (results_table.csv)

Each finding includes detailed information about detected risks and their potential impact.

## Testing

The project follows a structured testing methodology focused on validating detection logic and analysis correctness.

Test cases include:

- Detection of measurement misuse patterns
- Identification of qubit reuse without reset
- Verification of transpilation-induced changes
- Validation of anomaly detection in generated circuits

## Example Output

Below is an example analysis result for a quantum circuit:

```json
{
  "rule_id": "RV1",
  "title": "Noise-induced divergence",
  "severity": "medium",
  "message": "Execution context alters output distribution",
  "impact": {
    "confidentiality": false,
    "integrity": true,
    "availability": true
  },
  "metrics": {
    "tvd": 0.7109,
    "fidelity": 0.2890
  }
}

```

### Interpretation

The analyzer detects divergence between expected and actual circuit behavior due to compilation and execution context.

This impacts:
- Integrity (incorrect results)
- Availability (reliability under noise)


### Output Files

Each analyzed circuit generates a report:

`reports/<circuit_name>.json`

Example:
reports/adder.json

### Reproducing Aggregate Metrics

After ```results_table.csv``` has been generated, you can print the aggregate structural and runtime metrics with:

We used a fixed random seed (`42`) for reproducibility and `4096` shots to reduce sampling variance during simulation. 

```

python3 - <<'PY'
import pandas as pd

df = pd.read_csv("results_table.csv")
m = df[["depth_src", "depth_trans", "tvd", "fidelity"]].mean()

print("source-circuit depth =", round(m["depth_src"], 2))
print("transpiled depth =", round(m["depth_trans"], 2))
print("mean TVD =", round(m["tvd"], 3))
print("mean fidelity =", round(m["fidelity"], 3))
PY

``` 

## Summary

This project improves quantum software reliability by introducing security-aware static analysis.

It enables early detection of vulnerabilities in quantum circuits, including those introduced by compilation, hybrid execution environments, and automated code generation.

The tool supports safer development and evaluation of quantum programs by identifying risks before deployment.


## Acknowledgements

Parts of this project were developed with the assistance of GPT and Claude models, which were used to support code generation, refinement, and implementation.

Some QASM benchmark circuits used in this work were obtained from the Qiskit Benchpress repository:

https://github.com/Qiskit/benchpress/tree/main/benchpress%2Fqasm