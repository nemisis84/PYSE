import simpy
import numpy as np
import pandas as pd
# from employee import Employee
# from custumer import Custumer


class Employee:

    def __init__(self, env, bins, threshold_value, shelf_available):
        self.env = env
        self.bins = bins
        self.threshold_value = threshold_value
        self.shelf_available = shelf_available

    def refill(self, env, id, refilling_time, moving_time_lambda):

        while True:
            for i in range(6):
                # Hold for travel between sections
                yield env.timeout(neg_exp(moving_time_lambda))

                items_in_shelf = self.bins[i].level
                shelf_capacity = self.bins[i].capacity

                if (items_in_shelf/shelf_capacity < self.threshold_value) and self.shelf_available[i]:
                    self.shelf_available[i] = False
                    self.bins[i].put(shelf_capacity-items_in_shelf)
                    yield env.timeout(refilling_time[i])
                    self.shelf_available[i] = True
                    # print(f"Employee {id} refilled at {self.env.now:.2f}!")


def generator_employeers(env, number_of_employees, bins, threshold_value, refilling_time, moving_time_lambda, shelf_available):
    id = 0
    while (id < number_of_employees):
        # Create the employee
        new_employee = Employee(env, bins, threshold_value, shelf_available)
        # Have the environment employee
        env.process(new_employee.refill(
            env, id, refilling_time, moving_time_lambda))
        yield env.timeout(0)
        id += 1


class Custumer:

    def __init__(self, env, time_to_pick_item, bins, checkout, MOS_scores):
        self.env = env
        self.bins = bins
        self.shopping_list = self.__generate_shopping_list()
        self.time_to_pick_item = time_to_pick_item
        self.items_bought = 0
        self.checkout = checkout
        self.MOS_scores = MOS_scores

    def __generate_shopping_list(self):
        return np.random.choice(5, 7)

    def calulate_MOS(self, shopping_list, items_bought, queue_time):
        v = items_bought/shopping_list.sum()

        if v == 1 and queue_time == 0:
            return 5

        if v > 0.9 and queue_time < 0.3:
            return 4

        if v > 0.8 and queue_time < 0.6:
            return 3

        if v > 0.7 and queue_time < 1:
            return 2

        return 1

    def custumer_shopping(self, env, id, moving_time_lambda, scanning_time, paying_time):
        for i in range(7):
            # Move to the next station
            yield env.timeout(neg_exp(moving_time_lambda))

            items = self.shopping_list[i]
            if items <= self.bins[i].level and items != 0:
                # print(bins[i].level)
                self.bins[i].get(items)
                # print(bins[i].level)
                if i == 0:
                    self.items_bought += 1  # pant
                else:
                    self.items_bought += items
                grabbing_time = self.time_to_pick_item[i]*items
                yield env.timeout(grabbing_time)

        timestamp_1 = env.now
        req = self.checkout.request()
        yield req
        timestamp_2 = env.now
        queue_time = timestamp_2 - timestamp_1
        checkout_time = scanning_time*self.items_bought + paying_time + queue_time
        yield env.timeout(checkout_time)
        self.checkout.release(req)
        self.MOS_scores.append(self.calulate_MOS(
            sum(self.shopping_list), self.items_bought, queue_time))
        # print(
        # f"Custumer {id} left the store at {self.env.now:.2f} with {self.items_bought} items after waiting {queue_time} minutes in the queue!")


def generator_custumers(env, custumer_interval_lambda, time_to_pick_item, bins, checkout, MOS_scores, moving_time_lambda, scanning_time, paying_time):
    id = 0
    while True:
        new_custumer = Custumer(env, time_to_pick_item,
                                bins, checkout, MOS_scores)
        env.process(new_custumer.custumer_shopping(
            env, id, moving_time_lambda, scanning_time, paying_time))
        yield env.timeout(neg_exp(custumer_interval_lambda))
        id += 1
        # print(f"Custumer {id} entered the store at {env.now:.2f}!")


# def cutumer_interval(lam):
#     return np.random.poisson(lam)


def neg_exp(lam):
    return np.random.exponential(1/lam)


def run_sim(number_of_employees, custumer_interval_lambda, moving_time_lambda, scanning_time, paying_time, time_to_pick_item, N, refilling_time):
    MOS_scores = []
    threshold_value = number_of_employees*0.05
    env = simpy.Environment()
    bins = []
    shelf_available = [True]*7
    for i in range(len(N)):
        bins.append(simpy.Container(env, init=N[i], capacity=N[i]))
    checkout = simpy.Resource(env, capacity=4)
    env.process(generator_custumers(env, custumer_interval_lambda,
                                    time_to_pick_item, bins, checkout, MOS_scores, moving_time_lambda, scanning_time, paying_time))

    env.process(generator_employeers(
        env, number_of_employees, bins, threshold_value, refilling_time, moving_time_lambda, shelf_available))

    env.run(until=16*60)
    return MOS_scores


if __name__ == "__main__":

    # number_of_employees = 1
    # threshold_value = number_of_employees*0.05
    # env = simpy.Environment()
    custumer_interval_lambda = 1/3
    moving_time_lambda = 2
    scanning_time = 0.1
    paying_time = 0.2
    time_to_pick_item = np.array([0.1, 0.15, 0.1, 0.1, 0.15, 0.1, 0.2])
    N = np.array([100, 150, 50, 150, 80, 40, 250])
    refilling_time = np.array([60, 36, 42, 42, 30, 60, 90])

    employeers_range = 10
    simulations = 3

    results = np.zeros((employeers_range, simulations))
    for n_employyers in range(1, employeers_range+1):
        for i in range(simulations):
            sim = np.array(run_sim(n_employyers, custumer_interval_lambda, moving_time_lambda,
                                   scanning_time, paying_time, time_to_pick_item, N, refilling_time))
            results[n_employyers-1][i] = sim.mean()

    print(results)
    df = pd.DataFrame(results, columns=[
                      f"Run {i}" for i in range(len(results[1]))])
    print(df)
    # bins = []
    # for i in range(len(N)):
    #     bins.append(simpy.Container(env, init=N[i], capacity=N[i]))

    # checkout = simpy.Resource(env, capacity=4)

    # env.process(generator_custumers(env, custumer_interval_lambda,
    #                                 time_to_pick_item, bins, checkout))

    # env.process(generator_employeers(env, number_of_employees, bins))

    # env.run(until=16*60)


# TODO:
# 1. sjekke at ting fungerer som de skal
# 2  Sjekke at ting stemmer overens med diagrammene
# 3. Fikse environment time
# 4. sjekke MOS score
# 5. Refleksjon og rapport
