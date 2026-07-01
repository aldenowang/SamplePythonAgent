Adversarial Agent
--Final Goal--
"Hagent" (Hacker-Agent): An AI agent that can autonomously discover adversarial vulnerabilities in neural operator surrogate models used in nuclear reactor digital twins. 

We want to see if the LLM can replicate the vulnerability methodology of this paper when given only a black box of inputs and outputs:
Roy, S., Kobayashi, K., Chakraborty, S., Rizwan-uddin, & Alam, S.B. (2026). Adversarial Vulnerabilities in Neural Operator Digital Twins: Gradient-Free Attacks on Nuclear Thermal-Hydraulic Surrogates. arXiv:2603.22525

Overview

This project builds an AI agent that can reason about physics problems from first principles, evaluated against five physics simulators with known analytical solutions. The goal is to verify the agent has genuine physics reasoning capability before deploying it to discover adversarial vulnerabilities in neural operator surrogate models used in nuclear reactor digital twins.

Project Structure

CMU_Project/
  src/
    adversarial_agent/      ← AI agent (ReAct loop, tools, Claude API, calls Opus 4.8)
    simulators/
      idealGasLaw/          ← Simulator 1: PV = nRT
      RadioactiveDecay/     ← Simulator 2: N(t) = N0 * e^(-λt)
      SeperableDiffEqs/     ← Simulator 3: dy/dx = f(x)g(y)
      HeatConduction/       ← Simulator 4: k * d²T/dx² = 0
      NeutronDiffusion/     ← Simulator 5: D * d²φ/dx² - Σa * φ = 0
  tests/
    eval.py                 ← Automated eval pipeline
    transcript_reader.py    ← Debug tool for inspecting agent reasoning
  transcripts/              ← Per-question agent reasoning traces (auto-generated)

Physics Simulators So Far

Each simulator increases in difficulty. It provides an analytical ground truth to compare with the agent. The agent never sees the simulator code, it only receives the question in natural language and must solve it independently.

1. Gas LawPV = nRT — solve for any variable given the other three
2. Radioactive DecayN(t) = N₀ · e^(-λt) — exponential decay with half-life conversion
3. Separable ODEsdy/dx = k·y (exponential) and dy/dx = ax^n (polynomial)
4. 1D Heat ConductionSteady-state k·d²T/dx² + Q = 0 with optional internal heat generationSobhani et al. (2019)
5. 1D Neutron DiffusionD·d²φ/dx² - Σa·φ = 0 with hyperbolic sine solution "Duderstadt & Hamilton (1976)"

Eval Results

The agent achieves 100% pass rate across all 5 simulators in both tool-enabled mode (writes and runs Python scripts) and reasoning-only mode (no tools). All answers are much less than the 1% tolerance of the ground truth — consistent with the ~1.5% production-grade accuracy threshold used in Roy et al. (2026).

Notably, on the hardest question (neutron diffusion with highly absorbing material requiring evaluation of sinh(31.623)), the agent correctly approximated the large-argument hyperbolic function using exponential asymptotics and log base conversion, achieving 0.02% error without any code execution.

Setup:

  Prerequisites

  Python 3.10+
  Anthropic API key


Installation

bashgit clone <repo>
cd CMU_Project
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -e .

Configuration

Copy .env.example to .env and add your Anthropic API key:

ANTHROPIC_API_KEY=your_key_here

Running the Agent (Interactive Mode)

bashpython -m adversarial_agent.main

Running Evals

# Run a specific simulator
python tests/eval.py idealGasLaw
python tests/eval.py RadioactiveDecay
python tests/eval.py SeperableDiffEqs
python tests/eval.py HeatConduction
python tests/eval.py NeutronDiffusion

# Run all simulators
python tests/eval.py

# List available simulators
python tests/eval.py --list

Debugging Failures

Each question automatically generates a transcript at transcripts/<simulator>_Q<n>.jsonl logging the agent's full reasoning trace, tool calls, and thinking blocks.

# List all transcripts
python tests/transcript_reader.py --list

# Read a specific transcript (summarized)
python tests/transcript_reader.py transcripts/NeutronDiffusion_Q4.jsonl

# Full thinking trace
python tests/transcript_reader.py transcripts/NeutronDiffusion_Q4.jsonl --full

Agent Architecture

The agent is a ReAct-style loop built on the Anthropic API (Claude Opus 4.8) with the following tools:

bash: run shell commands
read_file / write_file / edit_file — file I/O
subagent: spawn and use a sub-agent for delegated tasks

In eval mode, tool confirmations are auto-approved and all output is silenced except the final ANSWER: <number> line, which eval.py captures and checks against the ground truth oracle.

Eval Tolerances

All simulators use 1% relative tolerance. Since our simulators have exact analytical solutions, 1% accounts only for floating point rounding and agent response formatting.

References

Roy et al. (2026) — Adversarial Vulnerabilities in Neural Operator Digital Twins. arXiv:2603.22525
Sobhani et al. (2019) — Modulation of heat transfer for extended flame stabilization in porous media burners via topology gradation. Proceedings of the Combustion Institute, 37(4), 5697–5704. DOI: 10.1016/j.proci.2018.05.155
Duderstadt, J.J. & Hamilton, L.J. (1976) — Nuclear Reactor Analysis. John Wiley & Sons. ISBN: 978-0471223634
Li et al. (2021) — Fourier Neural Operator for Parametric Partial Differential Equations. ICLR 2021. arXiv:2010.08895
