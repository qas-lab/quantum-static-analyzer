#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import math
import os
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error


# =========================
# DATA MODELS
# =========================

@dataclass
class Finding:
    rule_id: str
    title: str
    severity: str
    message: str
    impact: Dict[str, bool] = field(default_factory=dict)
    layer: str = "circuit"
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    backend: Optional[str]
    basis_gates: List[str]
    coupling_map: Optional[List[List[int]]]
    optimization_level: int
    noise_model: Optional[str]


@dataclass
class StructuralMetrics:
    depth: int
    size: int
    swaps: int
    num_qubits: int
    num_clbits: int
    two_qubit_ops: int
    measurements: int
    resets: int


@dataclass
class RuntimeValidation:
    tvd: Optional[float]
    hellinger: Optional[float]
    fidelity: Optional[float]
    status: str
    error: Optional[str] = None


@dataclass
class AnalysisReport:
    execution_context: ExecutionContext
    findings: List[Finding]
    source_metrics: StructuralMetrics
    transpiled_metrics: Optional[StructuralMetrics]
    runtime_validation: RuntimeValidation
    cia_summary: Dict[str, bool]
    status: str = "ok"
    errors: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(
            {
                "status": self.status,
                "errors": self.errors,
                "execution_context": asdict(self.execution_context),
                "findings": [asdict(f) for f in self.findings],
                "source_metrics": asdict(self.source_metrics),
                "transpiled_metrics": (
                    asdict(self.transpiled_metrics) if self.transpiled_metrics else None
                ),
                "runtime_validation": asdict(self.runtime_validation),
                "cia_summary": self.cia_summary,
            },
            indent=2,
        )


# =========================
# HELPERS
# =========================

def parse_coupling(spec: Optional[str]) -> Optional[List[List[int]]]:
    if not spec:
        return None

    pairs: List[List[int]] = []
    for raw in spec.split(","):
        raw = raw.strip()
        if not raw:
            continue
        if "-" not in raw:
            raise ValueError(f"Invalid coupling pair: {raw!r}")
        a, b = raw.split("-", 1)
        pairs.append([int(a), int(b)])
    return pairs or None


def normalize_counts(counts: Dict[str, int]) -> Dict[str, float]:
    total = sum(counts.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in counts.items()}


def align_distributions(
    p: Dict[str, float], q: Dict[str, float]
) -> Tuple[Dict[str, float], Dict[str, float]]:
    keys = set(p.keys()) | set(q.keys())
    return (
        {k: p.get(k, 0.0) for k in keys},
        {k: q.get(k, 0.0) for k in keys},
    )


def distribution_fidelity(p: Dict[str, float], q: Dict[str, float]) -> float:
    return sum(math.sqrt(p[k] * q[k]) for k in p) ** 2


def aggregate_findings(findings: List[Finding]) -> List[Finding]:
    grouped: Dict[Tuple[str, str, str, str, str], Dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "impact": {
                "confidentiality": False,
                "integrity": False,
                "availability": False,
            },
            "evidence": [],
        }
    )

    for f in findings:
        key = (f.rule_id, f.title, f.severity, f.message, f.layer)
        grouped[key]["count"] += 1
        grouped[key]["evidence"].append(f.evidence)

        for k in ["confidentiality", "integrity", "availability"]:
            grouped[key]["impact"][k] |= f.impact.get(k, False)

    out: List[Finding] = []
    for (rule_id, title, severity, message, layer), data in grouped.items():
        count = data["count"]
        out.append(
            Finding(
                rule_id=rule_id,
                title=f"{title} (n={count})" if count > 1 else title,
                severity=severity,
                message=message,
                impact=data["impact"],
                layer=layer,
                evidence={"occurrences": data["evidence"]},
            )
        )
    return out


def safe_read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        return ""


def safe_ast_parse(source_code: str) -> Optional[ast.AST]:
    if not source_code.strip():
        return None
    try:
        return ast.parse(source_code)
    except Exception:
        return None


def add_finding(
    findings: List[Finding],
    rule_id: str,
    title: str,
    severity: str,
    message: str,
    impact: Dict[str, bool],
    layer: str = "circuit",
    evidence: Optional[Dict[str, Any]] = None,
) -> None:
    findings.append(
        Finding(
            rule_id=rule_id,
            title=title,
            severity=severity,
            message=message,
            impact=impact,
            layer=layer,
            evidence=evidence or {},
        )
    )


