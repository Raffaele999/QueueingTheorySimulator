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

NUM_QUEUES = 7

class ShoeFactory:
    def __init__(self, arrival_rate, service_rate, num_customers):
        if len(arrival_rate) != NUM_QUEUES or len(service_rate) != NUM_QUEUES:
            throw error
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.num_customers = num_customers
        self.env = simpy.Environment()
        self.queue = simpy.Store(self.env)
        self.server = simpy.Resource(self.env, capacity=1000000) # infinite capacity
        self.queue_lengths = []
        self.done = False
        self.rng = np.random.default_rng()