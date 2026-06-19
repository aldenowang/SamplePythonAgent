"""
Linear Equation Solver
======================
Solves:
  1. Single linear equations   (e.g.  2x + 3 = 7)
  2. Systems of linear equations (e.g.  2x + 3y = 7,  x - y = 1)

No external dependencies — uses only the Python standard library.
"""

import re
from fractions import Fraction
from typing import Dict, List, Optional, Tuple


# ──────────────────────────────────────────────
#  Parsing a single linear equation string
# ──────────────────────────────────────────────

def _tokenize(expr: str) -> List[str]:
    """Split an expression into tokens (numbers, variables, operators)."""
    return re.findall(r'[+\-]|[A-Za-z_]\w*|\d+\.?\d*', expr)


def _parse_linear_expr(expr: str) -> Tuple[Dict[str, Fraction], Fraction]:
    """
    Parse a linear expression (no '=' sign) and return
    (coefficients_dict, constant) so that
        expression == sum(coeff * var for var, coeff in dict.items()) + constant
    """
    # Normalize: remove spaces and insert '+' before a bare '-' so the
    # regex can split on sign boundaries.
    expr = expr.replace(" ", "")
    # Split into signed terms, e.g. "2x-3y+4" -> ['+2x', '-3y', '+4']
    terms = re.findall(r'[+-]?[^+-]+', expr)

    coeffs: Dict[str, Fraction] = {}
    constant = Fraction(0)

    for term in terms: 
        term = term.strip()
        if not term:
            continue
        # Try to match  optional_sign  optional_number  variable_name
        m = re.fullmatch(r'([+-]?\d*\.?\d*)\s*([A-Za-z_]\w*)', term)
        if m:
            coeff_str, var = m.groups()
            if coeff_str in ('', '+'):
                coeff = Fraction(1)
            elif coeff_str == '-':
                coeff = Fraction(-1)
            else:
                coeff = Fraction(coeff_str).limit_denominator(10**12)
            coeffs[var] = coeffs.get(var, Fraction(0)) + coeff
        else:
            # Pure numeric constant
            constant += Fraction(term).limit_denominator(10**12)

    return coeffs, constant


def parse_equation(equation: str) -> Tuple[Dict[str, Fraction], Fraction]:
    """
    Parse  'LHS = RHS'  and return (coefficients, constant) such that
        sum(coeff * var) = constant
    i.e. everything is moved so variables are on the left and constants
    on the right.
    """
    if '=' not in equation:
        raise ValueError(f"Not an equation (no '=' sign): {equation}")

    lhs, rhs = equation.split('=', 1)
    #print("Here: " + rhs)
    lcoeffs, lconst = _parse_linear_expr(lhs)
    rcoeffs, rconst = _parse_linear_expr(rhs)

    # Move RHS variables to LHS and LHS constants to RHS
    all_vars = set(lcoeffs) | set(rcoeffs)
    coeffs = {}
    for v in all_vars:
        c = lcoeffs.get(v, Fraction(0)) - rcoeffs.get(v, Fraction(0))
        if c != 0:
            coeffs[v] = c
    constant = rconst - lconst  # moved to right side

    return coeffs, constant


# ──────────────────────────────────────────────
#  Solve a SINGLE linear equation  (one variable)
# ──────────────────────────────────────────────

def solve_single(equation: str) -> Dict[str, Fraction]:
    """
    Solve a single linear equation with one unknown.
    Returns a dict  { variable_name: value }.
    """
    coeffs, constant = parse_equation(equation)

    if len(coeffs) == 0:
        if constant == 0:
            raise ValueError("Identity (0 = 0): infinitely many solutions.")
        else:
            raise ValueError(f"Contradiction ({-constant} = {constant}): no solution.")

    if len(coeffs) > 1:
        raise ValueError(
            "Single‑equation solver received more than one variable: "
            f"{list(coeffs.keys())}. Use the system solver instead."
        )

    var, coeff = next(iter(coeffs.items()))
    return {var: constant / coeff}


