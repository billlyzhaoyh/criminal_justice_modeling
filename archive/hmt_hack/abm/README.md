# Simplistic Agent-Based Model in Python

This project implements a simplistic agent-based model to validate assumptions and system transition dynamics in a judicial system. It simulates the movement of cases through different stages, using probabilistic transitions and time distributions to model delays and outcomes.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Model Description](#model-description)
- [Simulation Process](#simulation-process)
- [Visualization](#visualization)
- [Scenarios](#scenarios)

## Introduction
This model simulates the flow of cases through various stages of the judicial system, such as investigation, charge, court backlog, and imprisonment. It allows for scenario analysis by modifying input parameters such as crime rates or processing speeds.

## Installation
To run this simulation, you need Python 3 and the following dependencies:

```sh
pip install numpy matplotlib pandas
```

## Usage
To run the simulation, execute the script:

```sh
python abm.py
```

This will:
- Initialize an agent population based on backlog statistics.
- Simulate case transitions over 730 days (two financial years).
- Plot the evolution of case counts across different states.
- Compare scenarios with different crime rates.

## Model Description
Each agent represents a case that progresses through a predefined set of states:

- **Under Investigation**
- **Charged**
- **Magistrate Court Backlog (MC Backlog)**
- **In Magistrate Court (In MC)**
- **Crown Court Backlog (CC Backlog)**
- **In Crown Court (In CC)**
- **Convicted**
- **Imprisoned**
- **Dismissed**

### Transition Probabilities
- Cases under investigation move to either **Charged (19%)** or **Dismissed (81%)**.
- Magistrate Court cases transition to Crown Court, conviction, or dismissal based on given probabilities.
- Crown Court cases either lead to conviction (91%) or dismissal (9%).
- Convicted cases move to **Imprisoned**, then ultimately to **Dismissed**.

### Time Spent in Each State
Each state has a mean duration, with a normal distribution (`mean / 3` standard deviation) to introduce variability.

## Simulation Process
The `simulate` function runs the model for `n` agents over `k` days:

1. Initializes agents based on backlog proportions.
2. Adds new cases each day under investigation.
3. Updates agents' state based on transition probabilities.
4. Tracks population spread across states over time.
5. Outputs results for visualization.

## Visualization
The model provides:

- **Time-Series Plot**: Tracks the number of cases in each state over time.
- **Scenario Comparison**: Evaluates the impact of different crime rates on system congestion.

Example output:

```python
plot_state_pop_tracker(state_pop_tracker)
compare_scenarios(state_pop_tracker, state_pop_tracker_new, CHARGED, "5 percent increase in crime rate")
```

## Scenarios
You can modify crime rates or processing speeds to evaluate different policy impacts. For instance, increasing the crime rate by 5% changes the influx of new cases and affects case backlog dynamics.


