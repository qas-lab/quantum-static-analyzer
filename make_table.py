import pandas as pd
# ensures all columns show
pd.set_option("display.max_columns", None)  

import json
import os

rows = []

REPORTS_DIR = "reports"

for filename in os.listdir(REPORTS_DIR):
    if not filename.endswith(".json"):
        continue

    path = os.path.join(REPORTS_DIR, filename)

    # ===== SAFE JSON LOADING =====
    try:
        with open(path) as f:
            content = f.read()

            try:
                data = json.loads(content)
            except:
                # attempt to trim extra garbage after JSON
                content = content.split("}\n")[0] + "}"
                data = json.loads(content)

    except Exception as e:
        print(f"Skipping bad file: {filename} ({e})")
        continue

    findings = data.get("findings", [])
    rules = {f["rule_id"] for f in findings}

    row = {
        "circuit_name": filename.replace(".json", ""),

        "category": (
            "LLM" if filename.startswith("llm_") else
            "routing" if "route" in filename else
            "qft" if "qft" in filename else
            "teleport" if "teleport" in filename else
            "vqe" if "vqe" in filename else
            "sdk" if "sdk" in filename else
            "safe" if "safe" in filename else
            "other"
        ),

        "LLM": int(filename.startswith("llm_")),
        "failed": int(data.get("status") != "ok"),

        #  Add R1, R2, R3, R4, R5, RV1 as binary features
        "R1": int("R1" in rules),
        "R2": int("R2" in rules),
        "R3": int("R3" in rules),
        "R4": int("R4" in rules),
        "R5": int("R5" in rules),
        "RV1": int("RV1" in rules),

        "fidelity": data.get("runtime_validation", {}).get("fidelity"),
        "tvd": data.get("runtime_validation", {}).get("tvd"),
        "depth_src": data.get("source_metrics", {}).get("depth"),
        "depth_trans": (
            data.get("transpiled_metrics", {}).get("depth")
            if data.get("transpiled_metrics") else None
        ),
    }

    rows.append(row)

# ===== BUILD DATAFRAME =====
df = pd.DataFrame(rows)

#  Include all in vulnerable
df["vulnerable"] = (
    (df["R1"] | df["R2"] | df["R3"] | df["R4"] | df["R5"] | df["RV1"]).astype(int)
)

# save table
df.to_csv("results_table.csv", index=False)

#  Forcing full display
print(df.head().to_string())

# ===== SUMMARY STATS =====
print("\n=== SUMMARY ===")
print("Vulnerability rate:", df["vulnerable"].mean())
print("R1:", df["R1"].mean())
print("R2:", df["R2"].mean())
print("R3:", df["R3"].mean())
print("R4:", df["R4"].mean())
print("R5:", df["R5"].mean())
print("RV1:", df["RV1"].mean())
print("Failures:", df["failed"].mean())

print("\n=== LLM vs NON-LLM ===")
print("LLM vulnerable:", df[df["LLM"] == 1]["vulnerable"].mean())
print("Non-LLM vulnerable:", df[df["LLM"] == 0]["vulnerable"].mean())