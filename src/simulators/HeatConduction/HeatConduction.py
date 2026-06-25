# #4 SIMPLEST SIMULATOR

"""
1D Steady-State Volumetric Heat Conduction Simulator
------------------------------------------

Inspired by the 1D volume-averaged thermal model used in CORNELL PROF PAPER:

    Sobhani, S., Mohaddes

The underlying governing equation for steady-state 1D heat conduction is:
    k * d²T/dx² = 0
    or d²T/dx² = 0  
    (k doesn't matter because it's a straight line with fixed temps on either end)
    where k is thermal conductivity.


With boundary conditions T(0) and T(L), this gives the
analytical solution:

    T(x) = T(0) + (T(L) - T(0)) * (x / L)

A linear temperature profile between the two boundary values.

We also include a version with an internal heat source (Q) (cornell version):

    k * d²T/dx² + Q = 0

An internal heat source is volumetric heat generation, 
where heat is being created inside the material.
E.g a wire conducting electricity, or a nuclear fuel rod.

After seperating and integrating twice, we get:

    T(x) = T(0) + (T(L) - T(0)) * (x/L)
           + (Q / (2*k)) * x * (L - x)

           Pretty much the previous equation added to the equation for the heat source.

Variables:
    T0  = temperature at x=0 (K or °C)
    TL  = temperature at x=L (K or °C)
    L   = length of the material (meters)
    k   = thermal conductivity (W/m·K)
    Q   = volumetric heat generation rate (W/m³), 0 if no source
    x   = position along the rod (meters), must be 0 <= x <= L
"""


def solve_temperature(
    x: float,
    T0: float,
    TL: float,
    L: float,
    k: float = 1.0,
    Q: float = 0.0
) -> float:

#k and q are default arguments unless called otherwise
    """
    Solve steady-state 1D heat conduction and return temperature at position x.

    With no heat source (Q=0):
        T(x) = T0 + (TL - T0) * (x / L)

    With internal heat generation (Q != 0):
        T(x) = T0 + (TL - T0) * (x/L) + (Q / (2*k)) * x * (L - x)

    Args:
        x   : position along rod (m), must satisfy 0 <= x <= L
        T0  : temperature at x=0
        TL  : temperature at x=L
        L   : total length of rod (m)
        k   : thermal conductivity (W/m·K), default 1.0
        Q   : volumetric heat generation (W/m³), default 0.0

    Returns:
        Temperature T at position x
    """
    if not (0 <= x <= L): #if the inputted position is greater than the length of the rod it throws an exception
        raise ValueError(f"x={x} must be between 0 and L={L}")

    linear_part = T0 + (TL - T0) * (x / L)
    heat_source_part = (Q / (2 * k)) * x * (L - x)
    return linear_part + heat_source_part

#fourier's law 
#does the agent know fourier's law?
#its kinda in the paper soo yeah
#q'' = -k * dT/dx
def solve_heat_flux(k: float, T0: float, TL: float, L: float) -> float:
    """
    Returns heat flux in W/m²  (negative = heat flows in -x direction)
    1D, linear, derivative is constant just the slope essentially
    """
    return -k * (TL - T0) / L



sampleQuestions = [
    {
        "question": (
            "A metal rod of length 1 meter has its left end held at 100°C "
            "and its right end held at 300°C. Assuming steady-state 1D heat "
            "conduction with no internal heat generation, what is the "
            "temperature at the midpoint (x = 0.5 m)?"
        ),
        "answer": solve_temperature(x=0.5, T0=100, TL=300, L=1.0),
    },
    {
        "question": (
            "A wall of thickness 0.2 meters has its left surface at 50°C "
            "and its right surface at 10°C. Assuming steady-state 1D heat "
            "conduction with no heat generation, what is the temperature "
            "at x = 0.05 m from the left surface?"
        ),
        "answer": solve_temperature(x=0.05, T0=50, TL=10, L=0.2),
    },
    {
         "question": (
            "A rod of length 4.4 meters has T(0) = 5.1°C and T(1) = 403°C. "
            "The rod has a uniform internal heat generation of Q = 6600 W/m³ "
            "and thermal conductivity k = 106 W/m·K. "
            "What is the temperature at x = 1.8 m?"
        ),
        "answer": solve_temperature(x=1.8, T0=5.1, TL=403, L=4.4, k=106, Q=6600),
    },
    {
        "question": (
            "A rod of length 1 meter has T(0) = 0°C and T(1) = 0°C. "
            "The rod has a uniform internal heat generation of Q = 1000 W/m³ "
            "and thermal conductivity k = 10 W/m·K. "
            "What is the temperature at the midpoint x = 0.5 m?"
        ),
        "answer": solve_temperature(x=0.5, T0=0, TL=0, L=1.0, k=10, Q=1000),
    },
    {
        #does the agent know fourier's law?
        "question": (
            "A steel rod (thermal conductivity k = 50 W/m·K) of length 0.5 m "
            "has its left end at 200°C and right end at 100°C. "
            "What is the heat flux through the rod in W/m²?"
        ),
        "answer": solve_heat_flux(k=50, T0=200, TL=100, L=0.5),
    },
]

#print questions and answers
if __name__ == "__main__":
    for i, sample in enumerate(sampleQuestions, 1):
        print(f"Q{i}: {sample['question']}")
        print(f" Answer:{sample['answer']:.4f}")
        if "note" in sample:
            print(f"     Note: {sample['note']}")
        print()
 