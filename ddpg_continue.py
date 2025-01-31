from environment import OnePlayerEnv
from policy import TestPolicy
from world import ContinuousWorld
from time import sleep
from time import time as now

import random
import numpy as np

import gym
from gym import wrappers

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, Concatenate, Conv2D, MaxPool2D, AvgPool2D
from keras.optimizers import Adam

from rl.agents import DDPGAgent
from rl.memory import SequentialMemory
from rl.random import OrnsteinUhlenbeckProcess


EPISODES = 100000

if __name__ == "__main__":
    # env = gym.make('CartPole-v1')

    w = ContinuousWorld(TestPolicy, obsticle_moving=False)
    env = OnePlayerEnv(w)

    state_size = 100
    action_size = 4
    # agent.load("./save/cartpole-dqn.h5")
    done = False
    batch_size = 1024

    # Next, we build a very simple model.
    actor = Sequential()
    actor.add(Conv2D(filters=8, kernel_size=(3, 3), activation="relu", input_shape=(1, 100, 100),
                    data_format="channels_first"))
    actor.add(Conv2D(filters=2, kernel_size=(3, 3),
                    activation="relu", data_format="channels_first"))
    # actor.add(MaxPool2D(2, 2, data_format="channels_first"))
    actor.add(AvgPool2D(2, 2, data_format="channels_first"))
    actor.add(Flatten())
    actor.add(Dense(256))
    actor.add(Activation('relu'))
    actor.add(Dense(32))
    actor.add(Activation('relu'))
    actor.add(Dense(16))
    actor.add(Activation('tanh'))
    actor.add(Dense(1))
    actor.add(Activation('sigmoid'))
    actor.summary()

    action_input = Input(shape=(1,), name='action_input')
    observation_input = Input(
        shape=(1, 100, 100), name='observation_input')
    x = Conv2D(filters=8, kernel_size=(3, 3), activation="relu",
                     data_format="channels_first")(observation_input)
    x = Conv2D(filters=2, kernel_size=(3, 3), activation="relu",
                     data_format="channels_first")(x)
    # x = MaxPool2D(2, 2, data_format="channels_first")(x)
    x = AvgPool2D(2, 2, data_format="channels_first")(x)
    x = Flatten()(x)
    x = Dense(255)(x)
    x = Activation('relu')(x)
    x = Concatenate()([x, action_input])
    x = Dense(255)(x)
    x = Activation('relu')(x)
    x = Dense(32)(x)
    x = Activation('relu')(x)
    x = Dense(16)(x)
    x = Activation('sigmoid')(x)
    x = Dense(1)(x)
    x = Activation('linear')(x)
    critic = Model(inputs=[action_input, observation_input], outputs=x)
    critic.summary()

    def monkey_patching_forward(self, observation):
        state = self.memory.get_recent_state(observation)
        action = self.select_action(state)
        self.recent_observation = observation
        self.recent_action = action

        if random.random() < 0.1:
            action = env.agents[0].pathGuide().angular_speed / 360
            action = np.array([action])
            action = np.reshape(action, self.recent_action.shape)
            self.recent_action = action
            return action

        return action

    DDPGAgent.forward = monkey_patching_forward

    memory = SequentialMemory(limit=100000, window_length=1)
    agent = DDPGAgent(nb_actions=1, actor=actor, critic=critic, critic_action_input=action_input,
                    memory=memory, nb_steps_warmup_critic=30000, nb_steps_warmup_actor=30000,
                    gamma=.99, target_model_update=1e-3)

    agent.compile([Adam(lr=1e-5), Adam(lr=1e-5)], metrics=['mae'])
    agent.load_weights('ddpg_{}_weights.h5f'.format("continous"))
    agent.fit(env, nb_steps=800000, visualize=False, verbose=1)

    # After training is done, we save the final weights.
    agent.save_weights('ddpg_{}_weights.h5f'.format("continous"), overwrite=True)

    # Finally, evaluate our algorithm for 5 episodes.
    agent.test(env, nb_episodes=5, visualize=False, nb_max_episode_steps=1000)