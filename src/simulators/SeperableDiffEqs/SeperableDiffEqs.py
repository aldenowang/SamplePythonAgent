"""
#3 SIMPLEST SIMULATOR 

A separable ODE (ordinary differential equation) is one you can rearrange
 so all y terms are on one side and all x terms are on the other,
then you can integrate both sides separately with respect to different variables.
 
General form:  dy/dx = f(x) * g(y) or y' = f(x) * g(y)
Rearranged:    dy / g(y) = f(x) dx
Then integrate both sides to get the solution.
  
TYPE 1 — Exponential growth/decay:
    dy/dx = ky  →  y(x) = y0 * e^(kx)
 
TYPE 2 — Simple separable (f(x) only):
    dy/dx = f(x)  →  y(x) = F(x)+ C
    e.g. dy/dx = 3x²  →  y = x³ + C
"""
 
import math
 
 
# --- Type 1: Exponential growth/decay ---
# dy/dx = k*y
#dy/y = kdx  (integrate both sides)
#ln|y| = kx + c
#y = e^(kx + c)
#y = e^(kx) * e^c
#y = Ce^(kx)
#C = y0
#y = y0 * e^(kx)
 
def solveExponential(y0: float, k: float, x: float) -> float:
    """
    Solve dy/dx = k*y with initial condition y(0) = y0.
    Returns y at position x.
    
    k > 0 → growth, k < 0 → decay
    """
    return y0 * math.exp(k * x)
 
 
# --- Type 2: Simple separable  ---
# dy/dx = ax^n
#dy = ax^n dx
#y = a/(n+1)x^(n+1) + c
#y0 = c
#y = a/(n+1)x^(n+1) + y0
 
def solveSimpleSeperable(y0: float, a: float, n: float, x: float) -> float:
    #dy/dx = ax^n
    """
    Solve dy/dx = a * x^n with initial condition y(0) = y0.
    Returns y at position x.
    
    Example: dy/dx = 3x²  →  y = y0 + x³
    """
    return (a / (n + 1)) * (x ** (n + 1)) + y0



 # list of dictionaries

 #!!Make sure to track agent thinking process to make sure it does the work correctly
 

sampleQuestions = [
    {
        "question": (
            "A population grows according to dy/dx = 0.3 * y. "
            "The initial population at x=0 is 50. "
            "What is the population at x=5?"
        ),
        "answer": solveExponential(y0=50, k=0.3, x=5),
        "equation": "y = 50 * e^(0.3x)"
    },
    {
        "question": (
            "A radioactive substance decays according to dy/dx = -0.1 * y. "
            "The initial amount at x=0 is 200 grams. "
            "How many grams remain at x=10?"
        ),
        "answer": solveExponential(y0=200, k=-0.1, x=10),
        "equation": "y = 200 * e^(-0.1x)"
    },
    {
        "question": (
            "Solve the ODE dy/dx = 3x², with initial condition y(0) = 5. "
            "What is y when x = 2?"
        ),
        "answer": solveSimpleSeperable(y0=5, a=3, n=2, x=2),
        "equation": "x^3 + 5",
    },
    {
        "question": (
            "Solve dy/dx = 12x³, with initial condition y(0) = 0. "
            "What is y when x = 3?"
        ),
        "answer": solveSimpleSeperable(y0=0, a=12, n=3, x=3),
        "equation": "3x^4 + 0",
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