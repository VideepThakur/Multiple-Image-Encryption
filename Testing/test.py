import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

def lorentz(t, xyz, sigma, rho, beta):
    x, y, z = xyz
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]

sigma = 10
rho = 28
beta = 8 / 3

initial_conditions_1 = [10.0, 0.0, 10.0]
initial_conditions_2 = [10.01, 0.0, 10.0]

t_span = (0, 50)
t_eval = np.linspace(*t_span, 10000)

sol_1 = solve_ivp(lorentz, t_span, initial_conditions_1, args=(sigma, rho, beta), t_eval=t_eval)
sol_2 = solve_ivp(lorentz, t_span, initial_conditions_2, args=(sigma, rho, beta), t_eval=t_eval)

plt.figure(figsize=(10, 6))
plt.plot(sol_1.t, sol_1.y[0] - sol_2.y[0], label='Difference in x variable')
plt.xlabel('Time')
plt.ylabel('Difference')
plt.title('Differences in x Variable for Slightly Different Initial Conditions')
plt.legend()
plt.grid(True)
plt.show()
