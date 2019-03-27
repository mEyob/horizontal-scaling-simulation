import random

class LoadBalancer():
    id_seq = 1
    def __init__(self, servers):
        self.rsc_id = 'LB' + str(LoadBalancer.id_seq)
        self.target_servers = servers
        self.unavailable = ['stopped', 'marked_for_stop']
    def jsq(self):
        while True:
            queue_len = [(server.rsc_id, server.queue.queue_length()) for server in self.target_servers.values() if server.state not in self.unavailable]
            queue_len.sort()
            yield min(queue_len, key=lambda x: x[1])[0]
    def roundrobin(self):
        server_id = [server.rsc_id for server in self.target_servers.values()]
        while True:
            for serv_id in server_id:
                if self.target_servers[serv_id].state not in self.unavailable:
                    yield serv_id
    def random(self):
        while True:
            server_id = [server.rsc_id for server in self.target_servers.values() if server.state not in self.unavailable]
            yield random.choice(server_id)
