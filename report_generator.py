import json
import os

def generate_report(report_data, output_path):
    """
    Save ONE clean JSON report per circuit
    """

    #  Making sure reports folder exists
    os.makedirs("reports", exist_ok=True)

    #  WRITE CLEAN JSON 
    with open(output_path, "w") as f:
        json.dump(report_data, f, indent=2)

    #  PRINT separately (NOT inside JSON)
    print(f"[OK] Report saved to {output_path}")


def generate_markdown(report_data, output_md_path):
    """
    Generate Markdown report (optional, per circuit)
    """

    with open(output_md_path, "w") as out:

        # =====================
        # Title
        # =====================
        out.write("# Quantum Circuit Security Analysis Report\n\n")

        # =====================
        # Execution Context
        # =====================
        ctx = report_data.get("execution_context", {})
        out.write("## Execution Context\n")
        out.write(f"- Basis Gates: {', '.join(ctx.get('basis_gates', []))}\n")
        out.write(f"- Coupling Map: {ctx.get('coupling_map')}\n")
        out.write(f"- Optimization Level: {ctx.get('optimization_level')}\n")
        out.write(f"- Noise Model: {ctx.get('noise_model')}\n\n")

        # =====================
        # Findings
        # =====================
        out.write("## Findings\n")
        for f in report_data.get("findings", []):
            out.write(f"### {f['rule_id']} — {f['title']} ({f['severity']})\n")
            out.write(f"{f['message']}\n\n")

            impact = f.get("impact", {})
            out.write(f"- Confidentiality: {impact.get('confidentiality')}\n")
            out.write(f"- Integrity: {impact.get('integrity')}\n")
            out.write(f"- Availability: {impact.get('availability')}\n")

            evidence = f.get("evidence", {})
            if "occurrences" in evidence:
                out.write("\n- Evidence:\n")
                for occ in evidence["occurrences"]:
                    out.write(f"  - {occ}\n")

            out.write("\n")

        # =====================
        # Metrics
        # =====================
        out.write("## Metrics\n")

        src = report_data.get("source_metrics", {})
        tx = report_data.get("transpiled_metrics", {})

        out.write("### Source Circuit\n")
        out.write(f"- Depth: {src.get('depth')}\n")
        out.write(f"- Size: {src.get('size')}\n")
        out.write(f"- Swaps: {src.get('swaps')}\n\n")

        out.write("### Transpiled Circuit\n")
        out.write(f"- Depth: {tx.get('depth')}\n")
        out.write(f"- Size: {tx.get('size')}\n")
        out.write(f"- Swaps: {tx.get('swaps')}\n\n")

        # =====================
        # Runtime Validation
        # =====================
        rv = report_data.get("runtime_validation", {})

        out.write("## Runtime Validation\n")

        tvd = rv.get("tvd")
        hell = rv.get("hellinger")
        fid = rv.get("fidelity")

        out.write(f"- TVD: {tvd}\n")
        out.write(f"- Hellinger: {hell}\n")
        out.write(f"- Fidelity: {fid}\n\n")

        # =====================
        # CIA Summary
        # =====================
        cia = report_data.get("cia_summary", {})
        out.write("## CIA Impact Summary\n")
        out.write(f"- Confidentiality: {cia.get('confidentiality')}\n")
        out.write(f"- Integrity: {cia.get('integrity')}\n")
        out.write(f"- Availability: {cia.get('availability')}\n")

    print(f"[OK] Markdown report saved to {output_md_path}")