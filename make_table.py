import json
import os
import pandas as pd

pd.set_option("display.max_columns", None)

rows = []
REPORTS_DIR = "reports"
LABELS_PATH = "llm_intent_labels.csv"


def load_json_safely(path: str):
    """Load a JSON report, with a fallback for trailing garbage."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            return json.loads(content)
        except Exception:
            # attempt to trim extra garbage after JSON
            content = content.split("}\n")[0] + "}"
            return json.loads(content)

    except Exception as e:
        print(f"Skipping bad file: {os.path.basename(path)} ({e})")
        return None


for filename in os.listdir(REPORTS_DIR):
    if not filename.endswith(".json"):
        continue

    path = os.path.join(REPORTS_DIR, filename)
    data = load_json_safely(path)
    if data is None:
        continue

    findings = data.get("findings", [])
    rules = {f.get("rule_id") for f in findings}

    # ===== EXTRACT VULNERABILITIES + MITIGATIONS =====
    vulnerability_labels = []
    mitigation_items = []
    mitigation_priorities = set()

    for f in findings:
        evidence = f.get("evidence", {})

        vulnerability_name = evidence.get(
            "vulnerability",
            f.get("title", f.get("rule_id", "UNKNOWN"))
        )
        if vulnerability_name not in vulnerability_labels:
            vulnerability_labels.append(vulnerability_name)

        priority = f.get("mitigation_priority")
        if priority:
            mitigation_priorities.add(priority)

        for item in f.get("mitigation", []):
            if item not in mitigation_items:
                mitigation_items.append(item)

    # ===== FALLBACK TO MITIGATION SUMMARY FOR OLDER REPORTS =====
    if not mitigation_items:
        ms = data.get("mitigation_summary", {})
        for level in ["high_priority", "medium_priority", "low_priority"]:
            for item in ms.get(level, []):
                if item not in mitigation_items:
                    mitigation_items.append(item)

    if not mitigation_priorities:
        ms = data.get("mitigation_summary", {})
        if ms.get("high_priority"):
            mitigation_priorities.add("high")
        if ms.get("medium_priority"):
            mitigation_priorities.add("medium")
        if ms.get("low_priority"):
            mitigation_priorities.add("low")

    # ===== CATEGORY LABEL =====
    category = (
        "LLM" if filename.startswith("llm_") else
        "routing" if "route" in filename else
        "qft" if "qft" in filename else
        "teleport" if "teleport" in filename else
        "vqe" if "vqe" in filename else
        "sdk" if "sdk" in filename else
        "safe" if "safe" in filename else
        "other"
    )

    row = {
        "circuit_name": filename.replace(".json", ""),
        "category": category,

        "LLM": int(filename.startswith("llm_")),
        "failed": int(data.get("status") != "ok"),

        # ===== RULE FLAGS =====
        "R1": int("R1" in rules),
        "R2": int("R2" in rules),
        "R3": int("R3" in rules),
        "R4": int("R4" in rules),
        "R5": int("R5" in rules),
        "RV1": int("RV1" in rules),

        # ===== VULNERABILITY / MITIGATION COLUMNS =====
        "vulnerabilities": " | ".join(vulnerability_labels) if vulnerability_labels else "",
        "mitigation_priorities": " | ".join(sorted(mitigation_priorities)) if mitigation_priorities else "",
        "mitigation_count": len(mitigation_items),
        "top_mitigation": mitigation_items[0] if mitigation_items else "",

        # ===== METRICS =====
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

# ===== VULNERABLE FLAG =====
if not df.empty:
    df["vulnerable"] = (
        (df["R1"] | df["R2"] | df["R3"] | df["R4"] | df["R5"] | df["RV1"]).astype(int)
    )
else:
    df["vulnerable"] = pd.Series(dtype=int)

# ===== MERGE MANUAL LLM INTENT LABELS =====
if os.path.exists(LABELS_PATH):
    labels_df = pd.read_csv(LABELS_PATH)
    df = df.merge(labels_df, on="circuit_name", how="left")
else:
    df["intent"] = None

# ===== SAVE TABLE =====
df.to_csv("results_table.csv", index=False)

# ===== DISPLAY =====
if not df.empty:
    print(df.head().to_string())
else:
    print("No valid report rows found.")

# ===== INTENT COUNTS =====
print("\n=== INTENT COUNTS ===")
if "intent" in df.columns and not df.empty:
    print(df["intent"].value_counts(dropna=False))
else:
    print("No intent data available.")

# ===== SUMMARY STATS =====
print("\n=== SUMMARY ===")
if not df.empty:
    print("Vulnerability rate:", df["vulnerable"].mean())
    print("R1:", df["R1"].mean())
    print("R2:", df["R2"].mean())
    print("R3:", df["R3"].mean())
    print("R4:", df["R4"].mean())
    print("R5:", df["R5"].mean())
    print("RV1:", df["RV1"].mean())
    print("Failures:", df["failed"].mean())
    print("Average mitigation count:", df["mitigation_count"].mean())
else:
    print("No data available.")

# ===== LLM VS NON-LLM =====
print("\n=== LLM vs NON-LLM ===")
if not df.empty:
    llm_df = df[df["LLM"] == 1]
    non_llm_df = df[df["LLM"] == 0]

    print("LLM vulnerable:", llm_df["vulnerable"].mean() if not llm_df.empty else "N/A")
    print("Non-LLM vulnerable:", non_llm_df["vulnerable"].mean() if not non_llm_df.empty else "N/A")
else:
    print("No data available.")

# ===== BENCHMARK / ISSUE-SEEKING / CLEAN-CONTROL =====
print("\n=== BENCHMARK / ISSUE-SEEKING / CLEAN-CONTROL ===")

benchmark_df = df[df["LLM"] == 0]
issue_df = df[df["intent"] == "issue_seeking"]
clean_df = df[df["intent"] == "clean_control"]

for name, sub in [
    ("Benchmark", benchmark_df),
    ("Issue-seeking", issue_df),
    ("Clean control", clean_df),
]:
    if sub.empty:
        print(f"\n{name}: no data")
        continue

    print(f"\n{name}")
    print("Vulnerable:", sub["vulnerable"].mean())
    print("R1:", sub["R1"].mean())
    print("R2:", sub["R2"].mean())
    print("R3:", sub["R3"].mean())
    print("R4:", sub["R4"].mean())
    print("R5:", sub["R5"].mean())
    print("RV1:", sub["RV1"].mean())