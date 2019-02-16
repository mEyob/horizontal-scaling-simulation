from server_resources import Server, Worker, Queue

class ScalingGroup():
    def __init__(self, min_servers, starting_num, max_servers, launch_delay, num_of_workers, worker_capacity):
        self.min_servers = min_servers
        self.max_servers = max_servers
        self.launch_delay = launch_delay
        self.workers_per_server = num_of_workers
        self.worker_capacity = worker_capacity
        self.scaling_group = {}
        for _ in range(starting_num):
            new_server = Server(launch_delay, num_of_workers, worker_capacity) 
            self.scaling_group[new_server.rsc_id] = new_server
