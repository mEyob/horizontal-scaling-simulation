from collections import namedtuple
from server_resources import Server, Worker, Queue

Event = namedtuple('Event', 'rsc rsc_id type ev_time')

class ScalingGroup():
    rsc_id = 'SG'
    def __init__(self, min_servers, starting_num, max_servers, server_cost_rate, launch_delay, num_of_workers, worker_capacity, avg_job_size, estimation_interval, scaling_period):
        self.min_servers = min_servers
        self.max_servers = max_servers
        self.launch_delay = launch_delay
        self.workers_per_server = num_of_workers
        self.worker_capacity = worker_capacity
        self.worker_service_rate = worker_capacity / avg_job_size
        self.scaling_group = {}
        for _ in range(starting_num):
            new_server = Server(launch_delay, server_cost_rate, num_of_workers, worker_capacity, avg_job_size) 
            self.scaling_group[new_server.rsc_id] = new_server
        self.estimation_interval = estimation_interval
        self.scaling_period = scaling_period
        self.target_load = 0.5
        self.threshold = 0.1
        self.job_count = 0
    def event_handler(self, event):
        if event.type == 'start_estimation':
            self.period = 'est_period'
            self.job_count = 0
            event = Event('scaling_group', ScalingGroup.rsc_id, 'start_scaling', event.ev_time + self.estimation_interval)
        elif event.type == 'start_scaling':
            self.autoscale()
            event = Event('scaling_group', ScalingGroup.rsc_id, 'start_estimation', event.ev_time + self.scaling_period)
        return event
    def autoscale(self):
        est_load, est_arrival_rate, active_num_servers = self.estimate()
        target_num_servers = round(est_arrival_rate / (self.target_load * self.workers_per_server * self.worker_service_rate))
        if est_load > self.target_load + self.threshold:
            # system overloaded
            if target_num_servers < self.max_servers: # if there are any servers to be started
                self.scaleup(target_num_servers - active_num_servers)
            elif active_num_servers < self.max_servers:
                self.scaleup(self.max_servers - active_num_servers)
        elif est_load < self.target_load - self.threshold:
            # system underloaded
            self.scaledown(active_num_servers - target_num_servers)
        print(est_load - self.target_load)

    def estimate(self):
        est_arrival_rate = self.job_count / self.estimation_interval
        active_num_servers = sum([1 for server in self.scaling_group.values() if server.state in ['launching', 'ready']])
        est_load = est_arrival_rate / (active_num_servers * self.workers_per_server * self.worker_service_rate)
        return est_load, est_arrival_rate, active_num_servers
    def scaleup(self, num_of_servers):
        print('scale_up')
        pass
    def scaledown(self, num_of_servers):
        print('scale_down')
        pass

