"""
#2 SIMPLEST SIMULATOR
Radioactive Decay 
Formula: A(t) = A(0) * e^(-λ * t)
 
Where:
  A(0)     = initial amount (grams or atoms)
  λ = decay constant (1/time)
  t      = time elapsed
  A(t)   = remaining amount at time t
 
Relationship between λ and half-life (t_half):
  λ = ln(2) / t_half  →  t_half = ln(2) / λ
"""
 
import math
 
# --- Core solver functions ---

 #A(t) = A(0) * e^(-λ * t)

def solveFor_A(A0: float, λ: float, t: float) -> float:
    """Given initial quantity, decay constant, and time, return remaining quantity."""
    return A0 * math.exp(-λ * t)
    #math.exp is e^x where x in this case is (-λ * t)
 
 #A(t) = A(0) * e^(-λ * t)
 #A(t)/A(0) = e^(-λ * t)
 #ln(A(t)/A(0)) = -λ * t
 #-ln(A(t)/A(0))/λ = t
def solveFor_t(A0: float, A: float, λ: float) -> float:
    """Given initial quantity, remaining quantity, and decay constant, return time elapsed."""
    return -math.log(A / A0) / λ
    #math.log is default ln when there is only one argument
 
 #A(t) = A(0) * e^(-λ * t)
 #A(t)/A(0) = e^(-λ * t)
 #1/A(0) = e^(-λ * t)/A(t)
 #A(0) = A(t)/e^(-λ * t)
def solveFor_A0(A: float, λ: float, t: float) -> float:
    """Given remaining quantity, decay constant, and time → return initial quantity."""
    return A / math.exp(-λ * t)
 
 
def halfLifeToDecayConstant(t_half: float) -> float:
    """Convert half-life to decay constant. Useful since questions usually give half-life."""
    return math.log(2) / t_half
 
 
def decayConstantToHalfLife(λ: float) -> float:
    """Convert decay constant back to half-life."""
    return math.log(2) / λ


 
# Carbon-14 half-life in years
C14_HALF_LIFE = 5730
C14_LAMBDA = halfLifeToDecayConstant(C14_HALF_LIFE)
 
# Iodine-131 half-life in days
I131_HALF_LIFE = 8.02
I131_LAMBDA = halfLifeToDecayConstant(I131_HALF_LIFE)
 
# Uranium-238 half-life in years
U238_HALF_LIFE = 4.468e9
U238_LAMBDA = halfLifeToDecayConstant(U238_HALF_LIFE)
 
 #list of dictionaries
sampleQuestions = [
    {
        "question": (
            "A sample starts with 100 grams of Carbon-14, which has a half-life of 5730 years. "
            "How many grams remain after 11,460 years?"
        ),
        "answer": solveFor_A(A0=100, λ=C14_LAMBDA, t=11460),
        "variable": "A(t)",
        "note": "Exactly 2 half-lives, so answer should be ~25g",
    },
    {
        "question": (
            "Iodine-131 has a half-life of 8.02 days. A hospital sample starts with 50 grams. "
            "How many grams remain after 24.06 days?"
        ),
        "answer": solveFor_A(A0=50, λ=I131_LAMBDA, t=24.06),
        "variable": "A(t)",
        "note": "Exactly 3 half-lives, so answer should be ~6.25g",
    },
    {
        "question": (
            "A radioactive isotope has a decay constant of 0.0237 per year. "
            "A sample starts with 214.3 grams. How many grams remain after 51.679 years?"
        ),
        "answer": solveFor_A(A0=214.3, λ=0.0237, t=51.679),
        "variable": "A(t)",
    },
    {
        "question": (
            "A Carbon-14 sample originally had 80.128 grams. It now has 21.447 grams. "
            "Carbon-14 has a half-life of 5730 years. How many years have passed?"
        ),
        "answer": solveFor_t(A0=80.128, A=21.447, λ=C14_LAMBDA),
        "variable": "t",
    },
    {
        "question": (
            "After 43.51 days, a sample of Iodine-131 contains 3.529 grams. "
            "Iodine-131 has a half-life of 8.02 days. "
            "What was the initial quantity in grams?"
        ),
        "answer": solveFor_A0(A=3.529, λ=I131_LAMBDA, t=43.51),
        "variable": "A0",
    },
]

if __name__ == "__main__":
    # Sanity check — print all sample answers
    for i, sample in enumerate(sampleQuestions, 1):
        print(f"Q{i}: {sample['question']}")
        #print(f"     Ground truth ({sample['variable']}): {sample['answer']:.4f}")
        print(f" Answer:{sample['answer']:.4f}")
        if "note" in sample:
            print(f"     Note: {sample['note']}")
        print()