"""
Reinforcement learning maze example.

Red rectangle:          explorer.
Black rectangles:       hells       [reward = -1].
Yellow bin circle:      paradise    [reward = +1].
All other states:       ground      [reward = 0].

This script is the main part which controls the update method of this example.
The RL is in RL_brain.py.

View more on my tutorial page: https://morvanzhou.github.io/tutorials/
"""

#from maze_env import Maze
from RL_brain import QLearningTable



def update():
    for episode in range(100):
        print('----------------------------------------------------------------\n')
        # initial observation
        #observation = env.reset()
        observation= RL.nmap()

        while True:
            # fresh env
            #env.render()

            # RL choose action based on observation
            action = RL.choose_action(str(observation))

            # RL take action and get next observation and reward
            #observation_, reward, done = env.step(action)
            observation_, reward, done = RL.step(action)

            # RL learn from this transition
            RL.learn(str(observation), action, reward, str(observation_))

            # swap observation
            observation = observation_

            # break while loop when end of this episode
            if done:
                break

    # end of game
    print('game over')
    #env.destroy()

if __name__ == "__main__":
    #env = Maze()
    RL = QLearningTable(actions=["samba","ftp1","mysql"], learning_rate=0.01, reward_decay=0.9, e_greedy=0.6)
    update()

    #env.after(100, update)
    #env.mainloop()