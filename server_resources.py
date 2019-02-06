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