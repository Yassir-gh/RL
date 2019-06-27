#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 09:49:22 2019

@author: yassir
"""

class Simulation1:
    
    
    def __init__(self):
        
        self.shell_1_obtained= False
        self.meterpreter_1_obtained_and_route_added= False
        self.shell_2_obtained= False
        self.shell_1_open=False
        self.shell_2_open=False
        self.root_hacked= False
        self.backgrounded= True
        self.last_opened_shell=None
        self.session= 0  #c'est pas forcément utile de garder l'indice de session je pense mais je le fais quand même
        
    def nmap_ports(self, ip):
        
        if self.shell_1_open==False and ip=='192.168.56.102':
            
            return """Starting Nmap 7.70 ( https://nmap.org ) at 2019-06-24 14:45 CEST
Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn
Nmap done: 1 IP address (0 hosts up) scanned in 3.04 seconds"""
        
        
        # je fais pas différent cas pour ce deuxième return car les 2 machines victimes ont la même configuration des ports
        return """Starting Nmap 7.70 ( https://nmap.org ) at 2019-06-25 11:46 CEST
Nmap scan report for 192.168.56.101
Host is up (0.0043s latency).
Not shown: 977 closed ports
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
23/tcp   open  telnet
25/tcp   open  smtp
53/tcp   open  domain
80/tcp   open  http
111/tcp  open  rpcbind
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
512/tcp  open  exec
513/tcp  open  login
514/tcp  open  shell
1099/tcp open  rmiregistry
1524/tcp open  ingreslock
2049/tcp open  nfs
2121/tcp open  ccproxy-ftp
3306/tcp open  mysql
5432/tcp open  postgresql
5900/tcp open  vnc
6000/tcp open  X11
6667/tcp open  irc
8009/tcp open  ajp13
8180/tcp open  unknown
Nmap done: 1 IP address (1 host up) scanned in 0.09 seconds"""

    def nmap_hosts(self):
        
        if self.shell_1_obtained== False:
            return """[*] exec: nmap -sP 192.168.56.0/24
Starting Nmap 7.70 ( https://nmap.org ) at 2019-06-24 14:16 CEST
Nmap scan report for 192.168.56.1
Host is up (0.00039s latency).
Nmap scan report for 192.168.56.101
Host is up (0.00096s latency).
Nmap done: 256 IP addresses (2 hosts up) scanned in 3.01 seconds"""
        
        if self.shell_1_obtained== True and self.shell_1_open==True: #le self.backgrounded doit être modifié par la fonction ssh_login je pense
            return """[*] exec: nmap -sP 192.168.56.0/24
Starting Nmap 4.53 ( http://insecure.org ) at 2019-05-31 00:31 EDT
Host 192.168.56.1 appears to be up.
MAC Address: 0A:00:27:00:00:00 (Unknown)
Host 192.168.56.100 appears to be up.
MAC Address: 08:00:27:82:94:FA (Cadmus Computer Systems)
Host 192.168.56.101 appears to be up.
Host 192.168.56.102 appears to be up.
MAC Address: 08:00:27:7D:34:9D (Cadmus Computer Systems)
Nmap done: 256 IP addresses (4 hosts up) scanned in 42.505 seconds"""

        if self.shell_2_obtained== True and self.shell_2_open==True: #le self.backgrounded doit être modifié par la fonction ssh_login je pense
            return """[*] exec: nmap -sP 192.168.56.0/24
Starting Nmap 4.53 ( http://insecure.org ) at 2019-05-31 00:31 EDT
Host 192.168.56.1 appears to be up.
MAC Address: 0A:00:27:00:00:00 (Unknown)
Host 192.168.56.100 appears to be up.
MAC Address: 08:00:27:82:94:FA (Cadmus Computer Systems)
Host 192.168.56.101 appears to be up.
Host 192.168.56.102 appears to be up.
MAC Address: 08:00:27:7D:34:9D (Cadmus Computer Systems)
Nmap done: 256 IP addresses (4 hosts up) scanned in 42.505 seconds"""
                    
        else:
            print("CAS NON PRIS EN COMPTE, REVOIR LA FONCTION 'Simulation.nmap_hosts' ")
            return ''
            
    def reinitialization(self):
        self.shell_1_obtained= False
        self.meterpreter_1_obtained_and_route_added= False
        self.shell_2_obtained= False
        self.shell_1_open=False
        self.shell_2_open=False
        self.root_hacked= False
        self.backgrounded= True
        
    def background(self):
        
        if self.backgrounded==True:
            return "Command not found"
        
        self.backgrounded=True
        self.shell_1_open=False
        self.shell_2_open=False
        return ''
    
    def whoami(self):
        if self.root_hacked==True:
            return 'root'
        else:
            return 'Not root'
    
    def ssh_login(self, ip):
        if self.backgrounded==False:
            return "Command not found"
        
        elif ip=='192.168.56.101':
            
            self.session+=1
            self.shell_1_obtained=True
            self.shell_1_open=True
            self.last_opened_shell="shell_1"
            self.backgrounded=False
            
            return """RHOSTS => 192.168.56.101
USERPASS_FILE => /usr/share/metasploit-framework/data/wordlists/root_userpass.txt
STOP_ON_SUCCESS => true
[+] 192.168.56.101:22 - Success: 'msfadmin:msfadmin' 'uid=1000(msfadmin) gid=1000(msfadmin) groups=4(adm),20(dialout),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),107(fuse),111(lpadmin),112(admin),119(sambashare),1000(msfadmin) Linux metasploitable 2.6.24-16-server #1 SMP Thu Apr 10 13:58:00 UTC 2008 i686 GNU/Linux '
[*] Command shell session """+str(self.session)+ """ opened (192.168.56.1:43183 -> 192.168.56.101:22) at 2019-06-24 15:54:31 +0200
[*] Scanned 1 of 1 hosts (100% complete)
[*] Auxiliary module execution completed"""
                    
        elif ip=="192.168.56.102" and self.shell_1_obtained==True and self.meterpreter_1_obtained_and_route_added==True:
            
            self.session+=1
            self.shell_2_obtained=True
            self.shell_2_open=True
            self.last_opened_shell="shell_2"
            self.backgrounded=False
            
            return """RHOSTS => 192.168.56.102
USERPASS_FILE => /usr/share/metasploit-framework/data/wordlists/root_userpass.txt
STOP_ON_SUCCESS => true
[+] 192.168.56.102:22 - Success: 'msfadmin:msfadmin' 'uid=1000(msfadmin) gid=1000(msfadmin) groups=4(adm),20(dialout),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),107(fuse),111(lpadmin),112(admin),119(sambashare),1000(msfadmin) Linux metasploitable 2.6.24-16-server #1 SMP Thu Apr 10 13:58:00 UTC 2008 i686 GNU/Linux '
[*] Command shell session """+str(self.session)+ """ opened (192.168.56.1-192.168.56.101:0 -> 192.168.56.102:22) at 2019-06-25 10:25:14 +0200
[*] Scanned 1 of 1 hosts (100% complete)
[*] Auxiliary module execution completed"""
        else:
            return ''
        
        
    def dirtyCow(self):
        if self.backgrounded==True or self.shell_1_open==True:
            return "Command not found"
        
        elif self.shell_2_open==True:
            
            self.root_hacked=True
            
            return """DirtyCow root privilege escalation
Backing up /usr/bin/passwd to /tmp/bak
mmap b7d9f000

ptrace 0

            
(___)                                   
(o o)_____/                             
@@ `     \                            
\ ____, //usr/bin/passwd                          
//    //                              
^^    ^^                               
DirtyCow root privilege escalation
Backing up /usr/bin/passwd to /tmp/bak
mmap b7d9f000

madvise 0"""
                    
        else:
            print("CAS NON PRIS EN COMPTE, REVOIR LA FONCTION 'Simulation.dirtyCow' ")
            return ''
        
    def pivot_autoroute(self):
        if self.backgrounded==False or self.shell_1_obtained==False or self.last_opened_shell=="meterpreter_1":
            return "Coommand not found"
        
        elif self.shell_1_obtained==True and self.backgrounded==True:
            self.meterpreter_1_obtained_and_route_added=True
            self.last_opened_shell="meterpreter_1"
            self.session+=1
            
            return """[*] Meterpreter session """+str(self.session)+ """ opened (192.168.56.1:46550 -> 192.168.56.101:50174) at 2019-06-25 11:02:30 +0200
[*] Command stager progress: 100.00% (773/773 bytes)
[*] Post module execution completed
[*] Running module against metasploitable.localdomain
[*] Searching for subnets to autoroute.
[+] Route added to subnet 192.168.56.0/255.255.255.0 from host's routing table.
[*] Post module execution completed"""
        
        else:
            print("CAS NON PRIS EN COMPTE, REVOIR LA FONCTION 'Simulation.autoroute' ")
            return ''
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        