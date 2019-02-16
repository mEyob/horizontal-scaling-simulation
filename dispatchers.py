import random

class LoadBalancer():
    id_seq = 1
    def __init__(self, servers):
        self.rsc_id = 'LB' + str(LoadBalancer.id_seq)
        self.target_servers = servers
    def jsq(self):
        while True:
            queue_len = {server.rsc_id: server.queue.queue_length() for server in self.target_servers}
            yield min(queue_len, key=queue_len.get)
    def roundrobin(self):
        server_id = [server.rsc_id for server in self.target_servers]
        while True:
            for i in server_id:
                yield i
    def random(self):
        server_id = [server.rsc_id for server in self.target_servers]
        while True:
            yield random.choice(server_id)
