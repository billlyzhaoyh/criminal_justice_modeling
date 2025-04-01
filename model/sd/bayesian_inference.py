import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pymc as pm
import pytensor
from scipy.integrate import odeint

# Initial conditions for the compartments:
I0 = 10000  # Innocent
U0 = 5000  # Under Investigation
C0 = 1000  # Charged
Mb0 = 800  # Magistrate Court Backlog
M0 = 600  # In Magistrate Court
Cb0 = 400  # Crown Court Backlog
Cc0 = 300  # In Crown Court
P0 = 200  # Imprisoned
y0 = [I0, U0, C0, Mb0, M0, Cb0, Cc0, P0]

# Time grid (e.g., days or weeks)
t = np.linspace(0, 5, 6)


# Define the ODE system that mirrors your SD model
def justice_system(y, t, lam):
    I, U, C, Mb, M, Cb, Cc, P = y
    # lam[0] is the rate at which Innocent become Under Investigation (crime rate)
    lam0, lam1, lam2, lam3, lam4, lam5, lam6, lam7 = lam

    dUdt = -lam1 * U + lam0 * I
    dCdt = lam1 * U - lam2 * C
    dMbdt = lam2 * C - lam3 * Mb
    dMdt = lam3 * Mb - lam4 * M
    dCbdt = lam4 * M - lam5 * Cb
    dCcdt = lam5 * Cb - lam6 * Cc
    dPdt = lam6 * Cc - lam7 * P
    # Flow returning to Innocent: accumulates from all downstream compartments
    dIdt = (
        -lam0 * I + lam2 * C + lam3 * Mb + lam4 * M + lam5 * Cb + lam6 * Cc + lam7 * P
    )

    return [dIdt, dUdt, dCdt, dMbdt, dMdt, dCbdt, dCcdt, dPdt]


with pm.Model() as model:
    # Priors for the 8 transition rates (lam₀ to lam₇)
    lam = pm.Lognormal("lam", mu=np.log(0.1), sigma=0.5, shape=8)

    # Define a function to simulate the system given lam values
    def simulate_justice(lam_values):
        # Evaluate the symbolic lam values to numeric values
        f_lam = pytensor.function([], lam_values)
        lam_values = f_lam()
        # Solve the ODE system over the time grid
        solution = odeint(justice_system, y0, t, args=(lam_values,))
        return pytensor.tensor.as_tensor_variable(solution)

    # Deterministic simulation of all compartments over time
    justice_sim = pm.Deterministic("justice_sim", simulate_justice(lam))

    # Example observed data for each compartment (adjust these as needed)
    observed_data = {
        "I": np.array([10000, 9850, 9700, 9550, 9400, 9250]),
        "U": np.array([5000, 4800, 4600, 4400, 4200, 4000]),
        "C": np.array([1000, 1100, 1150, 1180, 1200, 1220]),
        "Mb": np.array([800, 820, 850, 870, 880, 890]),
        "M": np.array([600, 620, 630, 640, 650, 660]),
        "Cb": np.array([400, 410, 420, 430, 440, 450]),
        "Cc": np.array([300, 320, 340, 360, 380, 400]),
        "P": np.array([200, 220, 240, 260, 280, 300]),
    }

    # Define a Poisson likelihood for each compartment using the simulated trajectory
    compartments = ["I", "U", "C", "Mb", "M", "Cb", "Cc", "P"]
    for i, comp in enumerate(compartments):
        pm.Poisson(f"obs_{comp}", mu=justice_sim[:, i], observed=observed_data[comp])

    # Sample from the posterior distribution
    trace = pm.sample(2000, tune=1000, cores=2, return_inferencedata=True)

# Posterior analysis and plotting
az.plot_posterior(trace, var_names=["lam"])
plt.show()

az.plot_trace(trace, var_names=["lam"])
plt.show()

print(az.summary(trace))