# =========================
# LOAD CIRCUIT
# =========================

def load_circuit(path: str) -> Tuple[QuantumCircuit, str]:
    if path.endswith(".qasm"):
        try:
            return QuantumCircuit.from_qasm_file(path), ""
        except Exception as e:
            raise ValueError(f"Failed to load QASM file {path}: {e}") from e

    if path.endswith(".py"):
        source_code = safe_read_text(path)

        spec = importlib.util.spec_from_file_location("loaded_circuit_module", path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not create import spec for {path}")

        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            raise ValueError(f"Failed to import Python circuit file {path}: {e}") from e

        try:
            if hasattr(mod, "build_circuit"):
                circ = mod.build_circuit()
            elif hasattr(mod, "qc"):
                circ = mod.qc
            else:
                raise ValueError("Python file must define build_circuit() or qc")
        except Exception as e:
            raise ValueError(f"Failed while building circuit from {path}: {e}") from e

        if not isinstance(circ, QuantumCircuit):
            raise ValueError(f"Loaded object from {path} is not a QuantumCircuit")

        return circ, source_code

    raise ValueError("Unsupported file type; expected .py or .qasm")


# =========================
# METRICS
# =========================

def metrics(circ: QuantumCircuit) -> StructuralMetrics:
    counts = circ.count_ops()
    two_qubit_ops = 0
    measurements = 0
    resets = 0

    for instr in circ.data:
        op = instr.operation
        if op.num_qubits == 2:
            two_qubit_ops += 1
        if op.name == "measure":
            measurements += 1
        elif op.name == "reset":
            resets += 1

    return StructuralMetrics(
        depth=int(circ.depth() or 0),
        size=int(circ.size() or 0),
        swaps=int(counts.get("swap", 0)),
        num_qubits=circ.num_qubits,
        num_clbits=circ.num_clbits,
        two_qubit_ops=two_qubit_ops,
        measurements=measurements,
        resets=resets,
    )


# =========================
# RULES: R1
# =========================

# =========================
# RULES: R1
# =========================

def rule_measurement_misuse(circ: QuantumCircuit) -> List[Finding]:
    findings: List[Finding] = []

    #  REMOVED suppression logic (reuse_events + measured_for_reuse)

    measured: set[int] = set()

    for i, instr in enumerate(circ.data):
        inst = instr.operation
        qubits = instr.qubits

        if inst.name == "measure":
            for qb in qubits:
                measured.add(circ.find_bit(qb).index)
            continue

        if inst.name == "reset":
            for qb in qubits:
                measured.discard(circ.find_bit(qb).index)
            continue

        for qb in qubits:
            idx = circ.find_bit(qb).index

            # ✅ FIX: allow R1 always (no suppression by R2)
            if idx in measured:
                print("R1 triggered at", i, "qubit", idx)
                add_finding(
                    findings,
                    "R1",
                    "Measurement misuse",
                    "high",
                    "Operation applied after measurement without reset",
                    {
                        "confidentiality": True,
                        "integrity": True,
                        "availability": False,
                    },
                    evidence={"index": i, "qubit": idx, "operation": inst.name},
                )

    return findings

def rule_classical_feedback(circ: QuantumCircuit) -> List[Finding]:
    findings: List[Finding] = []

    for i, instr in enumerate(circ.data):
        op = instr.operation
        condition = getattr(op, "condition", None)
        if condition is not None:
            add_finding(
                findings,
                "R1",
                "Classical feedback pattern",
                "medium",
                "Conditional operation detected; verify measurement ordering and reinitialization",
                {
                    "confidentiality": True,
                    "integrity": True,
                    "availability": False,
                },
                evidence={"index": i, "operation": op.name, "condition": str(condition)},
            )

    return findings


# =========================
# RULES: R2
# =========================

def rule_qubit_reuse(circ: QuantumCircuit) -> List[Finding]:
    findings: List[Finding] = []
    measured: Dict[int, int] = {}

    for i, instr in enumerate(circ.data):
        inst = instr.operation
        qubits = instr.qubits

        if inst.name == "measure":
            for qb in qubits:
                measured[circ.find_bit(qb).index] = i
            continue

        if inst.name == "reset":
            for qb in qubits:
                measured.pop(circ.find_bit(qb).index, None)
            continue

        for qb in qubits:
            idx = circ.find_bit(qb).index
            if idx in measured:
                add_finding(
                    findings,
                    "R2",
                    "Qubit reuse",
                    "high",
                    "Qubit reused after measurement without reset",
                    {
                        "confidentiality": True,
                        "integrity": True,
                        "availability": False,
                    },
                    evidence={
                        "measurement_index": measured[idx],
                        "reuse_index": i,
                        "qubit": idx,
                        "operation": inst.name,
                    },
                )

    return findings


# =========================
# RULES: R3
# =========================

def rule_swap_exposure(
    src: QuantumCircuit, tx: QuantumCircuit, ctx: ExecutionContext
) -> List[Finding]:
    findings: List[Finding] = []

    src_m = metrics(src)
    tx_m = metrics(tx)

    depth_growth = tx_m.depth / max(src_m.depth, 1)
    size_growth = tx_m.size / max(src_m.size, 1)

    if ctx.coupling_map is not None and (
        tx_m.swaps > src_m.swaps or
        depth_growth >= 1.5 or
        size_growth >= 2.0
    ):
        add_finding(
            findings,
            "R3",
            "Routing / compilation overhead",
            "medium",
            "Routing overhead detected (SWAPs or structural blow-up)",
            {
                "confidentiality": True,
                "integrity": False,
                "availability": True,
            },
            layer="compilation",
            evidence={
                "source_depth": src_m.depth,
                "transpiled_depth": tx_m.depth,
                "source_size": src_m.size,
                "transpiled_size": tx_m.size,
                "source_swaps": src_m.swaps,
                "transpiled_swaps": tx_m.swaps,
                "depth_growth": depth_growth,
                "size_growth": size_growth,
            },
        )

    return findings


# =========================
# RULES: R4
# =========================

def rule_sdk_fragility(source_code: str) -> List[Finding]:
    findings: List[Finding] = []
    if not source_code:
        return findings

    patterns = [
        (
            "execute(",
            "SDK fragility",
            "Use of legacy execute() API",
            {"confidentiality": False, "integrity": True, "availability": True},
        ),
        (
            "qiskit.opflow",
            "Deprecated module usage",
            "Use of deprecated qiskit.opflow module",
            {"confidentiality": False, "integrity": False, "availability": True},
        ),
        (
            "from qiskit import Aer",
            "Legacy Aer import",
            "Legacy Aer import style detected",
            {"confidentiality": False, "integrity": False, "availability": True},
        ),
        (
            "assemble(",
            "Legacy Qobj workflow",
            "Use of assemble()/qobj-era execution flow",
            {"confidentiality": False, "integrity": True, "availability": True},
        ),
        (
            "qiskit.providers.ibmq",
            "Legacy IBMQ provider",
            "Legacy qiskit.providers.ibmq import detected",
            {"confidentiality": False, "integrity": False, "availability": True},
        ),
        (
            "IBMQ.load_account(",
            "Legacy IBMQ account flow",
            "Legacy IBMQ account-loading pattern detected",
            {"confidentiality": False, "integrity": False, "availability": True},
        ),
        (
            "provider.get_backend(",
            "Backend binding fragility",
            "Version-sensitive direct backend selection pattern detected",
            {"confidentiality": False, "integrity": True, "availability": True},
        ),
    ]

    for token, title, message, impact in patterns:
        if token in source_code:
            add_finding(
                findings,
                "R4",
                title,
                "medium",
                message,
                impact,
                layer="hybrid",
                evidence={"token": token},
            )

    return findings


# =========================
# RULES: R5
# =========================

SELF_INVERSE_GATES = {"x", "y", "z", "h", "cx", "cy", "cz", "swap"}

def rule_redundant_gates(circ: QuantumCircuit) -> List[Finding]:
    findings: List[Finding] = []

    for i in range(len(circ.data) - 1):
        a = circ.data[i]
        b = circ.data[i + 1]

        same_qubits = a.qubits == b.qubits
        same_clbits = a.clbits == b.clbits
        same_name = a.operation.name == b.operation.name

        if same_name and same_qubits and same_clbits and a.operation.name in SELF_INVERSE_GATES:
            add_finding(
                findings,
                "R5",
                "Redundant gates",
                "medium",
                "Adjacent self-inverse gates cancel logically",
                {
                    "confidentiality": False,
                    "integrity": True,
                    "availability": True,
                },
                evidence={
                    "first_index": i,
                    "second_index": i + 1,
                    "operation": a.operation.name,
                },
            )

    return findings


def rule_dead_or_ineffective_patterns(circ: QuantumCircuit) -> List[Finding]:
    findings: List[Finding] = []

    for i in range(len(circ.data) - 3):
        ops = circ.data[i:i + 4]
        names = [x.operation.name for x in ops]
        qubits = [tuple(circ.find_bit(q).index for q in x.qubits) for x in ops]

        if names == ["cx", "cx", "cx", "cx"] and len(set(qubits)) <= 2:
            add_finding(
                findings,
                "R5",
                "Oscillating gate pattern",
                "medium",
                "Repeated two-qubit toggling pattern suggests low-value or anomalous logic",
                {
                    "confidentiality": False,
                    "integrity": True,
                    "availability": True,
                },
                evidence={"start_index": i, "pattern": names, "qubits": qubits},
            )

    return findings


def rule_register_conflict(circ: QuantumCircuit) -> List[Finding]:
    findings: List[Finding] = []
    clbit_last_write: Dict[int, int] = {}

    for i, instr in enumerate(circ.data):
        if instr.operation.name != "measure":
            continue

        for clb in instr.clbits:
            cidx = circ.find_bit(clb).index
            if cidx in clbit_last_write:
                add_finding(
                    findings,
                    "R5",
                    "Classical register overwrite",
                    "medium",
                    "Multiple measurements write to the same classical bit",
                    {
                        "confidentiality": False,
                        "integrity": True,
                        "availability": False,
                    },
                    evidence={
                        "clbit": cidx,
                        "previous_measure_index": clbit_last_write[cidx],
                        "current_measure_index": i,
                    },
                )
            clbit_last_write[cidx] = i

    return findings


def rule_over_entangle(circ: QuantumCircuit) -> List[Finding]:
    findings: List[Finding] = []

    twoq_pairs: List[Tuple[int, ...]] = []
    for instr in circ.data:
        if instr.operation.num_qubits == 2:
            pair = tuple(sorted(circ.find_bit(q).index for q in instr.qubits))
            twoq_pairs.append(pair)

    if circ.num_qubits >= 4 and len(twoq_pairs) >= max(4, circ.num_qubits + 1):
        unique_pairs = len(set(twoq_pairs))
        if unique_pairs >= circ.num_qubits:
            add_finding(
                findings,
                "R5",
                "Over-entanglement pattern",
                "medium",
                "Dense two-qubit connectivity may indicate anomalous or excessive entanglement",
                {
                    "confidentiality": False,
                    "integrity": True,
                    "availability": True,
                },
                evidence={
                    "num_qubits": circ.num_qubits,
                    "two_qubit_ops": len(twoq_pairs),
                    "unique_pairs": unique_pairs,
                },
            )

    return findings


def rule_fake_api_pattern(source_code: str, tree: Optional[ast.AST]) -> List[Finding]:
    findings: List[Finding] = []
    if not source_code:
        return findings

    suspicious_tokens = [
        ".run_circuit(",
        ".simulate_counts(",
        ".apply_noise_profile(",
        ".fake_backend(",
        ".quantum_execute(",
    ]

    for token in suspicious_tokens:
        if token in source_code:
            add_finding(
                findings,
                "R5",
                "Suspicious API pattern",
                "medium",
                "Potential hallucinated or non-standard API pattern detected",
                {
                    "confidentiality": False,
                    "integrity": True,
                    "availability": True,
                },
                layer="hybrid",
                evidence={"token": token},
            )

    if tree is not None:
        qiskit_method_allowlist = {
            "h", "x", "y", "z", "s", "sdg", "t", "tdg",
            "rx", "ry", "rz", "p", "u", "cx", "cy", "cz",
            "swap", "cp", "crx", "cry", "crz", "ccx",
            "measure", "measure_all", "reset", "barrier",
            "append", "compose", "copy",
            "draw", "depth", "size", "count_ops",
            "if_test",
        }

        class MethodVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.bad_calls: List[Tuple[int, str]] = []

            def visit_Call(self, node: ast.Call) -> None:
                if isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                    if name.startswith("fake_") or name.startswith("unsafe_"):
                        self.bad_calls.append((node.lineno, name))
                    elif (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "qc"
                        and name not in qiskit_method_allowlist
                    ):
                        if name not in {"c_if"}:
                            self.bad_calls.append((node.lineno, name))
                self.generic_visit(node)

        visitor = MethodVisitor()
        visitor.visit(tree)

        for lineno, name in visitor.bad_calls:
            add_finding(
                findings,
                "R5",
                "Suspicious method call",
                "medium",
                "Potential hallucinated or version-sensitive circuit method detected",
                {
                    "confidentiality": False,
                    "integrity": True,
                    "availability": True,
                },
                layer="hybrid",
                evidence={"line": lineno, "method": name},
            )

    return findings


# =========================
# NOISE + VALIDATION
# =========================

def build_noise(level: Optional[str]) -> Optional[NoiseModel]:
    if level in (None, "none"):
        return None

    if level not in {"light", "heavy"}:
        raise ValueError(f"Unsupported noise model: {level!r}")

    nm = NoiseModel()
    p = 0.01 if level == "light" else 0.05

    nm.add_all_qubit_quantum_error(depolarizing_error(p, 1), ["x", "sx", "rz"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p * 2, 2), ["cx"])
    nm.add_all_qubit_readout_error(ReadoutError([[0.98, 0.02], [0.02, 0.98]]))
    return nm


def ensure_measurements(circ: QuantumCircuit) -> QuantumCircuit:
    has_measurement = any(instr.operation.name == "measure" for instr in circ.data)
    out = circ.copy()
    if not has_measurement:
        out.measure_all()
    return out


def run_validation(tx: Optional[QuantumCircuit], ctx: ExecutionContext) -> RuntimeValidation:
    if tx is None:
        return RuntimeValidation(
            tvd=None,
            hellinger=None,
            fidelity=None,
            status="skipped",
            error="Validation skipped because transpilation failed",
        )

    try:
        tx_meas = ensure_measurements(tx)

        ideal_sim = AerSimulator()
        ideal_counts = ideal_sim.run(tx_meas, shots=1024).result().get_counts()

        noise_model = build_noise(ctx.noise_model)
        noisy_sim = AerSimulator(noise_model=noise_model)
        noisy_counts = noisy_sim.run(tx_meas, shots=1024).result().get_counts()

        p = normalize_counts(ideal_counts)
        q = normalize_counts(noisy_counts)
        p, q = align_distributions(p, q)

        tvd = 0.5 * sum(abs(p[k] - q[k]) for k in p)
        hell = math.sqrt(sum((math.sqrt(p[k]) - math.sqrt(q[k])) ** 2 for k in p)) / math.sqrt(2)
        fid = distribution_fidelity(p, q)

        return RuntimeValidation(
            tvd=tvd,
            hellinger=hell,
            fidelity=fid,
            status="ok",
        )
    except Exception as e:
        return RuntimeValidation(
            tvd=None,
            hellinger=None,
            fidelity=None,
            status="error",
            error=str(e),
        )


# =========================
# MAIN ANALYSIS
# =========================

def analyze(path: str, args) -> AnalysisReport:
    findings: List[Finding] = []
    errors: List[str] = []

    source_code = safe_read_text(path) if path.endswith(".py") else ""
    tree = safe_ast_parse(source_code)

    ctx = ExecutionContext(
        backend=args.fake_backend,
        basis_gates=(
            [g.strip() for g in args.basis_gates.split(",") if g.strip()]
            if args.basis_gates
            else ["rz", "sx", "x", "cx"]
        ),
        coupling_map=parse_coupling(args.coupling_map),
        optimization_level=args.optimization_level,
        noise_model=args.noise_model,
    )

    try:
        circ, loaded_source = load_circuit(path)
        if loaded_source:
            source_code = loaded_source
            tree = safe_ast_parse(source_code)
    except Exception as e:
        errors.append(str(e))
        dummy = QuantumCircuit(1, 1)
        initial_findings = rule_sdk_fragility(source_code) + rule_fake_api_pattern(source_code, tree)
        return AnalysisReport(
            execution_context=ctx,
            findings=aggregate_findings(initial_findings),
            source_metrics=metrics(dummy),
            transpiled_metrics=None,
            runtime_validation=RuntimeValidation(
                tvd=None,
                hellinger=None,
                fidelity=None,
                status="skipped",
                error="Circuit could not be loaded",
            ),
            cia_summary={
                "confidentiality": any(f.impact.get("confidentiality", False) for f in initial_findings),
                "integrity": any(f.impact.get("integrity", False) for f in initial_findings),
                "availability": True,
            },
            status="error",
            errors=errors,
        )

    findings += rule_measurement_misuse(circ)
    findings += rule_classical_feedback(circ)
    findings += rule_qubit_reuse(circ)
    findings += rule_redundant_gates(circ)
    findings += rule_dead_or_ineffective_patterns(circ)
    findings += rule_register_conflict(circ)
    findings += rule_over_entangle(circ)
    findings += rule_sdk_fragility(source_code)
    findings += rule_fake_api_pattern(source_code, tree)

    tx: Optional[QuantumCircuit] = None
    try:
        tx = transpile(
            circ,
            basis_gates=ctx.basis_gates,
            coupling_map=ctx.coupling_map,
            optimization_level=ctx.optimization_level,
        )
        findings += rule_swap_exposure(circ, tx, ctx)
    except Exception as e:
        errors.append(f"Transpile failed: {e}")
        add_finding(
            findings,
            "R3",
            "Compilation failure",
            "high",
            "Circuit could not be transpiled under the provided execution context",
            {
                "confidentiality": False,
                "integrity": True,
                "availability": True,
            },
            layer="compilation",
            evidence={
                "basis_gates": ctx.basis_gates,
                "coupling_map": ctx.coupling_map,
                "optimization_level": ctx.optimization_level,
                "error": str(e),
            },
        )

    validation = run_validation(tx, ctx)

    if validation.status == "ok" and validation.tvd is not None and validation.tvd > 0.1:
        add_finding(
            findings,
            "RV1",
            "Noise-induced divergence",
            "medium",
            "Execution context alters output distribution",
            {
                "confidentiality": False,
                "integrity": True,
                "availability": True,
            },
            layer="hardware",
            evidence={
                "tvd": validation.tvd,
                "hellinger": validation.hellinger,
                "fidelity": validation.fidelity,
            },
        )
    elif validation.status == "error":
        errors.append(f"Validation failed: {validation.error}")
        add_finding(
            findings,
            "RV0",
            "Validation execution issue",
            "low",
            "Runtime validation could not be completed",
            {
                "confidentiality": False,
                "integrity": False,
                "availability": True,
            },
            layer="hardware",
            evidence={"error": validation.error},
        )

    findings = aggregate_findings(findings)

    cia_summary = {
        "confidentiality": False,
        "integrity": False,
        "availability": False,
    }
    for f in findings:
        for k in cia_summary:
            if f.impact.get(k, False):
                cia_summary[k] = True

    return AnalysisReport(
        execution_context=ctx,
        findings=findings,
        source_metrics=metrics(circ),
        transpiled_metrics=metrics(tx) if tx is not None else None,
        runtime_validation=validation,
        cia_summary=cia_summary,
        status="ok" if not errors else "partial",
        errors=errors,
    )


# =========================
# CLI
# =========================

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--basis-gates")
    parser.add_argument("--coupling-map")
    parser.add_argument("--optimization-level", type=int, default=1)
    parser.add_argument("--fake-backend")
    parser.add_argument("--noise-model", default="light", choices=["none", "light", "heavy"])

    args = parser.parse_args()

    report = analyze(args.input, args)
    report_json = report.to_json()

    print(report_json)

    #  FIXED: everything BELOW must be inside main()
    os.makedirs("reports", exist_ok=True)

    # extract circuit name from input path
    circuit_name = os.path.splitext(os.path.basename(args.input))[0]

    output_path = f"reports/{circuit_name}.json"

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(report_json)

    print(f"\n[OK] Report saved to {output_path}")


if __name__ == "__main__":
    main()