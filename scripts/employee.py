import simpy
import numpy as np


# Create the negative exponential distributet T__t travel time between sections


class Employee:

    def __init__(self, env, bins):
        self.env = env
        self.bins = bins

    def refill(self, env, id):
        global refilling_time, number_of_employees, moving_time_lambda, travel_time
        threshold_value = number_of_employees*0.05
        for i in range(6):
            # Hold for travel between sections
            yield env.timeout(travel_time(moving_time_lambda))
            if (self.bins[i]/N[i] < threshold_value):
                req = self.bins[i].put(N[i]-self.bins[i])
                yield env.timeout(refilling_time[i])
            print(f"Employee {id} refilled at {self.env.now:.2f}!")
