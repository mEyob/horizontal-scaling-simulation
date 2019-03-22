#!/usr/bin/env python3
import argparse
import controller

###### Default parameter values
min_servers = 1
max_servers = 10
starting_num = 1
launch_delay = 1
num_of_workers = 2
worker_capacity = 100
arr_dist_name = 'expo'
arr_dist_param = 100
size_dist_name = 'expo'
size_dist_param = 1
avg_job_size = 1 / size_dist_param
server_cost_rate = 1
fromfile=False 
filetuple=None
lb_alg='roundrobin'
max_jobs=100000
estimation_interval = 100 * (1 / arr_dist_param)
scaling_period = 10 * estimation_interval

parser = argparse.ArgumentParser()


parser.add_argument("min",help='Minimum number of servers')
parser.add_argument("max",help='Maximum number of servers')
parser.add_argument("start",help='Starting number of servers')

parser.add_argument("-l","--launchdelay", help='Launch delay of servers')
parser.add_argument("-w","--workers", help='Number of workers per server')
parser.add_argument("-c","--workercap", help='Worker capacity')
parser.add_argument("-a","--arrdist", help='Probability distribution of request inter-arrival times')
parser.add_argument("-p","--arrdistparam", help='Used together with --arrdist option to set parameters for the arrival distribution')
parser.add_argument("-s","--sizedist", help='Probability distribution of request size')
parser.add_argument("-q","--sizedistparam", help='Used together with --size option to set parameters for the size distribution')

args = parser.parse_args()

if args.launchdelay:
    launch_delay = float(args.launchdelay)
if args.workers:
    num_of_workers = float(args.workers)
if args.workercap:
    worker_capacity = float(args.workercap)
if args.arrdist:
    arr_dist_name = args.arrdist
if args.arrdistparam:
    arr_dist_param = args.arrdistparam.split()
    arr_dist_param = tuple(map(float, arr_dist_param))
if args.sizedist:
    size_dist_name = args.sizedist
if args.sizedistparam:
    size_dist_param = args.sizedistparam.split()
    size_dist_param = tuple(map(float, size_dist_param))

min_servers = int(args.min)
max_servers = int(args.max) 
starting_servers = int(args.start)
result = controller.main(
    min_servers,
    starting_servers, 
    max_servers,
    server_cost_rate = server_cost_rate, 
    launch_delay = launch_delay, 
    num_of_workers = num_of_workers, 
    worker_capacity = worker_capacity, 
    avg_job_size = avg_job_size,
    arr_dist_name = arr_dist_name, 
    arr_dist_param = arr_dist_param, 
    size_dist_name = size_dist_name, 
    size_dist_param = size_dist_param, 
    estimation_interval = estimation_interval,
    scaling_period = scaling_period,
    fromfile=fromfile, 
    filetuple=filetuple, 
    lb_alg=lb_alg, 
    max_jobs=max_jobs
    )
print(result)



