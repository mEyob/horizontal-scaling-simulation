from sys import stdout as stdout

class Job:
    '''docstring for job '''
    num_of_jobs   = 0
    avg_resp_time = 0
    var_resp_time = 0
    tot_resp_time = 0
    def __init__(self, arrival_time, size):
        self._arrival_time = arrival_time
        self._size = size
        self._remaining_size = size
    def reduce_size(self, size):
        self._remaining_size = max(0, self._remaining_size - size)
    def get_size(self):
        return self._remaining_size
    def statistics(self, current_time):
        '''
        Online statistics collection for 
        mean and variance of response time
        '''
        Job.num_of_jobs   += 1
        resp_time          = current_time - self._arrival_time
        Job.tot_resp_time += resp_time
        delta = resp_time - Job.avg_resp_time
        Job.avg_resp_time += (delta / Job.num_of_jobs)
        Job.var_resp_time += delta * (resp_time - Job.avg_resp_time)
    
    @classmethod
    def write_stats(cls, stream=None):
        if stream is None:
            stream = stdout
        stream.write(',{},'.format(cls.num_of_jobs))
        stream.write('{:.5f},'.format(cls.avg_resp_time))
        stream.write('{:.5f}'.format(cls.var_resp_time / (cls.num_of_jobs - 1)))

    @classmethod 
    def reset(cls):
        cls.num_of_jobs   = 0
        cls.avg_resp_time = 0
        cls.var_resp_time = 0
        cls.tot_resp_time = 0

    def __repr__(self):
        return 'Job(arrival time={!r}, size={!r}, remaining size={!r})'.format(self._arrival_time, self._size, self._remaining_size)


        