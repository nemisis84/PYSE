import simpy
import numpy as np
# from employee import Employee
# from custumer import Custumer


class Employee:

    def __init__(self, env, bins):
        self.env = env
        self.bins = bins

    def refill(self, env, id):
        global refilling_time, number_of_employees, moving_time_lambda, N, travel_time
        threshold_value = number_of_employees*0.05
        for i in range(6):
            # Hold for travel between sections
            yield env.timeout(travel_time(moving_time_lambda))
            if (self.bins[i].capacity/N[i] < threshold_value):
                req = self.bins[i].put(N[i]-self.bins[i])
                yield env.timeout(refilling_time[i])
            print(f"Employee {id} refilled at {self.env.now:.2f}!")


class Custumer:

    def __init__(self, env, time_to_pick_item, bins, checkout):
        self.env = env
        self.bins = bins
        self.shopping_list = self.__generate_shopping_list()
        self.time_to_pick_item = time_to_pick_item
        self.items_bought = 0
        self.checkout = checkout

    def __generate_shopping_list(self):
        return np.random.choice(5, 7)

    def calulate_MOS(shopping_list, items_bought, que_time):
        v = items_bought/sum(shopping_list)

        if v == 1 and que_time == 0:
            return 5

        if v > 0.9 and que_time < 0.3:
            return 4

        if v > 0.8 and que_time < 0.6:
            return 3

        if v > 0.7 and que_time < 1:
            return 2

        return 1

    def custumer_shopping(self, env, id):
        global moving_time_lambda, scanning_time, paying_time, travel_time
        for i in range(7):
            # Move to the next station
            yield env.timeout(travel_time(moving_time_lambda))

            items = self.shopping_list[i]
            if items >= self.bins[i].level:
                req = self.bins[i].get(items)
                self.items_bought += req
                yield req
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
        print(f"Custumer {id} left the store at {self.env.now:.2f}!")


def generator_employeers(env, number_of_employees, bins):
    id = 0
    while (id < number_of_employees):
        new_employee = Employee(env, bins)  # Create the employee
        # Have the environment employee
        env.process(new_employee.refill(env, id))
        yield env.timeout(0)
        id += 1


def generator_custumers(env, custumer_interval_lambda, time_to_pick_item, bins, checkout):
    id = 0
    while True:
        new_custumer = Custumer(env, time_to_pick_item, bins, checkout)
        env.process(new_custumer.custumer_shopping(env, id))
        yield env.timeout(cutumer_interval(custumer_interval_lambda))
        id += 1
        print(f"Custumer {id} entered the store at {env.now:.2f}!")


def cutumer_interval(lam):
    return np.random.poisson(lam)


def travel_time(lam):
    return np.random.exponential(1/lam)


if __name__ == "__main__":
    number_of_employees = 3
    env = simpy.Environment()
    custumer_interval_lambda = 1/3
    moving_time_lambda = 2
    scanning_time = 0.1
    paying_time = 0.2
    time_to_pick_item = np.array([0.1, 0.15, 0.1, 0.1, 0.15, 0.1, 0.2])
    N = np.array([100, 150, 50, 150, 80, 40, 250])
    refilling_time = np.array([60, 36, 42, 42, 30, 60, 90])
    bins = []
    for i in range(len(N)):
        bins.append(simpy.Container(env, init=N[i], capacity=N[i]))

    checkout = simpy.Resource(env, capacity=4)

    env.process(generator_custumers(env, custumer_interval_lambda,
                                    time_to_pick_item, bins, checkout))

    env.process(generator_employeers(env, number_of_employees, bins))

    env.run(until=500)


# TODO:
# 1. sjekke at ting fungerer som de skal
# 2  Sjekke at ting stemmer overens med diagrammene
# 3. Fikse environment time
# 4. sjekke MOS score
# 5. Refleksjon og rapport
