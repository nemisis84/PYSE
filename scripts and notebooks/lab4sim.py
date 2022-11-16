import simpy
import numpy as np
import pandas as pd


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
        global queue_times
        queue_times.append(Tq)
        # print(time_stamp1, time_stamp2)


class Counter:
    def __init__(self, env, checkout, repairman):
        self.env = env
        self.checkout = checkout
        self.repairman = repairman

    def simulate_failure(self, repair_time_lam):
        repairman_req = self.repairman.request()
        yield repairman_req
        req = self.checkout.request()
        yield req
        repair_time = neg_exp(repair_time_lam)
        yield self.env.timeout(repair_time)
        self.checkout.release(req)
        self.repairman.release(repairman_req)


def neg_exp(lam):
    return np.random.exponential(1/lam)


def generate_custumers(env, checkout, checkout_lam, customer_interval_lam):
    while True:
        new_custumer = Custumer(env, checkout)
        env.process(new_custumer.checkout_process(checkout_lam))
        yield env.timeout(neg_exp(customer_interval_lam))


def generate_failure(env, counter, repair_time_lam, failure_interval_lam):
    while True:
        time_to_next_failure = neg_exp(failure_interval_lam)
        yield env.timeout(time_to_next_failure)
        env.process(counter.simulate_failure(repair_time_lam))


if __name__ == "__main__":
    queue_times = []
    checkout_lam = 1/2
    failure_interval_lam = 1/(4*60)
    repair_time_lam = 1/15
    customer_interval_lam = 1/3
    env = simpy.Environment()
    repairman = simpy.Resource(env, capacity=1)
    checkout = simpy.Resource(env, capacity=4)
    counter = Counter(env, checkout, repairman)
    env.process(generate_custumers(env, checkout,
                                   checkout_lam, customer_interval_lam))
    env.process(generate_failure(
        env, counter, repair_time_lam, failure_interval_lam))
    env.run(until=16*60)

    queue_times = np.array(queue_times)

    print(queue_times, queue_times.mean(), len(queue_times))
