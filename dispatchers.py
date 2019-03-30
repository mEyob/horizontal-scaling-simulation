import random

class LoadBalancer():
    id_seq = 1
    def __init__(self, servers):
        self.rsc_id = 'LB' + str(LoadBalancer.id_seq)
        self.target_servers = servers
        self.unavailable = ['stopped']
    def jsq(self):
        while True:
            queue_len = [(server.rsc_id, server.queue.queue_length()) for server in self.target_servers.values() if server.state not in self.unavailable and not server.marked_for_stop]
            queue_len.sort()
            yield min(queue_len, key=lambda x: x[1])[0]
    def roundrobin(self):
        server_id = [server.rsc_id for server in self.target_servers.values()]
        while True:
            for serv_id in server_id:
                if self.target_servers[serv_id].state not in self.unavailable and not self.target_servers[serv_id].marked_for_stop:
                    yield serv_id
    def random(self):
        while True:
            server_id = [server.rsc_id for server in self.target_servers.values() if server.state not in self.unavailable and not server.marked_for_stop]
            yield random.choice(server_id)
