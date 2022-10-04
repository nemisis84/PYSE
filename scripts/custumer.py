import simpy
import numpy as np


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
            yield travel_time(moving_time_lambda)  # Move to the next station

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
        yield checkout_time

        print(f"Custumer {id} left the store at {self.env.now:.2f}!")