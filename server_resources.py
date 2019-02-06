from collections import deque

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
    def process_job(self, job, start_time):
        self.state = 'w'
        return start_time + (job.get_size() / self._capacity)
