import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def draw_number_of_days(mean):
    # Define mean and standard deviation
    sigma = mean/3  # Standard deviation
    # Draw a single random number
    random_number = np.random.normal(mean, sigma)
    final_days = round(random_number)
    if final_days <= 1:
        final_days = 1
    return final_days

UNDER_INVESTIGATION = "under_investigation"
CHARGED = "charged"
MC_BACKLOG = "mc_backlog"
IN_MC = "in_mc"
CC_BACKLOG = "cc_backlog"
IN_CC = "in_cc"
CONVICTED = "convicted"
IMPRISONED = "imprisoned"
DISMISSED = "dismissed"

agent_states = [UNDER_INVESTIGATION, CHARGED, MC_BACKLOG, IN_MC, CC_BACKLOG, CC_BACKLOG, IN_CC, CONVICTED, IMPRISONED, DISMISSED]

# Settings
investigation_to_charged_prob = 0.19
mc_to_cc_prob = 0.04
mc_to_conviction_prob = 0.85
mc_to_dismissal_prob = 0.11
cc_to_conviction_prob = 0.91

# Ensure probabilities sum to 1
assert round(mc_to_cc_prob + mc_to_conviction_prob + mc_to_dismissal_prob, 5) == 1, "Probabilities must sum to 1"

# let's assume std is mean/3
mean_days_to_spend_in_state = {
    UNDER_INVESTIGATION: 30,
    CHARGED: 1,
    MC_BACKLOG: 36,
    IN_MC: 19,
    CC_BACKLOG: 353,
    IN_CC: 164, 
    CONVICTED: 1,
    DISMISSED: 999999,
    IMPRISONED: 18,
}

class Agent:
    def __init__(self, agent_id, initial_agent_state):
        self.agent_id = agent_id
        self.initial_agent_state = initial_agent_state
        self.current_agent_state = initial_agent_state
        self.next_agent_state = None
        self.days_to_spend_in_current_state = None
        self.days_left_in_current_state = None
        self.set_days_to_spend_in_current_state()
        self.set_next_agent_state()
        
    def __repr__(self):
        return f"Agent(agent_id={self.agent_id!r}, initial_agent_state={self.initial_agent_state!r})"

    def __str__(self):
        return f"current state: {self.current_agent_state}, next state: {self.next_agent_state}, days left in current state: {self.days_left_in_current_state}"
    
    def set_next_agent_state(self):
        # transition probabilities
        if self.current_agent_state == UNDER_INVESTIGATION:
            if random.random() <= investigation_to_charged_prob:
                self.next_agent_state = CHARGED
            else:
                self.next_agent_state = DISMISSED
        if self.current_agent_state == CHARGED:
            self.next_agent_state = MC_BACKLOG
        if self.current_agent_state == MC_BACKLOG:
            self.next_agent_state = IN_MC
        if self.current_agent_state == IN_MC:
            outcome = random.choices(
                [CC_BACKLOG, CONVICTED, DISMISSED],
                weights=[mc_to_cc_prob, mc_to_conviction_prob, mc_to_dismissal_prob]
            )[0]
            self.next_agent_state = outcome
        if self.current_agent_state == CC_BACKLOG:
            self.next_agent_state = IN_CC
        if self.current_agent_state == IN_CC:
            if random.random() <= cc_to_conviction_prob:
                self.next_agent_state = CONVICTED
            else:
                self.next_agent_state = DISMISSED
        if self.current_agent_state == CONVICTED:
            self.next_agent_state = IMPRISONED
        if self.current_agent_state == IMPRISONED:
            self.next_agent_state = DISMISSED
    
    def set_days_to_spend_in_current_state(self):
        self.days_to_spend_in_current_state = draw_number_of_days(mean_days_to_spend_in_state[self.current_agent_state])
        self.days_left_in_current_state = self.days_to_spend_in_current_state


def make_initial_population(N):
    # start the year with the right backlog   
    # MC_BACKLOG: 337,632
    # CC_BACKLOG: 62,207
    # IMPRISONED: 87,869
    # divide the three states above by the proportion
    totoal_population = 337632 + 62207 + 87869
    mc_backlog_proportion = 337632 / totoal_population
    cc_backlog_proportion = 62207 / totoal_population
    imprisoned_proportion = 87869 / totoal_population
    # total_number_of_new_comers_daily = round(((6657518/487708) * N)/365) * mean_days_to_spend_in_state[UNDER_INVESTIGATION] # steady state estimate of under investigation
    mc_backlog_N = round(mc_backlog_proportion * N)
    cc_backlog_N = round(cc_backlog_proportion * N)
    imprisoned_N = round(imprisoned_proportion * N)
    population = [Agent(agent_id=i, initial_agent_state=MC_BACKLOG) for i in range(mc_backlog_N)]
    population += [Agent(agent_id=i, initial_agent_state=CC_BACKLOG) for i in range(cc_backlog_N)]
    population += [Agent(agent_id=i, initial_agent_state=IMPRISONED) for i in range(imprisoned_N)]
    # population += [Agent(agent_id=i, initial_agent_state=UNDER_INVESTIGATION) for i in range(total_number_of_new_comers_daily)]
    return population
    

