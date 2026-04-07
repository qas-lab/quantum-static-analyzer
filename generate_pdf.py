from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import json

# load your report
with open("reports/llm_bell_no_reset_reuse.json") as f:
    data = json.load(f)

doc = SimpleDocTemplate("report.pdf")
styles = getSampleStyleSheet()

content = []

def add(text, style="Normal"):
    content.append(Paragraph(str(text), styles[style]))
    content.append(Spacer(1, 10))


# =========================
# TITLE
# =========================
add("<b>Quantum Security Analysis Report</b>", "Title")

# =========================
# STATUS
# =========================
add(f"<b>Status:</b> {data['status']}")

# =========================
# EXECUTION CONTEXT 
# =========================
add("<b>Execution Context:</b>")
for k, v in data["execution_context"].items():
    add(f"{k}: {v}")

# =========================
# FINDINGS 
# =========================
add("<b>Findings:</b>")

for f in data["findings"]:
    add(f"<b>{f['rule_id']} - {f['title']}</b>")

    add(f"Severity: {f['severity']}")
    add(f"Message: {f['message']}")

    evidence = f["evidence"]

    # 🔥 THIS WAS MISSING (occurrences)
    if "occurrences" in evidence:
        add("<b>Occurrences:</b>")
        for occ in evidence["occurrences"]:
            add(f"{occ}")

    if "vulnerability" in evidence:
        add(f"Vulnerability: {evidence['vulnerability']}")

    if "security_risk" in evidence:
        add(f"Risk: {evidence['security_risk']}")

    add("")  # spacing


# =========================
# METRICS 
# =========================
add("<b>Source Metrics:</b>")
for k, v in data["source_metrics"].items():
    add(f"{k}: {v}")

if data["transpiled_metrics"]:
    add("<b>Transpiled Metrics:</b>")
    for k, v in data["transpiled_metrics"].items():
        add(f"{k}: {v}")


# =========================
# RUNTIME VALIDATION 
# =========================
add("<b>Runtime Validation:</b>")
for k, v in data["runtime_validation"].items():
    add(f"{k}: {v}")


# =========================
# CIA SUMMARY
# =========================
add("<b>CIA Summary:</b>")
for k, v in data["cia_summary"].items():
    add(f"{k}: {v}")


# BUILD PDF
doc.build(content)

print("PDF generated: report.pdf")