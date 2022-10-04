import simpy
import numpy as np


class TelefonExchange:
    def __init__(self, env):
        self.env = env

        ### PARAMETERS ###
        self.NEXT_CALL = 30*60
        self.MAX_CONNECTION_TIME = 15
        self.FIXED_CONNECTION_TIME = 0.2
        self.DISCONNECTION_TIME = 0.2
        self.AVG_VARIABLE_CONNECTION_TIME = 3
        self.AVG_CONVERSATION_TIME = 3*60

        ### COUNTERS ###
        self.successful_Calls = 0
        self.lost_Calls = 0

        ### LISTS TO STORE SAMPLES ###
        self.call_Duration = []
        self.inter_Call_Times = []
        self.connection_Times = []
        self.conversation_Times = []
        self.subs = []  # A 2D list with [Subscriber, Timer] pairs

        self.t = None  # A variable to store the dedicated timer-process for a given subscriber

    def subscriber(self, ID):
        while True:
            try:
                ### WAIT FOR NEXT CALL ###
                wait_NEXT_CALL = np.random.exponential(self.NEXT_CALL)
                self.inter_Call_Times.append(wait_NEXT_CALL)
                yield self.env.timeout(wait_NEXT_CALL)

                ### START A DEDICATED TIMER FOR A SUBSCRIBER ###
                self.t = self.env.process(self.timer(ID))
                self.subs[ID][1] = self.t
                call_Start = self.env.now

                ### ESTABLISH CONNECTION ###
                wait_Connection = self.FIXED_CONNECTION_TIME + \
                    np.random.exponential(self.AVG_VARIABLE_CONNECTION_TIME)
                self.connection_Times.append(wait_Connection)
                yield self.env.timeout(wait_Connection)

                ### CONNECTION SUCCESSFULLY ESTABLISHED ###
                # Interrupt the subscribers dedicated timer
                self.subs[ID][1].interrupt()

                ### CONVERSATION HAPPENING ###
                conversation_Time = np.random.exponential(
                    self.AVG_CONVERSATION_TIME)
                self.conversation_Times.append(conversation_Time)
                yield self.env.timeout(conversation_Time)

                ### TEAR DOWN OF CONNECTION ###
                yield self.env.timeout(self.DISCONNECTION_TIME)
                self.successful_Calls += 1
                # Update the duration of the call, i.e. connection establishment + conversation +  tear down of connection
                self.call_Duration.append(self.env.now - call_Start)

            except simpy.Interrupt:
                ### TEAR DOWN OF CONNECTION INITAIATED BY THE DEDICATED TIMER ###
                self.lost_Calls += 1
                yield self.env.timeout(self.DISCONNECTION_TIME)

    def timer(self, ID):
        try:
            ### TIMER STARTED INITIATED BY SUBSCRIBER ###
            yield self.env.timeout(self.MAX_CONNECTION_TIME)
            # Timeout reached, interrupt dedicated subscriber and initiate tear down
            self.subs[ID][0].interrupt()

        except simpy.Interrupt:
            ### CONNECTION ESTABLISHED AND TIMER INTERRUPTED FROM DEDICATED SUBSCRIBER ###
            pass

    def startSimulation(self, N):
        ### SPAWN N SUBSCRIBERS ###
        for i in range(N):
            self.action = self.env.process(self.subscriber(i))
            self.subs.append([self.action, None])


env = simpy.Environment()

TE = TelefonExchange(env)
TE.startSimulation(20)  # Start simulation and spawn 20 subscribers

SIM_TIME = 30*24*60*60  # Simulate for 30 days

env.run(until=SIM_TIME)

print(
    '|-----------------------------Exercise 4.1 \033[93ma)\033[0m, b), \033[93mc)\033[0m, \033[92md)\033[0m-----------------------------|\n')
print('\033[93mNumber of call attempts lost: %g\033[0m' % (TE.lost_Calls))
print('\033[92mP(call loss)) = %g\033[0m' %
      (TE.lost_Calls/(TE.successful_Calls+TE.lost_Calls)))
print('|------------------------------|---Average---|---Standard Error---|---MIN---|---MAX---|\n')
print('|---------\033[93mCALL DURATION\033[0m--------|---\033[93m%.3f\033[0m---|------%.6f------|--%.3f--|-%.2f-|' % (np.average(np.array(TE.call_Duration)),
                                                                                                                      np.std(np.array(TE.call_Duration))/np.sqrt(len(TE.call_Duration)), np.min(np.array(TE.call_Duration)), np.max(np.array(TE.call_Duration))))
print('|-------INTER CALL TIME--------|---%.2f---|------%.5f------|-%.5f-|-%.1f-|' % (np.average(np.array(TE.inter_Call_Times)),
                                                                                      np.std(np.array(TE.inter_Call_Times))/np.sqrt(len(TE.inter_Call_Times)), np.min(np.array(TE.inter_Call_Times)), np.max(np.array(TE.inter_Call_Times))))
print('|---CONNECTION ESTABLISHMENT---|---%.5f---|------%.6f------|--%.3f--|-%.4f-|' % (np.average(np.array(TE.connection_Times)),
                                                                                        np.std(np.array(TE.connection_Times))/np.sqrt(len(TE.connection_Times)), np.min(np.array(TE.connection_Times)), np.max(np.array(TE.connection_Times))))
print('|-----CONVERSATION DURATION----|---%.3f---|------%.6f------|--%.3f--|-%.2f-|\n' % (np.average(np.array(TE.conversation_Times)),
                                                                                          np.std(np.array(TE.conversation_Times))/np.sqrt(len(TE.conversation_Times)), np.min(np.array(TE.conversation_Times)), np.max(np.array(TE.conversation_Times))))

env1 = simpy.Environment()

TE1 = TelefonExchange(env1)
### RE-ASSIGN PARAMETERS ###
TE1.MAX_CONNECTION_TIME = 30
TE1.AVG_VARIABLE_CONNECTION_TIME = 0.2
TE1.startSimulation(20)
SIM_TIME = 30*24*60*60
env1.run(until=SIM_TIME)

print('|-----------------------------------Exercise 4.1 e)-----------------------------------|\n')
print('Number of call attempts lost: %g' % (TE1.lost_Calls))
print('P(call loss)) = %g\n' %
      (TE1.lost_Calls/(TE1.successful_Calls+TE1.lost_Calls)))
