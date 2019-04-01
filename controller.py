from math import inf
from collections import namedtuple
from scaling_group import ScalingGroup
from traffic_source import TrafficGenerator
from dispatchers import LoadBalancer
from job import Job

Event = namedtuple('Event', 'rsc rsc_id type ev_time')

class Controller():
    id_seq = 1
    def __init__(self, scaling_group, starting_num, arrival_generator, size_generator, load_balancer):
        self.rsc_id = 'C' + str(Controller.id_seq)
        Controller.id_seq += 1
        self.scaling_group = scaling_group
        self.arrival_generator = arrival_generator
        self.size_generator = size_generator
        self.load_balancer = load_balancer
        self.starting_num = starting_num
    
    def run_simulation(self, max_jobs):
        sim_time = 0
        event_dict = {}

        count = 0
        for rsc_id, server in self.scaling_group.scaling_group.items():
            if count < self.starting_num:
                event_dict[rsc_id] = server.start(sim_time)
                count += 1
        arrival = self.arrival_generator.generate()
        next_arr_time = sim_time + next(arrival)
        event_dict[self.arrival_generator.rsc_id] = Event('arr_generator', self.arrival_generator.rsc_id, 'arrival', next_arr_time)

        # Scaling related event
        event_dict[ScalingGroup.rsc_id] = Event('scaling_group', ScalingGroup.rsc_id, 'start_estimation', sim_time)

        while Job.num_of_jobs < max_jobs:
            event = min(event_dict.items(), key=lambda x: x[1].ev_time)[1]

            if event.type == 'arrival':
                chosen_server = next(self.load_balancer)
                job_size = next(self.size_generator)
                job = Job(event.ev_time, job_size)
                self.scaling_group.scaling_group[chosen_server].queue.put_job(job)
                new_event = self.scaling_group.scaling_group[chosen_server].event_handler(Event('ctrl', self.rsc_id, 'new_job', event.ev_time))
                if new_event.type != 'dummy_event':
                    event_dict[new_event.rsc_id] = new_event
                try:
                    next_arr_time = event.ev_time + next(arrival)
                except StopIteration:
                    break
                self.scaling_group.job_count += 1
                event_dict[self.arrival_generator.rsc_id] = Event('arr_generator', self.arrival_generator.rsc_id, 'arrival', next_arr_time)

            elif event.type == 'launch_complete' or event.type == 'job_complete':
                if event.type == 'launch_complete':
                    event_dict[event.rsc_id] = Event('server', event.rsc_id, 'launch_complete', inf)
                elif event.type == 'job_complete':
                    event_dict[event.rsc_id] = Event('worker', event.rsc_id, 'job_complete', inf)
                server_id = event.rsc_id.split('W')[0]
                new_event = self.scaling_group.scaling_group[server_id].event_handler(event)
                if new_event.type != 'dummy_event':
                    event_dict[new_event.rsc_id] = new_event
            elif event.type == 'start_estimation' or event.type == 'start_scaling':
                events = self.scaling_group.event_handler(event)
                for ev in events:
                    event_dict[ev.rsc_id] = ev
            current_time = event.ev_time
        for server in self.scaling_group.scaling_group.values():
            if server.state != 'stopped':
                server.calc_cost(current_time)

def main(min_servers, starting_num, max_servers, target_load, *, server_cost_rate, launch_delay, num_of_workers, worker_capacity, arr_dist_name, arr_dist_param, size_dist_name, size_dist_param, estimation_interval, scaling_period, fromfile=False, filetuple=None, lb_alg='jsq', max_jobs=1000):
    # the line below only works for exp inter-arrival times (assuming arr_dist_param = arrival rate)
    # if not, substitute arr_dist_param with the correct arrival rate
    transient = 0.1 * max_jobs / arr_dist_param
    avg_job_size = 1 / size_dist_param[0]
    arrival_generator = TrafficGenerator(arr_dist_name, arr_dist_param, fromfile, filetuple)
    size_generator = TrafficGenerator(size_dist_name, size_dist_param, fromfile, filetuple)
    generate_size = size_generator.generate()
    Scaling_group = ScalingGroup(min_servers, starting_num, max_servers, target_load, server_cost_rate, launch_delay, num_of_workers, worker_capacity, avg_job_size, estimation_interval, scaling_period, transient)
    load_balancer = LoadBalancer(Scaling_group.scaling_group)
    
    lb = getattr(load_balancer, lb_alg.lower())    
    lb = lb()
    controller = Controller(Scaling_group, starting_num, arrival_generator, generate_size, lb)
    controller.run_simulation(max_jobs)
    total_cost = sum([server.total_cost for server in Scaling_group.scaling_group.values()])
    return Job.avg_resp_time, total_cost

if __name__ == '__main__':
    min_servers = 1
    max_servers = 10
    starting_servers = 1
    target_load = 0.5
    server_cost_rate = 1
    launch_delay = 1
    num_of_workers = 2
    worker_capacity = 100
    arr_dist_name = 'expo'
    arr_dist_param = 150
    size_dist_name = 'expo'
    size_dist_param = 1
    estimation_interval = 100 * (1 / arr_dist_param)
    scaling_period = 10 * estimation_interval

    result = main(
    min_servers,
    starting_servers, 
    max_servers,
    target_load,
    server_cost_rate = server_cost_rate, 
    launch_delay = launch_delay, 
    num_of_workers = num_of_workers, 
    worker_capacity = worker_capacity, 
    arr_dist_name = arr_dist_name, 
    arr_dist_param = arr_dist_param, 
    size_dist_name = size_dist_name, 
    size_dist_param = size_dist_param, 
    estimation_interval = estimation_interval,
    scaling_period = scaling_period,
    fromfile=False, 
    filetuple=None, 
    lb_alg='jsq', 
    max_jobs=100000
    )
