import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


class Custumer:
    def __init__(self, env, checkout):
        self.env = env
        self.checkout = checkout
        self.A = 1

    def checkout_process(self, checkout_lam):
        global queue_times, counters_working, waiting_time_and_counters
        time_stamp1 = self.env.now
        req = self.checkout.request()
        yield req
        time_stamp2 = self.env.now
        Tq = time_stamp2-time_stamp1
        if not counters_working in waiting_time_and_counters:
            waiting_time_and_counters[counters_working] = []
        waiting_time_and_counters[counters_working] += [Tq]
        checkout_time = neg_exp(checkout_lam)
        yield self.env.timeout(checkout_time)
        self.checkout.release(req)
        queue_times.append(Tq)


class Counter:
    def __init__(self, env, checkout, repairman):
        self.env = env
        self.checkout = checkout
        self.repairman = repairman

    def simulate_failure(self, repair_time_lam):
        timestamp = False

        req = self.checkout.request(priority=0)
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
            yield env.timeout(0.001)


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
    checkout = simpy.PriorityResource(env, capacity=4)
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


def calculate_queue_time(d: list):

    mean = []
    std = []
    for key in d.keys():
        if bool(d[key]):
            mean.append(np.array(d[key]).mean())
            std.append(np.array(d[key]).std())

    return mean, std


def C_formula(A, n):
    upper = A**(n)*n/(math.factorial(n)*(n-A))
    lower = 0
    for i in range(n):
        lower += A**(i)/math.factorial(i)
    lower += A**(n)*n/(math.factorial(n)*(n-A))
    return upper/lower


def expected_waiting_time(A, mu, n):
    return C_formula(A, n)/(mu*(n-A))


if __name__ == "__main__":

    queue_times_list = []
    down_time_list = []
    waiting_time_and_counters = {}

    A_list = []
    for i in range(10*365):
        print(f"Run{i}")

        queue_times = []
        down_time = 0
        counters_working = 4
        counters_working_when_custumer_arrives = []
        simulate()
        queue_times_list.append(np.array(queue_times))
        down_time_list.append(down_time)

    queue_times_list = np.hstack(np.array(queue_times_list))
    A_list = np.hstack(np.array(A_list))
    mean, std = calculate_queue_time(waiting_time_and_counters)
    mean.reverse(), std.reverse()
    print(f"Mean waiting time simulation: {mean} std: {std}")
    print(
        f'Results:\nAvailability A = {A_list.mean()}\nA std = {A_list.std()}\nMean queue time T_q = {queue_times_list.mean()}\nQueue time std={queue_times_list.std()}')

    # Analytical approach
    mu = 1/2
    lam = 1/3
    T = []
    for i in range(4):
        T.append(round(expected_waiting_time(lam/(mu), mu, i+1), 7))
    fig, ax = plt.subplots()
    ax.scatter(range(1, 5), T)
    print(f"Wating time analytical:{T}")
    ax.grid()
    ax.set_xlim((0.5, 4.5))
    ax.set_ylim((-1, 12))
    ax.set_xlabel('Counters')
    ax.set_ylabel('Waiting time')
    ax.set_title("Waiting times with different amount of counters")
    print(len(mean), len(std))
    ax.errorbar(range(1, len(mean)+1), mean,
                yerr=list(std), fmt="o", color="red")
    ax.legend(["Simulation", "Analytical"])
    plt.show()
