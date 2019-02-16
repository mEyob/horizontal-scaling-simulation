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
        self.state = 'w' # w for working
        self.job = job
        return Event('worker', self.rsc_id, 'job_complete', current_time + (job.get_size() / self._capacity))
    def __repr__(self):
        return 'Worker(id={!r} , Capacity={!r}, State={!r})'.format(self.rsc_id, self._capacity, self.state)


class Server(): 
    id_seq = 1
    def __init__(self, launch_delay,num_of_workers, worker_capacity):
        self.rsc_id = 'S' + str(Server.id_seq)
        Server.id_seq += 1
        self.launch_delay = launch_delay
        self.queue = Queue(self.rsc_id + 'Q')
        self.workers = {}
        self.idle_worker_reg = deque()
        for w_id in range(1, num_of_workers + 1):
            worker_id = self.rsc_id + 'W' + str(w_id)
            self.workers[worker_id] = Worker(worker_id, worker_capacity)
        self.state = 'stopped'
    def start(self, current_time):
        self.state = 'launching'
        return Event('server', self.rsc_id, 'launch_complete', current_time + self.launch_delay)
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
                return self.workers[worker_id].process_job(job, current_time)
            else:
                self.queue.put_job(job, new_job=False)
        return Event('server', self.rsc_id, 'dummy_event', inf)
    def event_handler(self, event):
        if event.type == 'launch_complete':
            self.state = 'ready'
            for worker_id, worker in self.workers.items():
                worker.state = 'i'
                self.idle_worker_reg.append(worker_id)
            next_event = self.assign_job(event.ev_time)
        elif event.type == 'job_complete':
            worker = self.workers[event.rsc_id]
            worker.job.statistics(event.ev_time)
            worker.state = 'i'
            self.idle_worker_reg.append(event.rsc_id)
            next_event = self.assign_job(event.ev_time)
        elif event.type == 'new_job':
            next_event = self.assign_job(event.ev_time)
        return next_event
    def __repr__(self):
        return 'Server(id={!r} , Workers={!r}, State={!r})'.format(self.rsc_id, len(self.workers), self.state)

