import gym
from gym import spaces
from gym.envs.registration import EnvSpec
import numpy as np

# environment for all agents in the multiagent world
# currently code assumes that no agents will be created/destroyed at runtime!
class OneStepEnv(gym.Env):
    def __init__(self, world):

        self.world = world
        self.agents = self.world.policy_agents


    @property
    def action_space(self):
        return self.world.action_space

    @property
    def observation_space(self):
        return self.world.observation_space

    def step(self, action_n):
        return self.world.step(action_n)

    def reset(self):
        # reset world
        return self.world.reset()

    # render environment
    def render(self, **kwargs):
        self.world.render()

    def observe(self):
        return self.world.observe()

    def decide(self):
        return self.world.decide()

class TestEnv(OneStepEnv):
    def __init__(self, world):
        super().__init__(world)

class OnePlayerEnv(OneStepEnv):
    def step(self, action_n):
        time = 0
        obs_n, reward_n, done_n, info_n = self.world.step(action_n, time)
        return obs_n[0], reward_n[0], done_n[0], {}

    def render(self, **kwargs):
        pass
