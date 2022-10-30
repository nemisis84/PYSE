
import numpy as np
import pandas as pd


def calulate_MOS(v):

    if v == 1:
        return 5

    if v > 0.9:
        return 4

    if v > 0.8:
        return 3

    if v > 0.7:
        return 2

    return 1


def calculate_results(a, b, c, stations, employees, special_case):

    results = np.zeros((stations, 3))
    MOS_scores = np.zeros(stations)
    v = np.zeros(stations)
    for i in range(stations):
        if special_case[i]:

            p_0 = b[i]/(b[i]+c[i])
            p_t = None
            p_n = c[i]/(b[i]+c[i])*employees
        else:

            p_0 = a[i]*b[i]/((a[i]+c[i])*(b[i]+c[i]))
            p_t = b[i]*c[i]/((a[i]+c[i])*(b[i]+c[i]))
            p_n = c[i]/(b[i]+c[i])*employees

        results[i] = [p_0, p_t, p_n]
        v[i] = 1-p_0
        MOS_scores[i] = calulate_MOS(v[i])
    df = pd.DataFrame(list(zip(a, b, c, results[:, 0], v, MOS_scores)), columns=[
                      "a", "b", "c", "p_0", "v", "MOS"])

    return df, MOS_scores


if __name__ == "__main__":

    lam = 1

    N = np.array([100, 150, 50, 150, 80, 40, 250])
    U = np.array([60, 36, 42, 42, 30, 60, 90])
    stations = 7
    max_employees = 15
    MOS_table = np.zeros((stations, max_employees))

    for employees in range(1, max_employees+1):
        p_i = 0.05*employees

        a = [lam/(p_i*n-2) for n in N]
        b = [lam/(n-p_i*n) for n in N]
        c = [1/u*employees for u in U]

        special_case = np.zeros(stations)

        for i in range(stations):
            if p_i*N[i] < 3:
                special_case[i] = 1

        df, MOS_scores = calculate_results(
            a, b, c, stations, employees, special_case)
        MOS_table[:, employees-1] = MOS_scores
    df1 = pd.DataFrame(MOS_table, columns=range(1, 16))
    print(df1)
