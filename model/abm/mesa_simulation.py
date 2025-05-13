import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mesa import Agent, Model
from mesa.agent import AgentSet
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

# Define processing time distributions (Mean and Std Dev in days)
processing_times = {
    "U": (10, 2),
    "C": (5, 1),
    "Mb": (15, 3),
    "M": (7, 2),
    "Cb": (20, 5),
    "Cc": (30, 7),
    "P": (180, 30),
}

# Define system capacities
NUM_POLICE = 5
NUM_MAGISTRATE_JUDGES = 3
NUM_CROWN_JUDGES = 2
PRISON_CAPACITY = 500

# Probabilities of moving forward at each stage
transition_probabilities = {
    "U": 0.8,
    "C": 0.7,
    "Mb": 0.6,
    "M": 0.5,
    "Cb": 0.7,
    "Cc": 0.8,
    "P": 1.0,
}


class Case(Agent):
    """An individual case moving through the justice system."""

    def __init__(self, model):
        super().__init__(model=model)
        self.state = "U"
        self.start_time = model.schedule.time
        self.end_time = None

    def step(self):
        """Progress case through the justice system."""
        if self.state in processing_times:
            # Simulate time spent in the current state
            mean, std = processing_times[self.state]
            time_spent = max(1, np.random.normal(mean, std))

            # Decide whether to proceed or be dismissed
            if np.random.rand() > transition_probabilities[self.state]:
                self.state = "D"
                self.end_time = self.model.schedule.time + time_spent
                return

            # Transition to the next stage
            transitions = ["U", "C", "Mb", "M", "Cb", "Cc", "P", "D"]
            next_state_index = transitions.index(self.state) + 1
            if next_state_index < len(transitions):
                self.state = transitions[next_state_index]

            # If imprisoned, check prison capacity
            if self.state == "P":
                if self.model.prison_population < PRISON_CAPACITY:
                    self.model.prison_population += 1
                else:
                    self.state = "D"

        # Record end time if case is completed or dismissed
        if self.state in ["P", "D"]:
            self.end_time = self.model.schedule.time


class JusticeSystemModel(Model):
    """Agent-Based Model of the justice system."""

    def __init__(self, num_cases=100, max_steps=500):
        super().__init__()
        self.num_cases = num_cases
        self.max_steps = max_steps
        self.prison_population = 0

        # ✅ FIX: Define a reproducible random number generator
        self.rng = np.random.default_rng(seed=42)

        # ✅ FIX: Initialize `AgentSet` properly with an empty list
        # self.schedule = AgentSet(agents=[], random=self.rng)
        self.schedule = RandomActivation(self)

        # Create cases and add them to AgentSet
        for i in range(num_cases):
            case = Case(model=self)
            self.schedule.add(case)

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={"Prison Population": lambda m: m.prison_population},
            agent_reporters={
                "State": "state",
                "Start Time": "start_time",
                "End Time": "end_time",
            },
        )

    def step(self):
        """Advance simulation by one time step."""
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self):
        """Run the simulation until max_steps is reached or all cases are completed."""
        for _ in range(self.max_steps):
            self.step()
            if all(agent.state in ["P", "D"] for agent in self.schedule.agents):
                break  # Stop simulation if all cases are resolved


# **Run the ABM simulation**
justice_model = JusticeSystemModel(num_cases=100, max_steps=500)
justice_model.run_model()

# **Collect and analyze results**
model_data = justice_model.datacollector.get_model_vars_dataframe()
agent_data = justice_model.datacollector.get_agent_vars_dataframe()

# Convert to Pandas DataFrame
df_agents = agent_data.reset_index()
print(df_agents.columns)
# Compute total case duration
df_agents["Total Duration"] = df_agents["End Time"] - df_agents["Start Time"]

# Print summary statistics
print("Summary Statistics:")
print(df_agents[["Total Duration"]].describe())

# **Plot Case Completion Times**
plt.figure(figsize=(10, 5))
plt.hist(
    df_agents["Total Duration"].dropna(),
    bins=30,
    alpha=0.7,
    color="blue",
    edgecolor="black",
)
plt.xlabel("Total Case Duration (Days)")
plt.ylabel("Number of Cases")
plt.title("Distribution of Case Completion Times in ABM")
plt.show()

# **Plot Final Case Outcomes**
outcomes = df_agents["State"].value_counts()
plt.figure(figsize=(10, 5))
outcomes.plot(kind="bar", color="red", edgecolor="black", alpha=0.7)
plt.xlabel("Final Outcome")
plt.ylabel("Number of Cases")
plt.title("Final Case Outcomes in the Justice System")
plt.xticks(rotation=45)
plt.show()

# **Plot Prison Population Over Time**
plt.figure(figsize=(10, 5))
plt.plot(
    model_data.index,
    model_data["Prison Population"],
    label="Prison Population",
    color="purple",
)
plt.xlabel("Simulation Time Steps")
plt.ylabel("Number of Prisoners")
plt.title("Prison Population Over Time in the Justice System")
plt.legend()
plt.show()
