import simpy
import numpy

#---------- Time unit i minutes ----------#

# Values

# Lambda inter arrival = 1/10 (every 10th minute)
lambda_ia = 1/10

# Create a sample picker from a negative exponential distribution
def inter_arrival_time(lambda_):
    return numpy.random.exponential(1/lambda_) # beta = 1/lambda

# Generator
def generator(env):
    id = 0
    while True:
        new_car = car(env, id) # Create the car
        env.process(new_car) # Have the environment process the car
        yield env.timeout(inter_arrival_time(lambda_ia)) # Wait sample of inter arrival time before creating next car
        id += 1

# Car component
def car(env, id):
    global tally, n         # Make tally and n available inside function
    gen_time = env.now      # Record generation time
    req = station.request() # Create request for resource
    yield req               # Ask for resource
    start_fill = env.now    # Record start filling time
    yield env.timeout(5)    # Wait 5 minutes for refilling
    station.release(req)    # Leave station and release station
    end_fill = env.now      # Record end filling time
    wait_times.append(start_fill-gen_time) # Add wait time to list for further calculations
    tally += start_fill-gen_time           # Add wait time to tally for further calculations
    n += 1                                 # Increment n for calculations
    print(f"Car: {id} \t Generated: {gen_time} \t Queue time:  {start_fill-gen_time} \t Start filling: {start_fill} \t End filling: {end_fill}")

# Results collecting
wait_times = []
tally = 0
n = 0

# Create the environment for simulation
env = simpy.Environment()

# Create the petrol station resource
station = simpy.Resource(env, capacity=1)

# Start the generator running in our environment
env.process(generator(env))

# Say how long to run the simulation for
env.run(until=500)

# Plotting results
print("------------------------------Results------------------------------")
print("Avereage wait time:", numpy.average(wait_times))
print("Avereage wait time:", tally/n) 
print("--------------------------------------------------------------------")