"""
#1 SIMPLEST SIMULATOR
Ideal Gas Law

Given 3 variables the LLM should be able to solve for the 4th.
This class gives the actual answers (A(q)), to check against the LLM.
Agent never sees this file.

Formula: PV = nRT
  P = pressure (atm)
  V = volume (liters)
  n = moles of gas
  R = 0.0821 L·atm / (mol·K)
  T = temperature (Kelvin)
"""

R = 0.0821 # L*atm/mol*K

#PV = nRT
#T = PV/nR
def solveFor_T(P: float, V: float, n: float) -> float:
    """Given P, V, n → return temperature in Kelvin."""
    return (P * V) / (n * R)
 
 #PV = nRT
 #P = nRT/V
def solveFor_P(V: float, n: float, T: float) -> float:
    """Given V, n, T → return pressure in atm."""
    return (n * R * T) / V
 
 #PV = nRT
 #V = nRT/P
def solveFor_V(P: float, n: float, T: float) -> float:
    """Given P, n, T → return volume in liters."""
    return (n * R * T) / P
 
 #PV = nRT
 #n = PV/RT
def solveFor_n(P: float, V: float, T: float) -> float:
    """Given P, V, T → return moles of gas."""
    return (P * V) / (R * T)

#list of dictionaries
sampleQuestions = [
    {
        "question": "A gas has a pressure of 4.63 atm, a volume of 11.323 liters, and contains 1.255 moles of gas. What is the temperature in Kelvin?",
        "answer": solveFor_T(P=4.63, V=11.323, n=1.255),
    },
    {
        "question": "A gas occupies 5 liters, contains 0.5 moles, and is at a temperature of 300 Kelvin. What is the pressure in atm?",
        "answer": solveFor_P(V=5, n=0.5, T=300),
    },
    {
        "question": "A gas has a pressure of 1.135 atm, contains 2.946 moles, and is at 273.471 Kelvin. What is the volume in liters?",
        "answer": solveFor_V(P=1.135, n=2.946, T=273.471),
    },
    {
        "question": "A gas has a pressure of 3.333 atm, a volume of 8.146 liters, and a temperature of 400.716 Kelvin. How many moles of gas are present?",
        "answer": solveFor_n(P=3.333, V=8.146, T=400.716),
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