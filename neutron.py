import math

# Parameters
a = 100.0       # cm
phi0 = 1e12     # neutrons/cm^2/s
D = 0.9         # cm
sigma_a = 0.01  # cm^-1
x = 50.0        # cm

# Diffusion equation: D d^2phi/dx^2 - sigma_a * phi = 0
# General solution: phi(x) = A sinh(kx) + B cosh(kx)
# where k = sqrt(sigma_a / D)

kappa = math.sqrt(sigma_a / D)
print(f"kappa = {kappa:.6f} cm^-1")
print(f"kappa*a = {kappa*a:.6f}")
print(f"kappa*50 = {kappa*50:.6f}")

# Boundary conditions:
#   phi(0) = phi0  =>  B = phi0
#   phi(a) = 0     =>  A sinh(ka) + phi0 cosh(ka) = 0
#                  =>  A = -phi0 cosh(ka)/sinh(ka)
#
# Solution simplifies to:
#   phi(x) = phi0 * sinh(kappa*(a - x)) / sinh(kappa*a)

phi_50 = phi0 * math.sinh(kappa * (a - x)) / math.sinh(kappa * a)

print(f"\nphi(50) = {phi_50:.6e} neutrons/cm^2/s")
print(f"phi(50) = {phi_50}")

# Verify boundary conditions
phi_0 = phi0 * math.sinh(kappa * a) / math.sinh(kappa * a)
phi_a = phi0 * math.sinh(kappa * 0) / math.sinh(kappa * a)
print(f"\nVerification:")
print(f"phi(0)   = {phi_0:.6e} (should be {phi0:.6e})")
print(f"phi(100) = {phi_a:.6e} (should be 0)")
