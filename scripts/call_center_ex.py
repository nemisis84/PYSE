import simpy
import random
import numpy as np

NUM_EMPLOYEES = 2
AVG_SUPPORT_TIME = 5
CUSTUMER_INTERVAL = 2
SIM_TIME = 120

custumers_handled = 0


class CallCenter:

    def __init__(self, env, num_employees, support_time):
        self.env = env
        self.staff = simpy.Resource(env, num_employees)
        self.support_time = support_time

    def support(self, custumer):
        random_time = max(1, np.random.normal(self.support_time, 4))
        yield self.env.timeout(random_time)
        print(
            f"support finished for custumer {custumer} at {self.env.now:.2f}")


def custumer(env, name, call_center):
    global custumers_handled
    print(f"Custumer {name} enters waiting queue at {env.now:.2f}!")
    with call_center.staff.request() as request:
        yield request
        print(f"Custumer {name} enters call at {env.now:.2f}")
        yield env.process(call_center.support(name))
        print(f"Custumer {name} left call at {env.now:.2f}")
        custumers_handled += 1


def setup(env, num_employees, support_time, custumer_interval):
    call_center = CallCenter(env, num_employees, support_time)

    for i in range(1, 6):
        env.process(custumer(env, i, call_center))

    while True:
        yield env.timeout(random.randint(custumer_interval - 1, custumer_interval + 1))
        i += 1
        env.process(custumer(env, i, call_center))


print("starting call center simulation")
env = simpy.Environment()
env.process(setup(env, NUM_EMPLOYEES, AVG_SUPPORT_TIME, CUSTUMER_INTERVAL))
env.run(until=SIM_TIME)

print("Custumers handled: " + str(custumers_handled))
