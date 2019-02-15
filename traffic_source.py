import random
import csv

class TrafficGenerator():
    def __init__(self, dist_name, dist_param, fromfile=False, filetuple=None):
        self.dist_name = dist_name
        self.dist_param = dist_param
        self._set_dist()
        self.fromfile = fromfile
        self.filetuple = filetuple
    def _set_dist(self):
        '''A method for setting the pdf function of an instance 
        of the TrafficGenerator class'''
        if self.dist_name =='unif':
            self.dist_func = random.uniform
        elif self.dist_name == 'expo':
            self.dist_func = random.expovariate
        elif self.dist_name == 'norm':
            self.dist_func = random.normalvariate
        elif self.dist_name == 'prto':
            self.dist_func = random.paretovariate
    @classmethod
    def from_file(cls, filetuple):
        '''Alternative constructor for TrafficGenerator to generate
        realizations from file instead of from a prob. distribution.
        'filetuple' should be of the form:
        namedtuple('FileTuple', 'filename column header delimiter') '''
        return cls(None, None, True, filetuple)
    def generate(self):
        '''A method for generating realizations of a random process 
        using probability distributions or a CSV file'''
        if self.fromfile:
            with open(self.filetuple.filename, 'r') as file_obj:
                csv_reader = csv.reader(file_obj, delimiter=self.filetuple.delimiter)
                if self.filetuple.header:
                    print('I was here')
                    next(csv_reader)
                for line in csv_reader:
                    try:
                        value = float(line[int(self.filetuple.column)])
                    except ValueError:
                        pass
                    except IndexError:
                        pass
                    else:
                        yield value
        else:
            while True:
                if isinstance(self.dist_param,(int, float)):
                    yield self.dist_func(self.dist_param)
                elif isinstance(self.dist_param,(list, tuple)):
                    yield self.dist_func(*self.dist_param)
                elif isinstance(self.dist_param,(dict)):
                    yield self.dist_func(**self.dist_param)


if __name__ == "__main__":
    from collections import namedtuple

    file_tuple = namedtuple('FileTuple', 'filename column header delimiter')

    gen = TrafficGenerator(dist_name='unif', dist_param=(1,10))
    generator = gen.generate()
    
    sys_time = 0
    for _ in range(10):
        next_arr_time = sys_time + next(generator)
        sys_time = next_arr_time
        print(sys_time)

    file_info = file_tuple('test_file.csv', '1', False, ',')

    gen_file = TrafficGenerator.from_file(file_info)
    generator = gen_file.generate()

    while True:
        print(next(generator))