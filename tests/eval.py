"""
eval.py
-------
Runs simulator questions through the agent and reports pass/fail.

Usage (from project root, with venv active):

    # Run a specific simulator:
    python tests/eval.py idealGasLaw
    python tests/eval.py RadioactiveDecay
    python tests/eval.py SeperableDiffEqs
    python tests/eval.py HeatConduction
    python tests/eval.py NeutronDiffusion

    # Run all simulators:
    python tests/eval.py

    # See available simulators:
    python tests/eval.py --list

Each question gets its own transcript saved to transcripts/<simulator>_Q<n>.jsonl
Read them with: python tests/transcript_reader.py --list
"""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass

import numpy as np

# Add project root to path so simulators can be imported
sys.path.insert(0, ".")

from simulators.idealGasLaw.idealGasLaw import sampleQuestions as IDEAL_GAS_QUESTIONS
from simulators.RadioactiveDecay.RadioactiveDecay import sampleQuestions as RADIOACTIVE_QUESTIONS
from simulators.SeperableDiffEqs.SeperableDiffEqs import sampleQuestions as ODE_QUESTIONS
from simulators.HeatConduction.HeatConduction import sampleQuestions as HEAT_QUESTIONS
from simulators.NeutronDiffusion.NeutronDiffusion import sampleQuestions as NEUTRON_QUESTIONS


# --- Tolerances per simulator ---
# All set to 1% — consistent with Roy et al. (2026) which considers
# neural operator surrogates production-ready at ~1.5% relative L2 error.
# Since our simulators have exact analytical solutions, 1% accounts only
# for floating point rounding and agent response formatting.
TOLERANCES = {
    "idealGasLaw":      0.01,
    "RadioactiveDecay": 0.01,
    "SeperableDiffEqs": 0.01,
    "HeatConduction":   0.01,
    "NeutronDiffusion": 0.01,
}

ALL_SIMULATORS = [
    ("idealGasLaw",       IDEAL_GAS_QUESTIONS),
    ("RadioactiveDecay",  RADIOACTIVE_QUESTIONS),
    ("SeperableDiffEqs",  ODE_QUESTIONS),
    ("HeatConduction",    HEAT_QUESTIONS),
    ("NeutronDiffusion",  NEUTRON_QUESTIONS),
]


# Sentinel values to distinguish failure modes
TIMEOUT  = "TIMEOUT"
NONZERO  = "NONZERO_EXIT"


@dataclass
class Result:
    simulator:    str
    question_num: int
    question:     str
    ground_truth: float
    agent_answer: float | None
    passed:       bool
    tolerance:    float
    elapsed:      float
    failure_mode: str | None = None   # None, "wrong_answer", "parse_error",
                                      # "timeout", "nonzero_exit"
    raw_output:   str | None = None   # what the agent actually said (for debugging)
    error_msg:    str | None = None


def call_agent(question: str, transcript_path: str | None = None) -> str | None:
    """
    Call the agent in eval mode and return its raw stdout output.
    Returns TIMEOUT or NONZERO sentinel strings on those failure modes.
    Returns None only on unexpected exceptions.
    """
    cmd = [sys.executable, "-m", "adversarial_agent.main", "--eval", question]
    if transcript_path:
        cmd.append(transcript_path)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,   # 5 minutes — neutron diffusion can take ~100s
        )
        if result.returncode != 0:
            return NONZERO
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return TIMEOUT
    except Exception as exc:
        return None


def parse_answer(raw: str | None) -> float | None:
    """
    Parse the agent's stdout into a float.
    The agent outputs just a number like '243.6' or '1.353e12'.
    Returns None if parsing fails — caller should check raw_output to debug.
    """
    if raw is None or raw in (TIMEOUT, NONZERO):
        return None
    try:
        return float(raw.strip())
    except ValueError:
        return None


