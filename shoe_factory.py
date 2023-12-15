# class ShoeFactory:
#     init:
#         Make environment
#         create structure of the ShoeFactory:
#             Make job Generator
#             make queues
#             make job sink
#             link instances
#     run:
#         start job Generator
#         start statistics job
#         run environment

# class JobGenerator:


# class MM1Queue:

import simpy
import random
import statistics

NUM_QUEUES = 7

queue_times = {}
system_time_list = []

discarded_jobs = {}
for i in range(NUM_QUEUES):
    discarded_jobs[i] = 0

class MMCKQueue:
    def __init__(self, env, queue_id, num_servers, max_queue_size, service_rate, arrival_rate=None, output_queues=[], self_feedback=False, customer_start_id=1):
        self.env = env
        self.queue_id = queue_id
        self.num_servers = num_servers
        self.max_queue_size = max_queue_size
        self.output_queues = output_queues
        self.start_queue = False
        self.end_queue = False
        self.self_feedback = self_feedback


        self.queue = simpy.Store(env, capacity=max_queue_size)
        self.servers = simpy.Resource(env, capacity=num_servers)

        self.service_rate = service_rate
        for _ in range(num_servers+2): # Resources limited by servers, not calls to service_process
            self.env.process(self.service_process())
        
        if arrival_rate != None:
            self.start_queue = True
            self.arrival_rate = arrival_rate
            self.env.process(self.arrival_process(customer_start_id))
        if len(output_queues) == 0:
            self.end_queue = True
        if self.self_feedback:
            self.output_queues.append(self)
        print(f"Queue {self.queue_id} Parameters:\n" \
               f" - Environment: {self.env}\n" \
               f" - Number of Servers: {self.num_servers}\n" \
               f" - Max Queue Size: {self.max_queue_size}\n" \
               f" - Output Queues: {self.output_queues}\n" \
               f" - Start Queue: {self.start_queue}\n" \
               f" - End Queue: {self.end_queue}")

    def arrival_process(self, customer_id=1):
        while True:
            inter_arrival_time = random.expovariate(self.arrival_rate)
            yield self.env.timeout(inter_arrival_time)
            self.customer(customer_id)
            #print(f"Customer {customer_id:04} entered the system at time {self.env.now:0.2f}")
            queue_times[customer_id] = [round(self.env.now, 2)]
            customer_id += 1

    def arrival_from_other_queue(self, customer_id):   
        #print("Queue", self.queue_id, "recieved customer", customer_id) 
        self.customer(customer_id)
        
    def service_process(self):
        while True:
            customer = yield self.queue.get()
            with self.servers.request() as request:
                yield request
                service_time = random.expovariate(self.service_rate)
                yield self.env.timeout(service_time)
                queue_times[customer].append(round(self.env.now, 2))
                if not self.end_queue:
                    destination = random.choice(self.output_queues)
                    destination.arrival_from_other_queue(customer)
                else:
                    system_time = round(self.env.now, 2)-queue_times[customer][0]
                    system_time_list.append(system_time)
                    #print(f"Customer {customer:04}    left the system at time {self.env.now:0.2f} and spent {system_time:0.2f} in the system")

                    
    def customer(self, customer_id):
        if len(self.queue.items) < self.max_queue_size:
            self.queue.put(customer_id)
        else:
            discarded_jobs[self.queue_id] += 1
            #print(f"Customer {customer_id} leaves - Queue is full.")

    def customer_statistics(self, customer):
        print("Queue", self.queue_id, "processed customer", customer)

def present_stats():
    print("Queue element times:")
    for key, value in queue_times.items():
        print(f"{key:06}: {value}")

    # print("\nList:")
    # print(system_time_list)
    steady_state_buffer = 1000 # Samples to be removed because the system hasnt reached steady state yet.
    average = statistics.mean(system_time_list[steady_state_buffer:])
    std_deviation = statistics.stdev(system_time_list[steady_state_buffer:])

    print("\nStatistics:")
    for key, value in discarded_jobs.items():
        print(f"Discarded jobs from queue {key}: {value}")

    print(f"Processed jobs: {len(system_time_list)}")
    print(f"Average: {average}")
    print(f"Standard Deviation: {std_deviation}")

def shoe_factory(arrival_rates, service_rates, queue_sizes, num_server_list, sim_duration):
    env = simpy.Environment()
    queue6 = MMCKQueue(env, 6, num_server_list[6], queue_sizes[6], service_rates[6])
    queue5 = MMCKQueue(env, 5, num_server_list[5], queue_sizes[5], service_rates[5], output_queues=[queue6])
    queue4 = MMCKQueue(env, 4, num_server_list[4], queue_sizes[4], service_rates[4], output_queues=[queue5])
    queue3 = MMCKQueue(env, 3, num_server_list[3], queue_sizes[3], service_rates[3], output_queues=[queue4], self_feedback=True)
    queue2 = MMCKQueue(env, 2, num_server_list[2], queue_sizes[2], service_rates[2], output_queues=[queue3])
    queue1 = MMCKQueue(env, 1, num_server_list[1], queue_sizes[1], service_rates[1], output_queues=[queue3], arrival_rate=arrival_rates[1], customer_start_id=100000)
    queue0 = MMCKQueue(env, 0, num_server_list[0], queue_sizes[0], service_rates[0], output_queues=[queue2], arrival_rate=arrival_rates[0])
    env.run(until=sim_duration)
    present_stats()
    





if __name__ == "__main__":
    arrival_rates = [1/30, 1/30]
    service_rates = [1/31.59, 1/22.02, 1/19.81, 1/55.04, 1/18.93, 1/29.28, 1/28.62]
    queue_sizes = [100, 100, 100, 100, 100, 100, 100]
    num_servers = [2, 2, 2, 12, 2, 2, 2]
    sim_duration = 100000
    shoe_factory(arrival_rates, service_rates, queue_sizes, num_servers, sim_duration)