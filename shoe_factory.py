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

NUM_QUEUES = 7

class MMCKQueue:
    def __init__(self, env, queue_id, num_servers, max_queue_size, service_rate, arrival_rate=None, output_queues=[], self_feedback=False):
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
        self.env.process(self.service_process())
        
        if arrival_rate != None:
            self.start_queue = True
            self.arrival_rate = arrival_rate
            self.env.process(self.arrival_process())
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

    def arrival_process(self):
        customer_id = 1
        while True:
            inter_arrival_time = random.expovariate(self.arrival_rate)
            yield self.env.timeout(inter_arrival_time)
            self.customer(customer_id)
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
                if not self.end_queue:
                    destination = random.choice(self.output_queues)
                    destination.arrival_from_other_queue(customer)
                    print("Queue", self.queue_id, "processed customer", customer, "and sent it to queue", destination.queue_id)

                
                #self.customer_statistics(customer)
                    
    def customer(self, customer_id):
        if len(self.queue.items) < self.max_queue_size:
            self.queue.put(customer_id)
        else:
            print(f"Customer {customer_id} leaves - Queue is full.")

    def customer_statistics(self, customer):
        print("Queue", self.queue_id, "processed customer", customer)


def shoe_factory(arrival_rates, service_rates, queue_sizes, num_server_list, sim_duration):
    env = simpy.Environment()
    queue6 = MMCKQueue(env, 6, num_server_list[6], queue_sizes[6], service_rates[6])
    queue5 = MMCKQueue(env, 5, num_server_list[5], queue_sizes[5], service_rates[5], output_queues=[queue6])
    queue4 = MMCKQueue(env, 4, num_server_list[4], queue_sizes[4], service_rates[4], output_queues=[queue5])
    queue3 = MMCKQueue(env, 3, num_server_list[3], queue_sizes[3], service_rates[3], output_queues=[queue4], self_feedback=True)
    queue2 = MMCKQueue(env, 2, num_server_list[2], queue_sizes[2], service_rates[2], output_queues=[queue3])
    queue1 = MMCKQueue(env, 1, num_server_list[1], queue_sizes[1], service_rates[1], output_queues=[queue3], arrival_rate=arrival_rates[1])
    queue0 = MMCKQueue(env, 0, num_server_list[0], queue_sizes[0], service_rates[0], output_queues=[queue2], arrival_rate=arrival_rates[0])
    env.run(until=sim_duration)
    





if __name__ == "__main__":
    arrival_rates = [1/20, 1/20]
    service_rates = [1/31.59, 1/22.02, 1/19.81, 1/55.04, 1/18.93, 1/29.28, 1/28.62]
    queue_sizes = [100, 100, 100, 100, 100, 100, 100]
    num_servers = [2, 2, 2, 4, 2, 2, 2]
    sim_duration = 10000
    shoe_factory(arrival_rates, service_rates, queue_sizes, num_servers, sim_duration)