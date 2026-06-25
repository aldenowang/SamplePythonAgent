"""
1D Steady-State Neutron Diffusion Simulator

    High flux → lots of fission → lots of heat generated.
    Low flux  → little fission → reactor dying out.
 
THE EQUATION (1-group, 1D, steady-state):
 
    D * d²φ/dx² - Σa * φ + S = 0
 
    Where:
        φ(x)  = neutron flux at position x (neutrons/cm²/s)
        D     = diffusion coefficient (cm) — how easily neutrons move
        Σa    = macroscopic absorption cross section (1/cm) — how fast
                neutrons get absorbed by the material
        S     = external neutron source (neutrons/cm³/s), 0 if no source. 
        S = always 0 for our purposes.
        L²    = D / Σa  (diffusion length squared, cm²)
 
SOLUTION after solving the differential equation and no external source, S=0
        φ(x) = φ0 * sinh((a - x) / L) / sinh(a / L)
 
"""
 
import math
 
 
def diffusionLength(D: float, sigma_a: float) -> float:
    """
    L represents the average distance a neutron travels before being absorbed.
    """
    return math.sqrt(D / sigma_a)
 
 
def solveNeutronFlux(x: float, phi0: float, a: float, D: float, sigma_a: float) -> float:
    """
    Solve 1D steady-state neutron diffusion with NO external source (S=0).
 
    Boundary conditions:
        φ(0) = phi0   (known flux at left end)
        φ(a) = 0      (no neutrons at right boundary)
 
    Solution:
        φ(x) = phi0 * sinh((a - x) / L) / sinh(a / L)
 
    Args:
        x       : position along reactor (cm), must satisfy 0 <= x <= a
        phi0    : neutron flux at x=0 (neutrons/cm²/s)
        a       : total length of reactor slab (cm)
        D       : diffusion coefficient (cm)
        sigma_a : macroscopic absorption cross section (1/cm)
 
    Returns:
        Neutron flux φ at position x
    """
    if not (0 <= x <= a):
        raise ValueError(f"x={x} must be between 0 and a={a}")
 
    L = diffusionLength(D, sigma_a)
    return phi0 * math.sinh((a - x) / L) / math.sinh(a / L)
 
  
sampleQuestions = [
    {
        "question": (
            "A 1D nuclear reactor slab has length a = 100 cm. "
            "The neutron flux at x=0 is phi0 = 1e12 neutrons/cm^2/s, "
            "and the flux vanishes at x=100 cm. "
            "The diffusion coefficient is D = 0.9 cm and the macroscopic "
            "absorption cross section is sigma_a = 0.01 cm^-1. "
            "There is no external neutron source. "
            "What is the neutron flux at x = 50 cm?"
        ),
        "answer": solveNeutronFlux(
            x=50, phi0=1e12, a=100, D=0.9, sigma_a=0.01
        ),
    },
    {
        "question": (
            "A reactor slab has length a = 60 cm. "
            "The neutron flux at x=0 is phi0 = 5e11 neutrons/cm^2/s "
            "and vanishes at x=60 cm. "
            "D = 1.2 cm, sigma_a = 0.02 cm^-1, no external source. "
            "What is the diffusion length L in cm?"
        ),
        "answer": diffusionLength(D=1.2, sigma_a=0.02),
    },
    {
        "question": (
            "A reactor slab has length a = 80 cm. "
            "The neutron flux at x=0 is phi0 = 1e13 neutrons/cm^2/s "
            "and vanishes at x=80 cm. "
            "D = 0.8 cm, sigma_a = 0.008 cm^-1, no external source. "
            "What is the neutron flux at x = 20 cm?"
        ),
        "answer": solveNeutronFlux(
            x=20, phi0=1e13, a=80, D=0.8, sigma_a=0.008
        ),
    },
    {
        "question": (
            "A reactor slab has length a = 100 cm. "
            "The neutron flux at x=0 is phi0 = 1e12 neutrons/cm^2/s "
            "and vanishes at x=100 cm. "
            "The material is highly absorbing: D = 0.5 cm, sigma_a = 0.05 cm^-1. "
            "There is no external neutron source. "
            "What is the neutron flux at x = 75 cm?"
        ),
        "answer": solveNeutronFlux(
            x=75, phi0=1e12, a=100, D=0.5, sigma_a=0.05
        ),

        "note": (
            "L = sqrt(0.5/0.05) = sqrt(10) ≈ 3.16 cm, very short diffusion length. "
            "Neutrons get absorbed almost immediately so flux drops drastically. "
            "x=75 is close to the boundary so flux should be extremely low."
        ),
    },
]
 
 #print questions and answers
if __name__ == "__main__":
    for i, sample in enumerate(sampleQuestions, 1):
        print(f"Q{i}: {sample['question']}")
        print()
        print(f" Answer:{sample['answer']:.4f}")
        if "note" in sample:
            print(f" Note: {sample['note']}")
        print()
        print()