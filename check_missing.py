import os
import pandas as pd

# Get all qasm files (without extension)
qasm_files = set(f.replace(".qasm", "") for f in os.listdir("circuits") if f.endswith(".qasm"))

# Load table
df = pd.read_csv("results_table.csv")
table_circuits = set(df["circuit_name"])

# Find differences
missing_in_table = qasm_files - table_circuits
extra_in_table = table_circuits - qasm_files

print("Missing in table:", missing_in_table)
print("Extra in table:", extra_in_table)