def simulate(n, k, total_number_of_new_comers_daily):
    """simulate n agents for k time steps"""
    population = make_initial_population(n)
    # print("Initial Population:", population)
    state_pop_tracker = []
    for i in range(k):
        # add number of people being investigated assuming people come in evenly per day
        population += [Agent(agent_id=i, initial_agent_state=UNDER_INVESTIGATION) for i in range(total_number_of_new_comers_daily)]
        spread_of_agents_among_states = {state: 0 for state in agent_states}
        for agent in population:
            agent.days_left_in_current_state -= 1
            if agent.days_left_in_current_state == 0:
                agent.current_agent_state = agent.next_agent_state
                agent.set_days_to_spend_in_current_state()
                agent.set_next_agent_state()
            spread_of_agents_among_states[agent.current_agent_state] += 1
        state_pop_tracker.append(spread_of_agents_among_states)
        # population += [Agent(agent_id=i, initial_agent_state=UNDER_INVESTIGATION) for i in range(total_number_of_new_comers_daily)]
    return population, state_pop_tracker


def plot_state_pop_tracker(state_pop_tracker):
    # Convert list of dicts to DataFrame
    df = pd.DataFrame(state_pop_tracker)
    # Plot each column as a separate line
    plt.figure(figsize=(10, 5))
    for column in df.columns:
        if column != DISMISSED:
            plt.plot(df.index, df[column], label=column)
    plt.xlabel('Days since end of FY24')
    plt.ylabel('Case count')
    plt.title('Agent based modeling over the next two financial year impact')
    # Add vertical lines at end of FY1 and FY2
    fy1_marker = plt.axvline(x=365, color='black', linestyle='--', label="End of FY25")
    fy2_marker = plt.axvline(x=730, color='red', linestyle='--', label="End of FY26")
    # Get current axis
    ax = plt.gca()
    # First legend (main legend for the graph)
    main_legend = ax.legend(loc="upper right")  # Adjust position if needed
    # Second legend (for fiscal year markers)
    fy_legend = ax.legend(handles=[fy1_marker, fy2_marker], loc="lower right", title="Fiscal Year Markers")
    # Add the main legend back to the plot
    ax.add_artist(main_legend)
    plt.grid(True)
    plt.show()

def compare_scenarios(state_pop_tracker_1, state_pop_tracker_2, dimension, label):
    state_pop_tracker_1_df = pd.DataFrame(state_pop_tracker_1)
    state_pop_tracker_2_df = pd.DataFrame(state_pop_tracker_2)
    plt.figure(figsize=(10, 5))
    plt.plot(state_pop_tracker_1_df.index, state_pop_tracker_1_df[dimension], label="BAU")
    plt.plot(state_pop_tracker_2_df.index, state_pop_tracker_2_df[dimension], label=label)
    plt.xlabel('Days since end of FY24')
    plt.ylabel('Case count')
    plt.title('Agent based modeling over the next two financial year impact comparing scenarios')
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()
    


if __name__ == "__main__":
    num_existing_cases = 10000
    num_days = 730
    total_number_of_new_comers_daily = round(((6657518/487708) * num_existing_cases)/365)
    final_population, state_pop_tracker = simulate(num_existing_cases, num_days, total_number_of_new_comers_daily)
    plot_state_pop_tracker(state_pop_tracker)
    # secenario where we increase the crime rate by 5%
    total_number_of_new_comers_daily_new = round(((6657518/487708) * num_existing_cases)/365 * 1.05)
    print(f"increasing new cases daily from {total_number_of_new_comers_daily} to {total_number_of_new_comers_daily_new}")
    final_population_new, state_pop_tracker_new = simulate(num_existing_cases, num_days, total_number_of_new_comers_daily_new)
    # plot the increase in charges and convictions
    compare_scenarios(state_pop_tracker, state_pop_tracker_new, CHARGED, "5 percent increase in crime rate")
