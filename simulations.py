import random
import simpy
import numpy as np
import matplotlib.pyplot as plt

class MMinfQueue:
    def __init__(self, arrival_rate, service_rate, num_customers):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.num_customers = num_customers
        self.env = simpy.Environment()
        self.queue = simpy.Store(self.env)
        self.server = simpy.Resource(self.env, capacity=1000000) # infinite capacity
        self.queue_lengths = []
        self.done = False
        self.rng = np.random.default_rng()

    def customer_arrival(self):
        for i in range(self.num_customers):
            yield self.env.timeout(self.rng.poisson(1/self.arrival_rate))
            self.env.process(self.customer_service())
        self.done = True

    def customer_service(self):
        with self.server.request() as request:
            yield request
            yield self.env.timeout(self.rng.exponential(1/self.service_rate))

    def run_simulation(self):
        self.env.process(self.customer_arrival())
        self.env.process(self.stats_processing())
        self.env.run()
    
    # def run_simulation(self, sim_time):
    #     self.env.process(self.arrival_process())
    #     self.env.run(until=sim_time)

    def stats_processing(self):
        # yield self.env.timeout(100)
        while not self.done:
            self.queue_lengths.append(self.server.count)
            # print(f'{self.server.count} of {self.server.capacity} slots are allocated.')
            # print(f'  Users: {len(res.users)}')
            # print(f'  Queued events: {len(res.queue)}')
            yield self.env.timeout(0.1)
        print("Simulation complete")
        print(f'Average queue length: {np.mean(self.queue_lengths)}')
        graph_queue_lengths(self.queue_lengths)

def graph_queue_lengths(queue_lengths):
    x = [i*0.1 for i in range(len(queue_lengths))]
    plt.plot(x, queue_lengths)
    plt.show()

# Example usage
if __name__ == "__main__":
    arrival_rate = 10  # average arrival rate of customers per unit of time
    service_rate = 1  # average service rate of the server per unit of time
    num_customers = 10000  # total number of customers to simulate

    queue = MMinfQueue(arrival_rate, service_rate, num_customers)
    queue.run_simulation()
