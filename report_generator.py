#!/usr/bin/env python3

import json
import os
from typing import Any, Dict


def generate_report(report_data: Dict[str, Any], output_path: str) -> None:
    """
    Save one clean JSON report per circuit.
    """

    os.makedirs("reports", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print(f"[OK] Report saved to {output_path}")


def generate_markdown(report_data: Dict[str, Any], output_md_path: str) -> None:
    """
    Generate Markdown report (optional, per circuit).
    """

    with open(output_md_path, "w", encoding="utf-8") as out:
        # =====================
        # Title
        # =====================
        out.write("# Quantum Circuit Security Analysis Report\n\n")

        # =====================
        # Overall Status
        # =====================
        out.write("## Report Status\n")
        out.write(f"- Status: {report_data.get('status', 'unknown')}\n")

        errors = report_data.get("errors", [])
        if errors:
            out.write("- Errors:\n")
            for err in errors:
                out.write(f"  - {err}\n")
        else:
            out.write("- Errors: None\n")
        out.write("\n")

        # =====================
        # Execution Context
        # =====================
        ctx = report_data.get("execution_context", {})
        out.write("## Execution Context\n")
        out.write(f"- Backend: {ctx.get('backend')}\n")
        out.write(f"- Basis Gates: {', '.join(ctx.get('basis_gates', []))}\n")
        out.write(f"- Coupling Map: {ctx.get('coupling_map')}\n")
        out.write(f"- Optimization Level: {ctx.get('optimization_level')}\n")
        out.write(f"- Noise Model: {ctx.get('noise_model')}\n\n")

        # =====================
        # Findings
        # =====================
        out.write("## Findings\n")
        findings = report_data.get("findings", [])

        if not findings:
            out.write("No findings detected.\n\n")
        else:
            for f in findings:
                out.write(
                    f"### {f.get('rule_id', 'UNKNOWN')} — {f.get('title', 'Untitled')} ({f.get('severity', 'unknown')})\n"
                )
                out.write(f"{f.get('message', '')}\n\n")
                out.write(f"- Layer: {f.get('layer', 'circuit')}\n")

                impact = f.get("impact", {})
                out.write(f"- Confidentiality: {impact.get('confidentiality')}\n")
                out.write(f"- Integrity: {impact.get('integrity')}\n")
                out.write(f"- Availability: {impact.get('availability')}\n")

                evidence = f.get("evidence", {})
                if evidence:
                    if "vulnerability" in evidence:
                        out.write(f"- Vulnerability: {evidence.get('vulnerability')}\n")
                    if "security_risk" in evidence:
                        out.write(f"- Security Risk: {evidence.get('security_risk')}\n")
                    if "occurrences" in evidence:
                        out.write("\n- Evidence:\n")
                        for occ in evidence["occurrences"]:
                            out.write(f"  - {occ}\n")

                mitigation_priority = f.get("mitigation_priority")
                if mitigation_priority is not None:
                    out.write(f"\n- Mitigation Priority: {mitigation_priority}\n")

                mitigation = f.get("mitigation", [])
                if mitigation:
                    out.write("- Mitigations:\n")
                    for item in mitigation:
                        out.write(f"  - {item}\n")

                out.write("\n")

        # =====================
        # Metrics
        # =====================
        out.write("## Metrics\n")

        src = report_data.get("source_metrics", {}) or {}
        tx = report_data.get("transpiled_metrics", {}) or {}

        out.write("### Source Circuit\n")
        out.write(f"- Depth: {src.get('depth')}\n")
        out.write(f"- Size: {src.get('size')}\n")
        out.write(f"- Swaps: {src.get('swaps')}\n")
        out.write(f"- Number of Qubits: {src.get('num_qubits')}\n")
        out.write(f"- Number of Classical Bits: {src.get('num_clbits')}\n")
        out.write(f"- Two-Qubit Ops: {src.get('two_qubit_ops')}\n")
        out.write(f"- Measurements: {src.get('measurements')}\n")
        out.write(f"- Resets: {src.get('resets')}\n\n")

        out.write("### Transpiled Circuit\n")
        if tx:
            out.write(f"- Depth: {tx.get('depth')}\n")
            out.write(f"- Size: {tx.get('size')}\n")
            out.write(f"- Swaps: {tx.get('swaps')}\n")
            out.write(f"- Number of Qubits: {tx.get('num_qubits')}\n")
            out.write(f"- Number of Classical Bits: {tx.get('num_clbits')}\n")
            out.write(f"- Two-Qubit Ops: {tx.get('two_qubit_ops')}\n")
            out.write(f"- Measurements: {tx.get('measurements')}\n")
            out.write(f"- Resets: {tx.get('resets')}\n\n")
        else:
            out.write("Unavailable\n\n")

        # =====================
        # Runtime Validation
        # =====================
        rv = report_data.get("runtime_validation", {}) or {}

        out.write("## Runtime Validation\n")
        out.write(f"- Status: {rv.get('status')}\n")
        out.write(f"- TVD: {rv.get('tvd')}\n")
        out.write(f"- Hellinger: {rv.get('hellinger')}\n")
        out.write(f"- Fidelity: {rv.get('fidelity')}\n")
        out.write(f"- Error: {rv.get('error')}\n\n")

        # =====================
        # CIA Summary
        # =====================
        cia = report_data.get("cia_summary", {}) or {}
        out.write("## CIA Impact Summary\n")
        out.write(f"- Confidentiality: {cia.get('confidentiality')}\n")
        out.write(f"- Integrity: {cia.get('integrity')}\n")
        out.write(f"- Availability: {cia.get('availability')}\n\n")

        # =====================
        # Mitigation Summary
        # =====================
        ms = report_data.get("mitigation_summary", {}) or {}
        out.write("## Mitigation Summary\n")

        high = ms.get("high_priority", [])
        medium = ms.get("medium_priority", [])
        low = ms.get("low_priority", [])

        out.write("### High Priority\n")
        if high:
            for item in high:
                out.write(f"- {item}\n")
        else:
            out.write("- None\n")

        out.write("\n### Medium Priority\n")
        if medium:
            for item in medium:
                out.write(f"- {item}\n")
        else:
            out.write("- None\n")

        out.write("\n### Low Priority\n")
        if low:
            for item in low:
                out.write(f"- {item}\n")
        else:
            out.write("- None\n")

        out.write("\n")

    print(f"[OK] Markdown report saved to {output_md_path}")