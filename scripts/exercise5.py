import simpy
from numpy import average, random

# Constants
MAX_DELAY = 3 # s
TRANSMISSION_DELAY_BETWEEN_ROUTERS = 0.2 # s
lambda_iat = 2 # s^(-1)
my_st = 1/3 # s
SIM_TIME = 30000 # s

# Values
def packet_inter_arrival_time(lambda_):
    return random.exponential(1/lambda_) # negative exponential distribution

def router_service_time(my_):
    return random.gamma(3, my_/3) # Erlang-3 distribution with expected value my_

# Objects
def packet_generator(env):
    while True:
        packet = Packet(env)
        packets.append(packet)
        yield env.timeout(packet_inter_arrival_time(lambda_iat))

class Packet(object):
    def __init__(self, env):
        self.env = env
        self.timestamp = env.now
        self.ttl = True
        self.ttlafterR3 = True
        self.delay = -1 # set to -1 as start-value, to be able to discard packets which did not finish traversing the routers
        self.process = env.process(self.traverseRouters()) 
        
    def traverseRouters(self):
        global recievedPackets, lostPackets, lostPacketsAfterR3, lostPacketsBetweenR2andR3 # Make variables available inside class
        first_hop = random.randint(0,2) # Choose first hop, 0 or 1
        with routers[first_hop].queue.request() as req:
            start_first = env.now
            yield req
            yield self.env.process(routers[first_hop].route(self))
            r = "R"+str(first_hop+1)
            time_in_routers[r].append(env.now - start_first)
            if not self.ttl: # If packet discardes
                lostPackets += 1
                return
        if first_hop == 1:
            if random.uniform() < 10e-4:
                lostPacketsBetweenR2andR3 += 1
                return
        yield self.env.timeout(TRANSMISSION_DELAY_BETWEEN_ROUTERS)
        with routers[2].queue.request() as req:
            start_last = env.now
            yield req
            yield self.env.process(routers[2].route(self))
            time_in_routers["R3"].append(env.now - start_last)
            if not self.ttl: # If packet discardes
                lostPackets += 1
                return
        self.delay = env.now - self.timestamp
        if self.delay > MAX_DELAY:
            self.ttlafterR3 = False
            lostPacketsAfterR3 += 1
            return
        recievedPackets += 1 # Packet did not get discarded

class Router(object):
    def __init__(self, env):
        self.env = env
        self.queue = simpy.Resource(env, capacity=1) # Create in-queue for router

    def route(self, packet): # route packet throug router
        if self.env.now - packet.timestamp > MAX_DELAY:
            packet.ttl = False # Discard packet
            return
        yield self.env.timeout(router_service_time(my_st))

# Registering results and plotting
recievedPackets = 0
lostPackets = 0
lostPacketsAfterR3 = 0
lostPacketsBetweenR2andR3 = 0
packets = []
time_in_routers = {"R1": [], "R2": [], "R3": []}

# Simulating
env = simpy.Environment()
env.process(packet_generator(env)) # Start the generator
routers = [Router(env) for i in range(3)] # Create router 0, 1 and 2 in a list (R1, R2, R3)
env.run(until=SIM_TIME) # Run simulation

# Results
print("--------------------------5.1 b)--------------------------")
print("Recieved packets:", recievedPackets)
print("Lost packets:", lostPackets)

print("--------------------------5.1 c)--------------------------")
avg_delay = average([p.delay for p in packets if p.ttl]) # Find mean delay for packets which were not discarded
min_delay = min([p.delay for p in packets if p.ttl and p.delay != -1]) # Find minimum delay for packets which were not discarded or did not finish traversing routers
max_delay = max([p.delay for p in packets])
print("Mean end-to-end delay:", avg_delay)
print("Minimum delay:", min_delay)
print("Maximum delay:", max_delay)

print("--------------------------5.1 d)--------------------------")
print("Lost packets after R3:", lostPacketsAfterR3)
print("Total number of lost packets:", lostPackets + lostPacketsAfterR3)
avg_delay_R3 = average([p.delay for p in packets if p.ttlafterR3]) # Find mean delay for packets which were not discarded, even after R3
print("Mean end-to-end delay without packets discareded after R3:", avg_delay_R3)

print("--------------------------5.1 e)--------------------------")
print("Mean time in R1:", average(time_in_routers["R1"]))
print("Mean time in R2:", average(time_in_routers["R2"]))
print("Mean time in R3:", average(time_in_routers["R3"]))
print("R3 is bottleneck in network")

print("--------------------------5.1 f)--------------------------")
print("Packets lost between R2 and R3:", lostPacketsBetweenR2andR3)
