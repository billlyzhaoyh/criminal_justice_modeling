import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import simpy

# Define processing time distributions (Mean and Standard Deviation in days)
processing_times = {
    "U": (10, 2),  # Under investigation
    "C": (5, 1),  # Charging decision
    "Mb": (15, 3),  # Magistrate Court Backlog
    "M": (7, 2),  # Magistrate Court Processing
    "Cb": (20, 5),  # Crown Court Backlog
    "Cc": (30, 7),  # Crown Court Processing
    "P": (180, 30),  # Prison sentence duration
}

# System Capacity Constraints
NUM_POLICE = 5
NUM_MAGISTRATE_JUDGES = 3
NUM_CROWN_JUDGES = 2
PRISON_CAPACITY = 500

# Data collection structures
case_data = []
prison_population = []


class JusticeSystem:
    def __init__(self, env):
        self.env = env
        self.police = simpy.Resource(env, capacity=NUM_POLICE)
        self.magistrate_court = simpy.Resource(env, capacity=NUM_MAGISTRATE_JUDGES)
        self.crown_court = simpy.Resource(env, capacity=NUM_CROWN_JUDGES)
        self.prison = simpy.Container(env, init=0, capacity=PRISON_CAPACITY)

    def process_stage(self, stage, case_id):
        """Simulate a processing stage with random duration."""
        duration = np.random.normal(*processing_times[stage])
        yield self.env.timeout(max(1, duration))
        return np.random.rand()  # Random chance to proceed


def case_process(env, case_id, justice_system):
    """Simulates the lifecycle of a case through the justice system."""
    entry_time = env.now
    log = {"case_id": case_id, "start_time": entry_time, "end_time": None}

    stages = ["U", "C", "Mb", "M", "Cb", "Cc", "P"]
    probabilities = [
        0.8,
        0.7,
        0.6,
        0.5,
        0.7,
        0.8,
        1.0,
    ]  # Chance to proceed at each stage

    for i, stage in enumerate(stages):
        start = env.now
        move_forward = yield env.process(justice_system.process_stage(stage, case_id))
        end = env.now

        log[f"{stage}_start"] = start
        log[f"{stage}_end"] = end
        log[f"{stage}_duration"] = end - start

        if move_forward > probabilities[i]:  # Case dismissed at this stage
            log["dismissed_at"] = stage
            log["end_time"] = end
            case_data.append(log)
            return

        if stage == "P":  # Entering prison
            justice_system.prison.put(1)
            prison_population.append((env.now, justice_system.prison.level))
            yield env.timeout(np.random.normal(*processing_times["P"]))
            justice_system.prison.get(1)
            prison_population.append((env.now, justice_system.prison.level))

    log["end_time"] = env.now
    case_data.append(log)  # <- This now executes


# **FIXED Simulation setup**
def run_simulation(num_cases=100, simulation_time=1000):
    env = simpy.Environment()
    justice_system = JusticeSystem(env)

    # Generate case processes
    for i in range(num_cases):
        env.process(case_process(env, i, justice_system))
        env.timeout(np.random.exponential(scale=5))  # No `yield` here!

    env.run(until=simulation_time)  # Run simulation


# **Run the fixed simulation**
run_simulation()

# **Check collected data**
if not case_data:
    print("Error: No case data was collected!")
else:
    print(f"Collected data for {len(case_data)} cases.")

# **Convert collected data into Pandas DataFrame**
df = pd.DataFrame(case_data)

# **Compute total case duration**
df["total_duration"] = df["end_time"] - df["start_time"]

# **Summary statistics**
print("Summary Statistics:")
print(df.describe())

# **Visualization**
plt.figure(figsize=(10, 5))
plt.hist(df["total_duration"], bins=20, alpha=0.7, color="b", edgecolor="black")
plt.xlabel("Total Case Duration (Days)")
plt.ylabel("Number of Cases")
plt.title("Distribution of Total Case Duration")
plt.show()
