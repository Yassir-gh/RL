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
import time



def update():
    for episode in range(100):
        print('\n\n Partie ' + str(episode))
        print('----------------------------------------------------------------\n')
        # initial observation
        #observation = env.reset()
        observation= RL.nmap()

        while True:
            # fresh env
            #env.render()
            
            RL.update_actions(observation)
            
            RL.update_q_tables(observation)
            
            # RL choose action based on observation
            action = RL.choose_action(str(observation))

            # RL take action and get next observation and reward
            #observation_, reward, done = env.step(action)
            observation_, reward, done = RL.step(action, observation)
            
            time.sleep(5)
            
            RL.update_actions(observation_)
            RL.update_q_tables(observation_)

            # RL learn from this transition
            RL.learn(str(observation), action, reward, str(observation_))

            # swap observation
            observation = observation_

            # break while loop when end of this episode
            if done:
                RL.background()
                break
            
            print('\n\n------')

    # end of game
    print('game over')
    #env.destroy()

if __name__ == "__main__":
    #env = Maze()
    RL = QLearningTable(actions=["samba","ftp1","mysql"], learning_rate=0.01, reward_decay=0.9, e_greedy=0.7)
    update()

    #env.after(100, update)
    #env.mainloop()