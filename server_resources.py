from collections import deque

class Queue():
    queue_id = 1
    def __init__(self):
        self.q_id = Queue.queue_id
        Queue.queue_id += 1
        self.num_jobs = 0
        self.queue = deque()
    def put_job(self, job):
        self.queue.append(job)
    def get_job(self):
        try:
            return self.queue.popleft()
        except IndexError:
            return None