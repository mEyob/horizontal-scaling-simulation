from math import inf
from collections import namedtuple
from scaling_group import ScalingGroup
from traffic_source import TrafficGenerator
from dispatchers import LoadBalancer
from job import Job

Event = namedtuple('Event', 'rsc rsc_id type ev_time')

class Controller():
    id_seq = 1
    def __init__(self, scaling_group, arrival_generator, size_generator, load_balancer):
        self.rsc_id = 'C' + str(Controller.id_seq)
        Controller.id_seq += 1
        self.scaling_group = scaling_group
        self.arrival_generator = arrival_generator
        self.size_generator = size_generator
        self.load_balancer = load_balancer
    
    def run_simulation(self, max_jobs):
        sim_time = 0
        event_dict = {}

        for rsc_id, server in self.scaling_group.items():
            event_dict[rsc_id] = server.start(sim_time)
        arrival = self.arrival_generator.generate()
        next_arr_time = sim_time + next(arrival)
        event_dict[self.arrival_generator.rsc_id] = Event('arr_generator', self.arrival_generator.rsc_id, 'arrival', next_arr_time)

        # for rsc_id in self.scaling_group.keys():
        #     event_dict[rsc_id] = Event('server', rsc_id, 'dummy_event', inf)

        while Job.num_of_jobs < max_jobs:
            event = min(event_dict.items(), key=lambda x: x[1].ev_time)[1]

            if event.type == 'arrival':
                chosen_server = next(self.load_balancer)
                job_size = next(self.size_generator)
                job = Job(event.ev_time, job_size)
                self.scaling_group[chosen_server].queue.put_job(job)
                new_event = self.scaling_group[chosen_server].event_handler(Event('ctrl', self.rsc_id, 'new_job', event.ev_time))
                if new_event.type is not 'dummy_event':
                    event_dict[new_event.rsc_id] = new_event
                try:
                    next_arr_time = event.ev_time + next(arrival)
                except StopIteration:
                    break
                event_dict[self.arrival_generator.rsc_id] = Event('arr_generator', self.arrival_generator.rsc_id, 'arrival', next_arr_time)

            else:
                server_id = event.rsc_id.split('W')[0]
                new_event = self.scaling_group[server_id].event_handler(event)
                if event.type == 'launch_complete':
                    event_dict[event.rsc_id] = Event('server', event.rsc_id, 'launch_complete', inf)
                elif event.type == 'job_complete':
                    event_dict[event.rsc_id] = Event('worker', event.rsc_id, 'job_complete', inf)
                if new_event.type is not 'dummy_event':
                    event_dict[new_event.rsc_id] = new_event

            sim_time = event.ev_time

def main(min_servers, starting_num, max_servers, launch_delay, num_of_workers, worker_capacity, arr_dist_name, arr_dist_param, size_dist_name, size_dist_param, fromfile=False, filetuple=None, lb_alg='roundrobin', max_jobs=1000):
    arrival_generator = TrafficGenerator(arr_dist_name, arr_dist_param, fromfile, filetuple)
    size_generator = TrafficGenerator(size_dist_name, size_dist_param, fromfile, filetuple)
    generate_size = size_generator.generate()
    server_group = ScalingGroup(min_servers, starting_num, max_servers, launch_delay, num_of_workers, worker_capacity)
    load_balancer = LoadBalancer(server_group.scaling_group)
    
    lb = getattr(load_balancer, lb_alg.lower())    
    lb = lb()
    controller = Controller(server_group.scaling_group, arrival_generator, generate_size, lb)
    controller.run_simulation(max_jobs)
    print(Job.avg_resp_time)

if __name__ == '__main__':
    min_servers = 1
    max_servers = 10
    starting_num = 1
    launch_delay = 1
    num_of_workers = 2
    worker_capacity = 100
    arr_dist_name = 'expo'
    arr_dist_param = 150
    size_dist_name = 'expo'
    size_dist_param = 1

    main(min_servers, starting_num, max_servers, launch_delay, num_of_workers, worker_capacity, arr_dist_name, arr_dist_param, size_dist_name, size_dist_param, fromfile=False, filetuple=None, lb_alg='roundrobin', max_jobs=100000)
