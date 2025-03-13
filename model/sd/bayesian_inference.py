import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pymc as pm
import pytensor
from scipy.integrate import odeint

# Initial conditions
U0 = 5000  # Under investigation
C0 = 1000  # Charged
Mb0 = 800  # Magistrate Court Backlog
M0 = 600  # In Magistrate Court
Cb0 = 400  # Referred to Crown Court Backlog
Cc0 = 300  # In Crown Court
P0 = 200  # Imprisoned
D0 = 0  # Dismissed
y0 = [U0, C0, Mb0, M0, Cb0, Cc0, P0, D0]

# Time grid (e.g., days)
t = np.linspace(0, 5, 6)


# Define the ODE system
def justice_system(y, t, lam, delta):
    U, C, Mb, M, Cb, Cc, P, D = y
    lam1, lam2, lam3, lam4, lam5, lam6 = lam
    delta_C, delta_Mb, delta_M, delta_Cb, delta_Cc, delta_P = delta

    dUdt = -lam1 * U
    dCdt = lam1 * U - (lam2 + delta_C) * C
    dMbdt = lam2 * C - (lam3 + delta_Mb) * Mb
    dMdt = lam3 * Mb - (lam4 + delta_M) * M
    dCbdt = lam4 * M - (lam5 + delta_Cb) * Cb
    dCcdt = lam5 * Cb - (lam6 + delta_Cc) * Cc
    dPdt = lam6 * Cc - delta_P * P
    dDdt = (
        delta_C * C
        + delta_Mb * Mb
        + delta_M * M
        + delta_Cb * Cb
        + delta_Cc * Cc
        + delta_P * P
    )

    return [dUdt, dCdt, dMbdt, dMdt, dCbdt, dCcdt, dPdt, dDdt]


# Bayesian inference with PyMC
with pm.Model() as model:
    # Priors for lambda rates
    lam = pm.Lognormal("lam", mu=np.log(0.1), sigma=0.5, shape=6)

    # Priors for dismissal rates
    delta = pm.Lognormal("delta", mu=np.log(0.05), sigma=0.5, shape=6)

    # Solve ODE system
    def simulate_justice(lam_values, delta_values):
        f_lam = pytensor.function([], lam_values)
        f_delta = pytensor.function([], delta_values)
        lam_values = f_lam()
        delta_values = f_delta()
        solution = odeint(justice_system, y0, t, args=(lam_values, delta_values))
        return pytensor.tensor.as_tensor_variable(solution)

    # Simulated trajectories for all compartments
    justice_sim = pm.Deterministic("justice_sim", simulate_justice(lam, delta))

    # Example observed data (replace with real data)
    observed_data = {
        "U": np.array([5000, 4800, 4600, 4500, 4400, 4300]),
        "C": np.array([1000, 1030, 900, 800, 700, 600]),
        "Mb": np.array([800, 850, 870, 860, 850, 830]),
        "M": np.array([600, 620, 630, 640, 650, 660]),
        "Cb": np.array([400, 410, 420, 430, 440, 450]),
        "Cc": np.array([300, 310, 320, 330, 340, 350]),
        "P": np.array([200, 210, 220, 230, 240, 250]),
        "D": np.array([0, 20, 50, 80, 100, 150]),
    }

    # Loop through each compartment to define likelihood
    for i, state in enumerate(["U", "C", "Mb", "M", "Cb", "Cc", "P", "D"]):
        pm.Poisson(f"obs_{state}", mu=justice_sim[:, i], observed=observed_data[state])

    # Sample from the posterior
    trace = pm.sample(2000, tune=1000, cores=2, return_inferencedata=True)

# Analyze results
az.plot_posterior(trace, var_names=["lam", "delta"])
plt.show()
az.plot_trace(trace, var_names=["lam", "delta"])
plt.show()
print(az.summary(trace))
