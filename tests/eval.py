"""
eval.py
-------
Runs simulator questions through the agent and reports pass/fail.

Usage (from project root, with venv active):

    # Run a specific simulator:
    python tests/eval.py ideal_gas
    python tests/eval.py radioactive_decay
    python tests/eval.py separable_ode
    python tests/eval.py heat_conduction
    python tests/eval.py neutron_diffusion

    # Run all simulators:
    python tests/eval.py

    # See available simulators:
    python tests/eval.py --list
"""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass

# --- Import all simulators ---
# Add src/ to path so we can import the simulators
sys.path.insert(0, "src")

from simulators.idealGasLaw.idealGasLaw import sampleQuestions as IDEAL_GAS_QUESTIONS
from simulators.RadioactiveDecay.RadioactiveDecay import sampleQuestions as RADIOACTIVE_QUESTIONS
from simulators.SeperableDiffEqs.SeperableDiffEqs import sampleQuestions as ODE_QUESTIONS
from simulators.HeatConduction.HeatConduction import sampleQuestions as HEAT_QUESTIONS
from simulators.NeutronDiffusion.NeutronDiffusion import sampleQuestions as NEUTRON_QUESTIONS


# --- Tolerances per simulator ---
# How close does the agent's answer need to be (as a fraction of ground truth)?
# e.g. 0.01 = within 1%
TOLERANCES = {
    "idealGasLaw":        0.01,   # algebra, exact — 1%
    "RadioactiveDecay":   0.01,   # exponential, exact — 1%
    "SeperableDiffEqs":   0.01,   # calculus, slight rounding — 2%
    "HeatConduction":     0.01,   # ODE, slight rounding — 2%
    "NeutronDiffusion":   0.01,   # sinh of large numbers, more rounding — 5%
}


# --- All simulators bundled together ---
ALL_SIMULATORS = [
    ("idealGasLaw",       IDEAL_GAS_QUESTIONS),
    ("RadioactiveDecay",  RADIOACTIVE_QUESTIONS),
    ("SeperableDiffEqs",  ODE_QUESTIONS),
    ("HeatConduction",    HEAT_QUESTIONS),
    ("NeutronDiffusion",  NEUTRON_QUESTIONS),
]


@dataclass
class Result:
    simulator:   str
    question_num: int
    question:    str
    ground_truth: float
    agent_answer: float | None
    passed:      bool
    tolerance:   float
    error_msg:   str | None = None


def call_agent(question: str) -> str | None:
    """
    Call the agent in eval mode and return its raw stdout output.
    Returns None if the subprocess fails.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "cmu_project.main", "--eval", question],
            capture_output=True,
            text=True,
            timeout=120,   # 2 min max per question
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def parse_answer(raw: str | None) -> float | None:
    """
    Parse the agent's stdout into a float.
    The agent should output just a number like '243.6'.
    Returns None if parsing fails.
    """
    if raw is None:
        return None
    try:
        return float(raw.strip())
    except ValueError:
        return None


def check_tolerance(agent_answer: float, ground_truth: float, tolerance: float) -> bool:
    """
    Check if agent_answer is within `tolerance` fraction of ground_truth.
    e.g. tolerance=0.01 means within 1%.

    Handles the case where ground_truth is very close to zero.
    """
    if abs(ground_truth) < 1e-10:
        # ground truth is basically zero — use absolute tolerance
        return abs(agent_answer - ground_truth) < 1e-6
    relative_error = abs(agent_answer - ground_truth) / abs(ground_truth)
    return relative_error <= tolerance


def run_all_evals(simulators: list) -> list[Result]:
    results = []

    for simulator_name, questions in simulators:
        tolerance = TOLERANCES[simulator_name]
        print(f"\n{'='*60}")
        print(f"SIMULATOR: {simulator_name.upper()}  (tolerance: {tolerance*100:.0f}%)")
        print(f"{'='*60}")

        for i, sample in enumerate(questions, 1):
            question = sample["question"]
            ground_truth = sample["answer"]

            print(f"\nQ{i}: {question[:80]}...")
            print(f"     Ground truth: {ground_truth:.6g}")

            # Call agent
            start = time.time()
            raw_output = call_agent(question)
            elapsed = time.time() - start

            # Parse answer
            agent_answer = parse_answer(raw_output)

            # Check pass/fail
            if agent_answer is None:
                passed = False
                error_msg = f"Could not parse output: {repr(raw_output)}"
                print(f"     Agent output: {repr(raw_output)}")
                print(f"     ❌ FAIL — could not parse answer ({elapsed:.1f}s)")
            else:
                passed = check_tolerance(agent_answer, ground_truth, tolerance)
                error_msg = None
                relative_error = abs(agent_answer - ground_truth) / abs(ground_truth) if abs(ground_truth) > 1e-10 else 0
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"     Agent answer: {agent_answer:.6g}  (error: {relative_error*100:.2f}%)  {status}  ({elapsed:.1f}s)")

            results.append(Result(
                simulator=simulator_name,
                question_num=i,
                question=question,
                ground_truth=ground_truth,
                agent_answer=agent_answer,
                passed=passed,
                tolerance=tolerance,
                error_msg=error_msg,
            ))

    return results


def print_summary(results: list[Result], simulators: list) -> None:
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    # Per-simulator breakdown
    for simulator_name, _ in simulators:
        sim_results = [r for r in results if r.simulator == simulator_name]
        passed = sum(1 for r in sim_results if r.passed)
        total = len(sim_results)
        bar = "█" * passed + "░" * (total - passed)
        print(f"  {simulator_name:<20} {bar}  {passed}/{total}")

    # Overall
    total_passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n  TOTAL: {total_passed}/{total} passed ({total_passed/total*100:.0f}%)")

    # List all failures
    failures = [r for r in results if not r.passed]
    if failures:
        print(f"\nFAILURES:")
        for r in failures:
            print(f"  [{r.simulator}] Q{r.question_num}")
            print(f"    Ground truth:  {r.ground_truth:.6g}")
            print(f"    Agent answer:  {r.agent_answer}")
            if r.error_msg:
                print(f"    Error: {r.error_msg}")
    else:
        print("\n  All questions passed! 🎉")


if __name__ == "__main__":
    # --- Handle command line argument ---
    VALID_NAMES = [name for name, _ in ALL_SIMULATORS]

    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print("Available simulators:")
        for name in VALID_NAMES:
            print(f"  {name}")
        sys.exit(0)

    if len(sys.argv) == 2:
        chosen = sys.argv[1]
        if chosen not in VALID_NAMES:
            print(f"Unknown simulator '{chosen}'.")
            print(f"Available: {', '.join(VALID_NAMES)}")
            print(f"Run all:   python tests/eval.py")
            sys.exit(1)
        # Run just the chosen simulator
        simulators_to_run = [(name, q) for name, q in ALL_SIMULATORS if name == chosen]
    else:
        # No argument — run all
        simulators_to_run = ALL_SIMULATORS

    total_q = sum(len(q) for _, q in simulators_to_run)
    print("CMU Project — Simulator Eval")
    print(f"Running {total_q} question(s) across {len(simulators_to_run)} simulator(s)\n")

    results = run_all_evals(simulators_to_run)
    print_summary(results, simulators_to_run)