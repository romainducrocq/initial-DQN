from env import Env, View, RES
from dqn.config import HYPER_PARAMS
from dqn import make_env, Networks
from pyglet.gl import *

import os
import argparse
import numpy as np
from functools import reduce

from torch import device, cuda


class Observe(View):
    def __init__(self, width, height, name, env, args):
        os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
        os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu

        super(Observe, self).__init__(width, height, name, make_env(env=env, repeat=HYPER_PARAMS['repeat'], max_episode_steps=args.max_steps))

        self.network = getattr(Networks, {
            "DQNAgent": "DeepQNetwork",
            "DoubleDQNAgent": "DeepQNetwork",
            "DuelingDoubleDQNAgent": "DuelingDeepQNetwork"
        }[args.dir.split('_')[0].split('save/')[1]])(
            device(("cuda:" + args.gpu) if cuda.is_available() else "cpu"),
            float(args.dir.split('_')[1].split('lr')[1]),
            reduce(lambda x, y: x * y, list(self.env.observation_space.shape)),
            self.env.action_space.n
        )

        self.network.load(args.dir)

        self.obs = np.zeros(reduce(lambda x, y: x * y, list(self.env.observation_space.shape)), dtype=np.float32)

    def setup(self):
        self.obs = self.env.reset()
        self.polygons_track = self.env.reset_render()

    def loop(self):
        action = self.network.actions([self.obs.tolist()])[0]

        self.obs, _, done, _ = self.env.step(action)
        if done:
            self.setup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initial DQN - OBSERVE")
    parser.add_argument('-dir', type=str, default='', help='Directory', required=True)
    parser.add_argument('-max_steps', type=int, default=HYPER_PARAMS['max_episode_steps'], help='Max episode steps')
    parser.add_argument('-gpu', type=str, default='0', help='GPU #')

    play = Observe(RES[0], RES[1], "Initial DQN - OBSERVE", Env(), parser.parse_args())
    pyglet.clock.schedule_interval(play.on_draw, 0.002)
    pyglet.app.run()