# ──────────────────────────────────────────────
#  Solve a SYSTEM of linear equations (Gaussian elimination)
# ──────────────────────────────────────────────

def solve_system(equations: List[str]) -> Dict[str, Fraction]:
    """
    Solve a system of N linear equations in N unknowns using
    Gaussian elimination with partial pivoting (exact arithmetic
    via fractions).
    """
    # Parse all equations
    parsed = [parse_equation(eq) for eq in equations]

    # Collect ordered list of variables
    var_set: dict = {}  # use dict to preserve insertion order
    for coeffs, _ in parsed:
        for v in coeffs:
            var_set[v] = None
    variables = list(var_set.keys())
    n = len(variables)

    if len(parsed) != n:
        raise ValueError(
            f"Expected {n} equations for {n} unknowns {variables}, "
            f"but got {len(parsed)} equations."
        )

    # Build augmented matrix  [A | b]  (list of lists of Fraction)
    matrix: List[List[Fraction]] = []
    for coeffs, const in parsed:
        row = [coeffs.get(v, Fraction(0)) for v in variables] + [const]
        matrix.append(row)

    # Forward elimination
    for col in range(n):
        # Partial pivot: find the row with the largest absolute value
        max_row = col
        for row in range(col + 1, n):
            if abs(matrix[row][col]) > abs(matrix[max_row][col]):
                max_row = row
        matrix[col], matrix[max_row] = matrix[max_row], matrix[col]

        pivot = matrix[col][col]
        if pivot == 0:
            raise ValueError(
                "Singular system (no unique solution). "
                "The equations may be dependent or contradictory."
            )

        # Eliminate below
        for row in range(col + 1, n):
            factor = matrix[row][col] / pivot
            for j in range(col, n + 1):
                matrix[row][j] -= factor * matrix[col][j]

    # Back substitution
    solution = [Fraction(0)] * n
    for i in range(n - 1, -1, -1):
        s = matrix[i][n]
        for j in range(i + 1, n):
            s -= matrix[i][j] * solution[j]
        solution[i] = s / matrix[i][i]

    return {variables[i]: solution[i] for i in range(n)}


# ──────────────────────────────────────────────
#  Pretty helpers
# ──────────────────────────────────────────────

def _format_value(v: Fraction) -> str:
    """Return a nice string: integer when possible, otherwise a fraction."""
    if v.denominator == 1:
        return str(v.numerator)
    return str(v)


def print_solution(solution: Dict[str, Fraction]) -> None:
    for var in sorted(solution):
        print(f"  {var} = {_format_value(solution[var])}")


# ──────────────────────────────────────────────
#  Interactive menu
# ──────────────────────────────────────────────

def main() -> None:
    print("=" * 50)
    print("       LINEAR EQUATION SOLVER")
    print("=" * 50)

    while True:
        print("\nChoose an option:")
        print("  1) Solve a single linear equation")
        print("  2) Solve a system of linear equations")
        print("  3) Quit")

        choice = input("\n> ").strip()

        if choice == "1":
            print("\nEnter a linear equation (e.g.  2x + 3 = 7 ):")
            eq = input("> ").strip()
            try:
                sol = solve_single(eq)
                print("\nSolution:")
                print_solution(sol)
            except ValueError as e:
                print(f"\nError: {e}")

        elif choice == "2":
            print("\nHow many equations? ", end="")
            try:
                count = int(input().strip())
            except ValueError:
                print("Please enter a valid integer.")
                continue
            eqs: List[str] = []
            print(f"Enter {count} equations (e.g.  2x + 3y = 7 ):")
            for i in range(1, count + 1):
                eqs.append(input(f"  eq{i}> ").strip())
            try:
                sol = solve_system(eqs)
                print("\nSolution:")
                print_solution(sol)
            except ValueError as e:
                print(f"\nError: {e}")

        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
