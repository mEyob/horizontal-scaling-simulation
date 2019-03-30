import random
from heapq import nsmallest
from collections import namedtuple
from server_resources import Server, Worker, Queue

Event = namedtuple('Event', 'rsc rsc_id type ev_time')

class ScalingGroup():
    rsc_id = 'SG'
    def __init__(self, min_servers, starting_num, max_servers, target_load, server_cost_rate, launch_delay, num_of_workers, worker_capacity, avg_job_size, estimation_interval, scaling_period, transient):
        self.min_servers = min_servers
        self.max_servers = max_servers
        self.launch_delay = launch_delay
        self.workers_per_server = num_of_workers
        self.worker_capacity = worker_capacity
        self.worker_service_rate = worker_capacity / avg_job_size
        self.scaling_group = {}
        for _ in range(max_servers):
            new_server = Server(launch_delay, server_cost_rate, num_of_workers, worker_capacity, avg_job_size) 
            self.scaling_group[new_server.rsc_id] = new_server
        self.estimation_interval = estimation_interval
        self.scaling_period = scaling_period
        self.transient = transient
        self.target_load = target_load
        self.threshold = 0.1
        self.job_count = 0
    def event_handler(self, event):
        if event.type == 'start_estimation':
            self.period = 'est_period'
            self.job_count = 0
            event = [Event('scaling_group', ScalingGroup.rsc_id, 'start_scaling', event.ev_time + self.estimation_interval)]
        elif event.type == 'start_scaling':
            events = []
            if event.ev_time > self.transient:
                events = self.autoscale(event.ev_time)
            event = [Event('scaling_group', ScalingGroup.rsc_id, 'start_estimation', event.ev_time + self.scaling_period)]
            if events:
                event.extend(events)
        return event
    def autoscale(self, current_time):
        est_load, est_arrival_rate, active_num_servers = self.estimate()
        target_num_servers = round(est_arrival_rate / (self.target_load * self.workers_per_server * self.worker_service_rate))
        events = []
        if (est_load > self.target_load + self.threshold) and (target_num_servers > active_num_servers):
            # system overloaded
            if target_num_servers < self.max_servers: # if there are any servers to be started
                events = self.scaleup(target_num_servers - active_num_servers, current_time)
            elif active_num_servers < self.max_servers:
                events = self.scaleup(self.max_servers - active_num_servers, current_time)
        elif (est_load < self.target_load - self.threshold) and active_num_servers > self.min_servers:
            if active_num_servers > target_num_servers:
            # system underloaded
                servers_to_stop = min([active_num_servers - target_num_servers, active_num_servers - self.min_servers])
                self.scaledown(servers_to_stop, current_time)
        return events             

    def estimate(self):
        est_arrival_rate = self.job_count / self.estimation_interval
        active_num_servers = sum([1 for server in self.scaling_group.values() if server.state in ['busy', 'idle']])
        est_load = est_arrival_rate / (active_num_servers * self.workers_per_server * self.worker_service_rate)
        return est_load, est_arrival_rate, active_num_servers

    def scaleup(self, num_of_servers, current_time):
        stopped_servers = [server.rsc_id for server in self.scaling_group.values() if server.state == 'stopped']
        events = []
        for _ in range(num_of_servers):
            if stopped_servers:
                server_id = random.choice(stopped_servers)
                launch_event = self.scaling_group[server_id].start(current_time)
                events.append(launch_event)
                stopped_servers.remove(server_id)
        return events

    def scaledown(self, num_of_servers, current_time):
        target_servers = [server for server in self.scaling_group.values() if server.state in ['idle']]
        if len(target_servers) >= num_of_servers:
            for _ in range(num_of_servers):
                server = random.choice(target_servers)
                server.stop(current_time)
                target_servers.remove(server)
        else:
            if target_servers:
                for server in target_servers:
                    server.stop(current_time)
            server_queue_tup = [(server.queue.queue_length(), server.rsc_id) for server in self.scaling_group.values()]
            to_be_stopped = nsmallest(num_of_servers - len(target_servers), server_queue_tup, key=lambda x: x[0])
            for _, rsc_id in to_be_stopped:
                self.scaling_group[rsc_id].marked_for_stop = True 
