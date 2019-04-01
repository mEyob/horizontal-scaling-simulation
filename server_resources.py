from collections import deque, namedtuple
from math import inf

Event = namedtuple('Event', 'rsc rsc_id type ev_time')


class Queue():
    def __init__(self, queue_id):
        self.rsc_id = queue_id
        self._queue = deque()
    def put_job(self, job, new_job=True):
        if new_job:
            self._queue.appendleft(job)
        else:
            self._queue.append(job)
    def get_job(self):
        try:
            return self._queue.pop()
        except IndexError:
            return None
    def queue_length(self):
        return len(self._queue)
    def __repr__(self):
        return 'Queue(id={!r} , Queue length={!r})'.format(self.rsc_id, self.queue_length())


class Worker():
    def __init__(self, worker_id, capacity):
        self.rsc_id = worker_id
        self._capacity = capacity
        self.state = 'u' # u for unavailable
    def process_job(self, job, current_time):
        assert self.state == 'i', "Worker state {}. Worker needs to be idle to start processing jobs".format(self.state)
        self.state = 'w' # w for working
        self.job = job
        return Event('worker', self.rsc_id, 'job_complete', current_time + (job.get_size() / self._capacity))
    def __repr__(self):
        return 'Worker(id={!r} , Capacity={!r}, State={!r})'.format(self.rsc_id, self._capacity, self.state)


class Server(): 
    id_seq = 1
    def __init__(self, launch_delay, cost_rate, num_of_workers, worker_capacity, avg_job_size):
        self.rsc_id = 'S' + str(Server.id_seq)
        Server.id_seq += 1
        self.launch_delay = launch_delay
        self.cost_rate = cost_rate
        self.queue = Queue(self.rsc_id + 'Q')
        self.workers = {}
        self.idle_worker_reg = deque()
        for w_id in range(1, num_of_workers + 1):
            worker_id = self.rsc_id + 'W' + str(w_id)
            self.workers[worker_id] = Worker(worker_id, worker_capacity)
        self.state = 'stopped'
        self.marked_for_stop = False
        self.total_cost = 0
        self.last_cost_time = -1 # cost should acumulate only after the server is started for the first time
    def start(self, current_time):
        self.last_cost_time = current_time
        self.state = 'launching'
        self.marked_for_stop = False
        return Event('server', self.rsc_id, 'launch_complete', current_time + self.launch_delay)
    def stop(self, current_time):
        self.calc_cost(current_time)
        self.state = 'stopped'
        for worker in self.workers.values():
            worker.state = 'u'
        self.idle_worker_reg = deque()
    def calc_cost(self, current_time):
        if self.last_cost_time > -1:
            self.total_cost += self.cost_rate * (current_time - self.last_cost_time)
        self.last_cost_time = current_time
    def total_jobs(self):
        queue_len = self.queue.queue_length()
        busy_workers = sum([1 for worker in self.workers.values() if worker.state == 'w'])
        return queue_len + busy_workers
    def get_worker(self):
        try:
            return self.idle_worker_reg.popleft()
        except IndexError:
            return None
    def assign_job(self, current_time):
        job = self.queue.get_job()
        if job:
            worker_id = self.get_worker()
            if worker_id:
                assert self.workers[worker_id].state == 'i', "Worker state {}. Only idle workers can start processing jobs".format(self.workers[worker_id].state)
                self.state = 'busy'
                return self.workers[worker_id].process_job(job, current_time)
            else:
                self.queue.put_job(job, new_job=False)
        return Event('server', self.rsc_id, 'dummy_event', inf)

    def event_handler(self, event):
        if event.type == 'launch_complete':
            assert self.state == 'launching', "Launch complete only possible in the \'launching\' state."
            self.state = 'idle'
            for worker_id, worker in self.workers.items():
                worker.state = 'i'
                self.idle_worker_reg.append(worker_id)
            next_event = self.assign_job(event.ev_time)
        elif event.type == 'job_complete':
            assert self.state is 'busy', "Jobs can only be processed in the \'busy\' state."
            worker = self.workers[event.rsc_id]
            worker.job.statistics(event.ev_time)
            worker.state = 'i'
            self.idle_worker_reg.append(event.rsc_id)
            worker_states = [True if worker.state == 'i' else False for worker in self.workers.values() ]
            if all(worker_states) and self.queue.queue_length() == 0:
                self.state = 'idle'
            if self.marked_for_stop and self.state == 'idle':
                self.stop(event.ev_time)
            next_event = self.assign_job(event.ev_time)
        elif event.type == 'new_job':
            next_event = self.assign_job(event.ev_time)
        return next_event
    def __repr__(self):
        return 'Server(id={!r} , Workers={!r}, State={!r})'.format(self.rsc_id, len(self.workers), self.state)

