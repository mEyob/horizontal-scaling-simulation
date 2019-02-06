from collections import deque, namedtuple

Event = namedtuple('Event', 'creator type time')


class Queue():
    def __init__(self, queue_id):
        self._queue_id = queue_id
        self._queue = deque()
    def put_job(self, job):
        self._queue.append(job)
    def get_job(self):
        try:
            return self._queue.popleft()
        except IndexError:
            return None


class Worker():
    def __init__(self, worker_id, capacity):
        self._worker_id = worker_id
        self._capacity = capacity
        self.state = 'i'
    def process_job(self, job, current_time):
        self.state = 'w'
        return Event(self._worker_id, 'job_complete', current_time + (job.get_size() / self._capacity))

class Server(): 
    id_seq = 1
    def __init__(self, launch_delay,num_of_workers, worker_capacity):
        self.server_id = 'S' + str(Server.id_seq)
        Server.id_seq += 1
        self.launch_delay = launch_delay
        self.queue = Queue(self.server_id + 'Q')
        self.workers = {}
        for w_id in range(1, num_of_workers + 1):
            worker_id = self.server_id + 'W' + str(w_id)
            self.workers[worker_id] = Worker(worker_id, worker_capacity)
    def start(self, current_time):
        self.state = 'launching'
        return Event(self.server_id, 'launch_complete', current_time + self.launch_delay)

