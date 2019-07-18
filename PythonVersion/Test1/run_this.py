
#from maze_env import Maze
from RL_brain import QLearningTable
import time



def update():
    
    RL.nmap_hosts()
    
    episode=0
    successive_victory=0
    
    #for episode in range(100):
    while successive_victory != 1:
        episode+=1
    
        print('\n\n Partie ' + str(episode))
        print('----------------------------------------------------------------\n')
        # initial observation
        #observation = env.reset()
        observation= RL.nmap_ports()

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
            
            RL.update_actions(observation_)
            RL.update_q_tables(observation_)

            # RL learn from this transition
            RL.learn(str(observation), action, reward, str(observation_))

            # swap observation
            observation = observation_

            # break while loop when end of this episode
            if done:
                
                if reward==1:
                    successive_victory+=1
                else:
                    successive_victory=0
                    
                RL.background()
                RL.reinitialization()
                break
            
            print('\n\n------')

    # end of game
    print('game over')
    #env.destroy()

if __name__ == "__main__":
    #env = Maze()
    
    start_time = time.time()
    
    RL = QLearningTable(victim_ip_address='192.168.56.101', local_ip_address='192.168.56.1', learning_rate=0.1, reward_decay=0.9, e_greedy=0.95, simulation=False )
    update()
    
    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- %s minutes ---" % str( (int(time.time() - start_time)/60) ) )

    #env.after(100, update)
    #env.mainloop()