
## Horizontal scaling and cost-performance optimization

In horizontal scaling systems, resources are added (launched) when the demand on the system increases
and removed (stopped) when demand drops and they are not needed anymore. 
The arrival intensity and the size of jobs processed 
in such systems usually exhibit a great deal of random variation. 

Obviously, having as many resources as possible helps in reducing the latency (response time) 
experienced by jobs. However, this usually comes at the expense of increased operating cost, e.g.,
rental, energy or other related costs.

**The challenge:** *To optimize the trade-off between system performance and operating cost 
in the face of randomly varying traffic/load. To make things a bit more chanllenging,  
there is also the so-called **launch (setup) delay**, the time it takes to launch/start a 
stopped resource. This could especially be problematic during traffic surges, in which 
case resources are launched in response to traffic increase but they are not ready yet 
to provide service.* 

## System architecture

Horizontal scalability is a basic system design feature that appears in many 
(seamingly unrelated) domains. To name a few, *call center staffing*, *inventory management* and
*highly-available and fault tolerant cloud computing* all leverage the benefits of 
horizontal scaling, and hence need to address the cost-performance trade-off mentioned 
above.

In call centers, fewer operators would translate into less cost (salary) but also longer call 
waiting time for customers. By contrast, increasing the number of operators would reduce call 
waiting time but also increase the operating cost. The launch delay, in this case, is the 
time it takes to (interview, ...etc) aquire new operators. 

Similarly in a cloud computing environment, virtual machines, containers or lambda functions can be 
launched/stopped to improve/reduce performance/cost. If the group of resources are virtual 
machines, the launch delay is the time it takes to bootstrap a VM or a golden image. In any
case, a horizontally scaling system has the following basic components:

- **Traffic**: The stream of jobs that the system is designed to serve. The traffic contributes two 
sources of randomness that should be considered in the design phase. Inter-arrival times of jobs 
and their sizes.
- **Resource/Server**: A server has *m* service places, in which it can serve *m* jobs simultaneously.
If the number of jobs *j* is greater than *m*, the server applies some scheduling policy (e.g. FIFO, PS)
to determine which jobs get processed and which jobs wait in (a) queue(s).
- **Dispatcher**: The interface jobs will encounter when they first arrive in the system. Its main duty is 
assigning incoming jobs to available servers. A dispatcher can be designed to inhance service 
availability and fault tolerance, in which case it is usually known as a **load balancer**.
A dispatcher may also be designed to unbalance load, e.g. to reduce the cost of running servers 
by packing jobs to as few servers as possible. The dispatcher employes popular algorithms such as
**Round Robin**, **Join the Shortest Queue (JSQ)** or **Random** to assign jobs to servers.
- **Resource Group Manager**: This manages the cluster of resources/servers. Have a total of *N* servers
at its disposal, of which *n<=N* are currently active, it applies some scaling policy to determine the number
of servers to stop/remove or launch based on current or estimated load.

The following figure shows a black-box representation of each of the components discussed above and their interaction.

<center><img src="{{ site.baseurl }}/assets/img/resource-group-arch.png" align="middle" style="width: 500px; height: 300px" /></center>

## Analysis

- **Measurement and statistical analysis**: This is usually the prefered way of analysis, in which 
relevant data such as request/job arrival times, response times, and the associated cost is collected
from an actual system. Statistical analysis of the collected data usually produces valuable insights 
into the currently implemented system. These insights, however, are limited to the specific system 
and data set. It is difficult to address questions like "what would happen to the total cost if the 
request arrival intensity is doubled and the processing power of servers is doubled?" Moreover,
such data may not be available, e.g., during the design phase.
- **Emulation and detailed model simulation**: In this case, a simulator that closely mimicks the 
internal workings of the system is used to study performance/cost under different scenarios. Once 
the simulator is built, the system can be studied under all sorts of traffic intensity, load, and 
cost models. However, this approach requires a fairly detailed model for the analysis to produce 
a useful result. For example, in the cloud computing system, we may need to model jobs at 
TCP-connection level or even at packet level (e.g. using NS3).
- **Abstract model simulation**: Here all interactions are abstracted into stochastic models and 
each component is treated as a black-box. The traffic is assumed to be generated from a specific random process, 
whose stochastic properties may or may not be known. Response times are also assumed to be drawn from some 
(unknown) probability distribution. The black-box approach enables us to quickly develop 
the simulator and the resulting analysis has a better chance of being generalizable.
- **Mathematical analysis**: In this case, well-developed mathematical frameworks are applied to 
analyze the system and quantify performance & cost metrics. Closed-form expressions can be obtained 
that provide a number of useful insights about the system. However, due to the shear complexity of 
such systems it os often impossible to do mathematical analysis without making some assumptions 
that may not hold in the real system. Some of the common assumptions are i.i.d. job inter-arrival 
times, i.i.d service times and stationary (often Poisson) arrival process. The analysis often 
focuses on mean values of performance and cost metrics instead of percentiles (e.g. 95th, 99th).

## Example: Abstract modeling of a horizontally-scaled AWS-hosted application

AutoScale - Target load and threshold - launches servers when actual load is greater than target load + threshold
									  - stops servers when actual load is less than target load - threshold
									  - threshold helps in avoiding oscillatory effect in which the autoscaler attempts to 
									  keep the actual load at the target load by launching/stoping servers indefinately
									  - when a server is marked for stopping, this is communicated with the ELB so that 
									  it stops sending new requests to that server
Elastic Load Balancer (ELB) - can use RR, JSQ, RND
N EC2s - m copies of application hosted in a single EC2
