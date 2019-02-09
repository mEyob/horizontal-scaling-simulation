import random

class LoadBalancer():
    id_seq = 1
    def __init__(self, servers):
        self.lb_id = 'lb' + str(LoadBalancer.id_seq)
        self.servers = servers
    def jsq(self):
        queue_len = {server.server_id: server.queue.queue_length() for server in self.servers}
        return min(queue_len, key=queue_len.get)
    def roundrobin(self):
        server_id = [server.server_id for server in self.servers]
        while True:
            for i in server_id:
                yield i
    def random(self):
        server_id = [server.server_id for server in self.servers]
        while True:
            yield random.choice(server_id)
