# this is for display currently!!!!

from environment import OnePlayerOneStepEnv
from policy import TestPolicy
from world import OneStepWorld
from time import sleep

# w = OneStepWorld(TestPolicy)
# env = OnePlayerOneStepEnv(w)
# while 1:
#     obs_n = env.observe()
#     action_n = env.decide()
#     obs, reward, done, info = env.step(action_n)
#     while not done:
#         obs, reward, done, info = env.step(action_n)
#         action_n = env.decide()
#         # print(obs, reward, done, info)
#     sleep(1)
#     print(w.game.map.friendly_ships[0].coordinate())
#     env.reset()


import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten
from keras.optimizers import Adam

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=200000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99985
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Conv2D(32, (3, 3), input_shape=(
            1, 10, 10), activation='selu', data_format="channels_first"))
        model.add(Flatten())
        model.add(Dense(512, activation='selu'))
        model.add(Dense(64, activation='selu'))
        model.add(Dense(32, activation='selu'))
        model.add(Dense(self.action_size, activation='sigmoid'))
        model.compile(loss='categorical_crossentropy',
                      optimizer=Adam(lr=self.learning_rate))
        model.summary()
        sleep(2)
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, guide_action):
        if np.random.rand() <= self.epsilon:
            if np.random.rand() <= 0.3 or guide_action is None:
                return random.randrange(self.action_size)
            else:
                return guide_action
        act_values = self.model.predict(state)
        # exit()
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):

        x = []
        y = []
        
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            # print(self.model.predict(next_state))
            # exit()
            if not done:
                target = (reward + self.gamma *
                        #   np.amax(self.model.predict(next_state)))
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
        
            x.append(state.reshape(1, 10, 10))
            y.append(target_f.reshape(4))

        x = np.array(x)
        y = np.array(y)
        self.model.fit(x, y, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


EPISODES = 100000

if __name__ == "__main__":
    # env = gym.make('CartPole-v1')

    w = OneStepWorld(TestPolicy)
    env = OnePlayerOneStepEnv(w)

    state_size = 100
    action_size = 4
    agent = DQNAgent(state_size, action_size)
    # agent.load("./save/cartpole-dqn.h5")
    done = False
    batch_size = 1024

    for e in range(EPISODES):
        state = env.reset()
        # state = np.reshape(state, [1, state_size])
        state = np.reshape(state, [1, 1, 10, 10])

        s = 0
        t = 0
        for time in range(500):
            try:
                a_star_action = env.world.policy_agents[0].finda()
                a_star_action_i = env.world.action_space.index(a_star_action)
            except:
                a_star_action_i = None

            action = agent.act(state, a_star_action_i)
            # print(action)
            next_state, reward, done, _ = env.step([action], time)
            # reward = reward if not done else -100
            s += reward
            t += 1
            # next_state = np.reshape(next_state, [1, state_size])
            next_state = np.reshape(next_state, [1, 1, 10, 10])
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            if done:
                print("episode: {}/{}, score: {}, e: {:.2}, end_r: {}, path_len: {}"
                      .format(e, EPISODES, s / t, agent.epsilon, reward, time + 1))
                break
                
        if len(agent.memory) > 100000:
            agent.replay(batch_size)

    if e % 3000 == 0 and e > 0:
        agent.save("%d.ml" % e)