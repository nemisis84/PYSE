import simpy
import numpy as np


class Employee:

    def __init__(self, env, bins, threshold_value):
        self.env = env
        self.bins = bins
        self.threshold_value = threshold_value

    def refill(self, env, id, refilling_time, moving_time_lambda):

        while True:
            for i in range(6):
                # Hold for travel between sections
                yield env.timeout(neg_exp(moving_time_lambda))

                items_in_shelf = self.bins[i].level
                shelf_capacity = self.bins[i].capacity

                if (items_in_shelf/shelf_capacity < self.threshold_value):

                    self.bins[i].put(shelf_capacity-items_in_shelf)
                    yield env.timeout(refilling_time[i])

                    # print(f"Employee {id} refilled at {self.env.now:.2f}!")
