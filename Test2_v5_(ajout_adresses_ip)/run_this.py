# coding=utf-8

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
        print('\n\nPartie ' + str(episode))
        print('----------------------------------------------------------------\n')
        # initial observation
        #observation = env.reset()
        observation= RL.nmap()

        while True:
            # fresh env
            #env.render()

            # RL choose action based on observation
            action = RL.choose_action(observation)

            # RL take action and get next observation and reward
            #observation_, reward, done = env.step(action)
            observation_, reward, done = RL.step(action, observation) # j'ai ajouté l'argument "observation" dans cette version

            # RL learn from this transition
            RL.learn(str(observation), action, reward, str(observation_))

            # swap observation
            observation = observation_

            # break while loop when end of this episode
            if done:
                RL.background() # ce "background" prend-t-il en compte le cas où on a ouvert un shell dans un shell par exemple ?
                break
            
            print('\n\n------\n\n')

    # end of game
    print('game over')
    #env.destroy()

if __name__ == "__main__":
    #env = Maze()
    RL = QLearningTable(victim_ip_address='192.168.56.101', local_ip_address='192.168.56.1', learning_rate=0.01, reward_decay=0.9, e_greedy=0.6)
    update()

    #env.after(100, update)
    #env.mainloop()