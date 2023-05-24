import random, numpy as np, pandas as pd
import simpy
import statistics
import streamlit as st
import matplotlib.pyplot as plt

wait_times = []
cashier_line = []

# Determine the average time a moviegoer goes from entering
# the theater to sitting down to watch a movie
class Theater(object):
    # A moviegoer goes to the cashier and buys a ticket
    # Before moving on, he might stop by and by some snacks (servers)
    # Lastly, an usher checks his ticket
    def __init__(self,env,num_cashiers, num_servers, num_ushers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)
        self.server = simpy.Resource(env, num_servers)
        self.usher = simpy.Resource(env, num_ushers)
    
    def purchase_ticket(self, moviegoer):
        # Ticket purchases take on average 1-3 min.
        yield self.env.timeout(random.randint(1,3))
    
    def check_ticket(self,moviegoer):
        # Checking tickets takes on average 3 sec.
        yield self.env.timeout(3/60)
    
    def sell_food(self,moviegoer):
        # An order at the servers takes on average 1-5 min.
        yield self.env.timeout(random.randint(1,5))

def go_to_movies(env, moviegoer, theater):
    # Moviegoer arrives at the theater
    arrival_time = env.now
    # The param. 'theater' gives access to the
    # overall class definition

    # Generate a request to use a cashier
    with theater.cashier.request() as request:
        yield request # moviegoer waits for a cashier if all are currently in use
        yield env.process(theater.purchase_ticket(moviegoer)) 
        # ^ moviegoer uses an available cashier to complete the given process (purchase a ticket)
    
    with theater.usher.request() as request:
        yield request
        yield env.process(theater.check_ticket(moviegoer))
    
    # We can't know if a moviegoer wants snacks, so we use a random selection
    if random.choice([True, False]):
        with theater.server.request() as request:
            yield request
            yield env.process(theater.sell_food(moviegoer))
    
    # Update the cashier line
    cashier_line.append((env.now,len(theater.cashier.queue))) 

    #Moviegoer heads into the theater
    wait_times.append(env.now - arrival_time)
    
def run_theater(env, num_cashiers, num_servers, num_ushers):
    theater = Theater(env, num_cashiers, num_servers, num_ushers)

    # Assume there are 3 moviegoers waiting in line for the box office to open
    for moviegoer in range(3):
        env.process(go_to_movies(env,moviegoer,theater))

    while True:
        # A moviegoer then arrives every 6 sec.
        yield env.timeout(0.10)
        moviegoer += 1
        env.process(go_to_movies(env,moviegoer,theater))
    
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

def get_user_input():
    num_cashiers = input("Input # of cashiers working: ")
    num_servers = input("Input # of servers working: ")
    num_ushers = input("Input # of ushers working: ")
    params = [num_cashiers, num_servers, num_ushers]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. The simulation will use default values:",
            "\n1 cashier, 1 server, 1 usher.",
        )
        params = [1, 1, 1]
    return params

def main():
    st.write("# Theater simulation")
    "We first specify the number of cashiers, servers and ushers:"
    
    #Setup environment
    random.seed(42)
    num_cashiers, num_servers, num_ushers = get_user_input()

    'Cashiers:', num_cashiers
    'Servers:', num_servers
    'Ushers:', num_ushers

    #Create environment run the simulation
    env = simpy.Environment()
    env.process(run_theater(env, num_cashiers, num_servers, num_ushers))

    # List to store the number of people waiting at each minute
    cashier_line.append((0,3)) # Initially 3 are in line

    # Determine how long you want the simulation to run.
    env.run(until=90) # 90 min

    # Results
    min, sec = get_average_wait_time(wait_times)
    print(
        "Running simulation...",
        f"\nThe average wait time is {min} minutes and {sec} seconds."
    )

    x,y=zip(*cashier_line)

    # Visualize the data
    fig, ax = plt.subplots()
    ax.plot(x,y)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("People in queue")
    ax.set_title("Cashier queue")
    st.pyplot(fig)

# Invoke main function 
if __name__ == '__main__':
    main()

