import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Custumer:
    def __init__(self, env, checkout):
        self.env = env
        self.checkout = checkout
        self.A = 1

    def checkout_process(self, checkout_lam):
        time_stamp1 = self.env.now
        req = self.checkout.request()
        yield req
        time_stamp2 = self.env.now
        Tq = time_stamp2-time_stamp1
        checkout_time = neg_exp(checkout_lam)
        yield self.env.timeout(checkout_time)
        self.checkout.release(req)
        global queue_times, counters_working, counters_working_when_custumer_arrives
        queue_times.append(Tq)
        counters_working_when_custumer_arrives.append(counters_working)


class Counter:
    def __init__(self, env, checkout, repairman):
        self.env = env
        self.checkout = checkout
        self.repairman = repairman

    def simulate_failure(self, repair_time_lam):
        timestamp = False

        req = self.checkout.request()
        yield req

        global counters_working
        counters_working -= 1
        if counters_working == 0:
            time_stamp1 = self.env.now
            timestamp = True

        repairman_req = self.repairman.request()
        yield repairman_req

        repair_time = neg_exp(repair_time_lam)
        yield self.env.timeout(repair_time)

        self.repairman.release(repairman_req)
        self.checkout.release(req)

        counters_working += 1

        if timestamp:
            time_stamp2 = self.env.now
            global down_time
            down_time += time_stamp2-time_stamp1
            timestamp = False


def neg_exp(lam):
    return np.random.exponential(1/lam)


def generate_custumers(env, checkout, checkout_lam, customer_interval_lam):
    while True:
        new_custumer = Custumer(env, checkout)
        env.process(new_custumer.checkout_process(checkout_lam))
        yield env.timeout(neg_exp(customer_interval_lam))


def generate_failure(env, counter, repair_time_lam, failure_interval_lam):
    while True:
        global counters_working
        if counters_working > 0:
            time_to_next_failure = neg_exp(
                failure_interval_lam*counters_working)
            yield env.timeout(time_to_next_failure)
            env.process(counter.simulate_failure(repair_time_lam))
        else:
            yield env.timeout(0.1)


def availability(up_time, down_time):
    return up_time/(up_time+down_time)


def simulate():
    # Lambdas
    checkout_lam = 1/2
    # 4hours between every failure for each counter. Will be multiplied with counters_working before used
    failure_interval_lam = 1/(4*60)
    repair_time_lam = 1/15
    customer_interval_lam = 1/3

    # Simpy setup and resources
    env = simpy.Environment()
    repairman = simpy.Resource(env, capacity=1)
    checkout = simpy.Resource(env, capacity=4)
    counter = Counter(env, checkout, repairman)

    # Start processes
    env.process(generate_custumers(env, checkout,
                                   checkout_lam, customer_interval_lam))
    env.process(generate_failure(
        env, counter, repair_time_lam, failure_interval_lam))
    env.run(until=16*60)

    up_time = 16*60-down_time
    global A_list
    A_list.append(availability(up_time, down_time))


if __name__ == "__main__":

    queue_times_list = []
    down_time_list = []
    counters_working_when_custumer_arrives_list = []
    A_list = []
    for i in range(365*3):
        print(f"Run{i}")
        queue_times = []
        down_time = 0
        counters_working = 4
        counters_working_when_custumer_arrives = []
        simulate()
        queue_times_list.append(np.array(queue_times))
        down_time_list.append(down_time)
        counters_working_when_custumer_arrives_list.append(
            np.array(counters_working_when_custumer_arrives))

    queue_times_list = np.hstack(np.array(queue_times_list))
    counters_working_when_custumer_arrives_list = np.hstack(np.array(
        counters_working_when_custumer_arrives_list))
    A_list = np.hstack(np.array(A_list))
    print(f'Results:\nAvailability A = {A_list.mean()}\nA std = {A_list.std()}\nMean queue time T_q = {queue_times_list.mean()}\nQueue time std={queue_times_list.std()}\nMean counters available when in front of line = {counters_working_when_custumer_arrives_list.mean()}\Counters available when in front of line std = {counters_working_when_custumer_arrives_list.std()}')