def check_tolerance(agent_answer: float, ground_truth: float, tolerance: float) -> bool:
    """
    Check if agent_answer is within tolerance fraction of ground_truth.
    Uses numpy isclose: abs(a-b) <= atol + rtol * abs(b)
    atol=1e-8 handles near-zero ground truths safely.
    """
    return bool(np.isclose(agent_answer, ground_truth, rtol=tolerance, atol=1e-8))


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

            # Each question gets its own transcript file
            transcript_path = f"transcripts/{simulator_name}_Q{i}.jsonl"

            start = time.time()
            raw_output = call_agent(question, transcript_path)
            elapsed = time.time() - start

            agent_answer = parse_answer(raw_output)

            # --- Determine failure mode ---
            failure_mode = None
            error_msg = None

            if raw_output == TIMEOUT:
                passed = False
                failure_mode = "timeout"
                error_msg = f"Agent exceeded 300s time limit"
                print(f"     ⏰ TIMEOUT — agent exceeded 300s  ({elapsed:.1f}s)")
                print(f"     📄 Transcript: {transcript_path}")

            elif raw_output == NONZERO:
                passed = False
                failure_mode = "nonzero_exit"
                error_msg = "Agent process exited with non-zero return code"
                print(f"     💥 CRASH — agent exited with error  ({elapsed:.1f}s)")
                print(f"     📄 Transcript: {transcript_path}")

            elif agent_answer is None:
                passed = False
                failure_mode = "parse_error"
                error_msg = f"Could not parse as float: {repr(raw_output)}"
                # Show what the agent actually said so you can debug
                print(f"     ⚠️  PARSE ERROR — agent said: {repr(raw_output)}")
                print(f"     (Did the agent forget to write 'ANSWER: <number>'?)")
                print(f"     ({elapsed:.1f}s)")
                print(f"     📄 Transcript: {transcript_path}")

            else:
                passed = check_tolerance(agent_answer, ground_truth, tolerance)
                if passed:
                    failure_mode = None
                else:
                    failure_mode = "wrong_answer"
                    error_msg = f"Answer outside {tolerance*100:.0f}% tolerance"

                relative_error = (
                    abs(agent_answer - ground_truth) / abs(ground_truth)
                    if abs(ground_truth) > 1e-10 else 0
                )
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"     Agent answer: {agent_answer:.6g}  "
                      f"(error: {relative_error*100:.2f}%)  {status}  ({elapsed:.1f}s)")
                if not passed:
                    print(f"     📄 Transcript: {transcript_path}")

            results.append(Result(
                simulator=simulator_name,
                question_num=i,
                question=question,
                ground_truth=ground_truth,
                agent_answer=agent_answer,
                passed=passed,
                tolerance=tolerance,
                elapsed=elapsed,
                failure_mode=failure_mode,
                raw_output=raw_output,
                error_msg=error_msg,
            ))

    return results


def print_summary(results: list[Result], simulators: list) -> None:
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for simulator_name, _ in simulators:
        sim_results = [r for r in results if r.simulator == simulator_name]
        passed = sum(1 for r in sim_results if r.passed)
        total = len(sim_results)
        avg_time = sum(r.elapsed for r in sim_results) / total if total else 0
        bar = "█" * passed + "░" * (total - passed)
        print(f"  {simulator_name:<20} {bar}  {passed}/{total}  avg {avg_time:.0f}s/q")

    total_passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n  TOTAL: {total_passed}/{total} passed ({total_passed/total*100:.0f}%)")

    failures = [r for r in results if not r.passed]
    if failures:
        print(f"\nFAILURES:")
        for r in failures:
            mode_label = {
                "wrong_answer":  "❌ Wrong answer",
                "parse_error":   "⚠️  Parse error",
                "timeout":       "⏰ Timeout",
                "nonzero_exit":  "💥 Crash",
            }.get(r.failure_mode, "❌ Unknown")

            print(f"\n  [{r.simulator}] Q{r.question_num}  —  {mode_label}  ({r.elapsed:.1f}s)")
            print(f"    Ground truth:  {r.ground_truth:.6g}")
            print(f"    Agent answer:  {r.agent_answer}")

            if r.failure_mode == "parse_error":
                print(f"    Agent said:    {repr(r.raw_output)}")

            if r.error_msg:
                print(f"    Detail:        {r.error_msg}")

            print(f"    Transcript:    transcripts/{r.simulator}_Q{r.question_num}.jsonl")
    else:
        print("\n  All questions passed! 🎉")

    # Slowest questions
    slowest = sorted(results, key=lambda r: r.elapsed, reverse=True)[:3]
    print(f"\nSLOWEST QUESTIONS:")
    for r in slowest:
        print(f"  [{r.simulator}] Q{r.question_num}: {r.elapsed:.1f}s")
        print(f"    → python tests/transcript_reader.py "
              f"transcripts/{r.simulator}_Q{r.question_num}.jsonl")


if __name__ == "__main__":
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
            sys.exit(1)
        simulators_to_run = [(name, q) for name, q in ALL_SIMULATORS if name == chosen]
    else:
        simulators_to_run = ALL_SIMULATORS

    total_q = sum(len(q) for _, q in simulators_to_run)
    print("CMU Project — Simulator Eval")
    print(f"Running {total_q} question(s) across {len(simulators_to_run)} simulator(s)\n")

    results = run_all_evals(simulators_to_run)
    print_summary(results, simulators_to_run)