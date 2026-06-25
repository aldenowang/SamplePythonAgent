import math

a = 80.0
phi0 = 1e13
D = 0.8
sigma_a = 0.008
x = 20.0

kappa = math.sqrt(sigma_a / D)
print("kappa =", kappa, "cm^-1")
print("kappa*a =", kappa * a)
print("kappa*(a-x) =", kappa * (a - x))

sinh_ka = math.sinh(kappa * a)
sinh_kamx = math.sinh(kappa * (a - x))
print("sinh(kappa*a) =", sinh_ka)
print("sinh(kappa*(a-x)) =", sinh_kamx)

ratio = sinh_kamx / sinh_ka
phi_20 = phi0 * ratio
print("ratio =", ratio)
print("phi(20) =", phi_20)
print("phi(20) = {:.4e}".format(phi_20))
