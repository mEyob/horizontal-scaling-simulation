import random

class TrafficGenerator():
    def __init__(self, *, dist=None, dist_param=None, filename=None):
        if dist is None and filename is None:
            raise "Please provide a probability distribution or a file name"
        self.dist = dist
        self.filename = filename
        self.dist_param = dist_param
    def __next__(self):
            while True:
                if isinstance(self.dist_param,(int, float)):
                    return self.dist(self.dist_param)
                elif isinstance(self.dist_param,(list, tuple)):
                    return self.dist(*self.dist_param)
                elif isinstance(self.dist_param,(dict)):
                    return self.dist(**self.dist_param)


if __name__ == "__main__":
    gen = TrafficGenerator(dist=random.uniform, dist_param=(1,10))
    
    sys_time = 0
    for _ in range(10):
        next_arr_time = sys_time + next(gen)
        sys_time = next_arr_time
        print(sys_time)



    # gen_file = TrafficGenerator(filename="testfile.txt")
    # for index, line in enumerate(gen_file):
    #     print(index, line, end="")
    # print("\n")