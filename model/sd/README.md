# ⚖️ Criminal Justice System Model – System Dynamics

This repository models the flow of individuals through various stages of the criminal justice system using a system dynamics approach (ODE-based). Each stage is represented as a compartment, and people "flow" through the system over time.

---

## 📦 Compartments

Each compartment represents a stage in the system:

- `I(t)`: Innocent
- `U(t)`: Under Investigation
- `C(t)`: Charged
- `M_b(t)`: Magistrate Court Backlog
- `M(t)`: In Magistrate Court
- `C_b(t)`: Crown Court Backlog
- `C_c(t)`: In Crown Court
- `P(t)`: In Prison

---

## 🔁 Transitions

The system is governed by a set of linear ordinary differential equations (ODEs):

```math
\frac{dU}{dt} = \lambda_0 I(t) - \lambda_1 U(t)
```
```math
\frac{dC}{dt} = \lambda_1 U(t) - \lambda_2 C(t)
```
```math
\frac{dM_b}{dt} = \lambda_2 C(t) - \lambda_3 M_b(t)
```
```math
\frac{dM}{dt} = \lambda_3 M_b(t) - \lambda_4 M(t)
```
```math
\frac{dC_b}{dt} = \lambda_4 M(t) - \lambda_5 C_b(t)
```
```math
\frac{dC_c}{dt} = \lambda_5 C_b(t) - \lambda_6 C_c(t)
```
```math
\frac{dP}{dt} = \lambda_6 C_c(t) - \lambda_7 P(t)
```
```math
\frac{dI}{dt} = -\lambda_0 I(t) + \lambda_2 C(t) + \lambda_3 M_b(t) + \lambda_4 M(t) + \lambda_5 C_b(t) + \lambda_6 C_c(t) + \lambda_7 P(t)
```

Here:
- $\lambda_i$ are the flow rates between stages.
- $\delta_{*}$ are the rates at which cases are dismissed from that stage.

Critical thinking:

- The dismissal rate at each stage is crucial. In a real-world setting, these may be estimated from historical data (e.g., proportion of charged cases that end up being dismissed).
- Rates might change over time, so you might need to extend this to allow time-varying transition rates (analogous to time-varying $R_t$ in epidemiology).