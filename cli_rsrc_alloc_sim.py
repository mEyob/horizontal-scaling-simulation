#!/usr/bin/env python3
import argparse
import controller

###### Default parameter values
min_servers = 1
max_servers = 10
starting_num = 1
launch_delay = 1
num_of_workers = 2
worker_capacity = 1
arr_dist_name = 'expo'
arr_dist_param = 150
size_dist_name = 'expo'
size_dist_param = [0.5]
server_cost_rate = 1
fromfile=False 
filetuple=None
lb_alg='roundrobin'
max_jobs=50000
estimation_interval = 10
scaling_period = 60

parser = argparse.ArgumentParser()


parser.add_argument("min",help='Minimum number of servers')
parser.add_argument("max",help='Maximum number of servers')
parser.add_argument("start",help='Starting number of servers')
parser.add_argument("targetLoad", help='The load at which the system is supposed to operate')

parser.add_argument("-C","--costrate", help='Operational (rental) cost of servers per time unit')
parser.add_argument("-l","--launchdelay", help='Launch delay of servers')
parser.add_argument("-L", "--lbalg", help='The load balancing algorithm. Can be JSQ, RND or RR')
parser.add_argument("-w","--workers", help='Number of workers per server')
parser.add_argument("-c","--workercap", help='Worker capacity')
#parser.add_argument("-j","--jobsize", help='Average job size')
parser.add_argument("-a","--arrdist", help='Probability distribution of request inter-arrival times')
parser.add_argument("-p","--arrdistparam", help='Used together with --arrdist option to set parameters for the arrival distribution')
parser.add_argument("-s","--sizedist", help='Probability distribution of request size')
parser.add_argument("-q","--sizedistparam", help='Used together with --size option to set parameters for the size distribution')
parser.add_argument("-A","--autoscale", help='Autoscaling period for the server group')
parser.add_argument("-e","--estinterval", help='Estimation interval for infering load parameters for autoscale')
args = parser.parse_args()

if args.costrate:
    server_cost_rate = float(args.costrate)
if args.launchdelay:
    launch_delay = float(args.launchdelay)
if args.lbalg:
    lb_alg = args.lbalg
if args.workers:
    num_of_workers = int(args.workers)
if args.workercap:
    worker_capacity = float(args.workercap)
if args.arrdist:
    arr_dist_name = args.arrdist
# if args.jobsize:
#     avg_job_size = float(args.jobsize)
if args.arrdistparam:
    arr_dist_param = args.arrdistparam.split()
    if len(arr_dist_param) == 1:
        arr_dist_param = float(arr_dist_param[0])
    else:
        arr_dist_param = tuple(map(float, arr_dist_param))
if args.sizedist:
    size_dist_name = args.sizedist
if args.sizedistparam:
    size_dist_param = args.sizedistparam.split()
    size_dist_param = tuple(map(float, size_dist_param))
if args.estinterval:
    estimation_interval = float(args.estinterval)
if args.autoscale:
    scaling_period = float(args.autoscale)

min_servers = int(args.min)
max_servers = int(args.max) 
starting_servers = int(args.start)
target_load = float(args.targetLoad)
result = controller.main(
    min_servers,
    starting_servers, 
    max_servers,
    target_load,
    server_cost_rate = server_cost_rate, 
    launch_delay = launch_delay, 
    num_of_workers = num_of_workers, 
    worker_capacity = worker_capacity, 
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



