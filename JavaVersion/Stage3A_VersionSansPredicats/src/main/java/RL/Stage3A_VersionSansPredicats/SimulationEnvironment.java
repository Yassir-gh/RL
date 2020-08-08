package RL.Stage3A_VersionSansPredicats;

import java.util.ArrayList;

public class SimulationEnvironment {
	
	public ArrayList<String> ip_addresses_list = null;
	public String ip_vulnerable= "";
	public String ip_visible="";
	public ArrayList<Machine> machines = new ArrayList<Machine>();
	public boolean root_hacked= false;
	public boolean backgrounded= true;
	public String last_opened_shell= null;
	public int session= 0;
	
	public SimulationEnvironment(ArrayList<String> ip_addresses_list, String ip_vulnerable, String ip_visible) {
		this.ip_addresses_list= ip_addresses_list;
		this.ip_vulnerable= ip_vulnerable;
		this.ip_visible= ip_visible;
		
		for(int i=0; i<ip_addresses_list.size(); i++) {
			ArrayList<String> neighbors= new ArrayList<String>();
			
			if(i!=0 && i!=(ip_addresses_list.size()-1) ) {
				neighbors.add(ip_addresses_list.get(i-1));
				neighbors.add(ip_addresses_list.get(i+1));
			}
			if(i==0) {
				neighbors.add(ip_addresses_list.get(i+1));
			}
			if(i==(ip_addresses_list.size()-1) ) {
				neighbors.add(ip_addresses_list.get(i-1));
			}
			
			this.machines.add(new Machine(ip_addresses_list.get(i), neighbors) );
		}
		
		for(Machine machine: this.machines) {
			machine.neighbors_machines= this.machines;
		}
		
	}

	public String nmap_hosts() {
		// TODO Auto-generated method stub
		
		for(Machine machine: this.machines) {
			if(machine.shell_open == true) {
				return machine.nmap_hosts(this.ip_visible);
			}
		}
		
		return "[*] exec: nmap -sP 192.168.56.0/24 \n Starting Nmap 7.70 ( https://nmap.org ) at 2019-06-24 14:16 CEST \n Nmap scan report for 192.168.56.1 Host is up (0.00039s latency). \n Nmap scan report for " + this.ip_visible + " \n Host is up (0.00096s latency). \n Nmap done: 256 IP addresses (2 hosts up) scanned in 3.01 seconds";
	}

	public String nmap_ports(String ip) {
		// TODO Auto-generated method stub
		if(this.backgrounded==true && ip==this.ip_visible) {
			return "Starting Nmap 7.70 ( https://nmap.org ) at 2019-06-25 11:46 CEST \n Nmap scan report for 192.168.56.101 \n Host is up (0.0043s latency). \n Not shown: 977 closed ports \n PORT     STATE SERVICE \n21/tcp   open  ftp \n22/tcp   open  ssh \n23/tcp   open  telnet \n25/tcp   open  smtp \n53/tcp   open  domain \n80/tcp   open  http \n111/tcp  open  rpcbind \n139/tcp  open  netbios-ssn \n445/tcp  open  microsoft-ds \n512/tcp  open  exec \n513/tcp  open  login \n514/tcp  open  shell \n1099/tcp open  rmiregistry \n1524/tcp open  ingreslock \n2049/tcp open  nfs \n2121/tcp open  ccproxy-ftp \n3306/tcp open  mysql \n5432/tcp open  postgresql \n 5900/tcp open  vnc \n6000/tcp open  X11 \n6667/tcp open  irc \n8009/tcp open  ajp13 \n8180/tcp open  unknown \n Nmap done: 1 IP address (1 host up) scanned in 0.09 seconds";
		}
		for(Machine machine: this.machines) {
			if(machine.ip_address==ip) {
				return machine.nmap_ports();
			}
		}
		return null;
	}

	public String background() {
		// TODO Auto-generated method stub
		if(this.backgrounded==true) {
			return "Command not found";
		}
		for(Machine machine: this.machines) {
			machine.background();
		}
		this.backgrounded=true;
		return "";
	}

	public String ssh_login(String ip) {
		// TODO Auto-generated method stub
		if( this.backgrounded==false ) {
			return "Command not found";
		}
		for(Machine machine: this.machines) {
			if(machine.ip_address== ip) {
				String result= machine.ssh_login(this.session, this.ip_visible);
				if ( result != "Command not found") {
					this.last_opened_shell= machine.ip_address;
					this.backgrounded= false;
					this.session += 1;
				}
				return result;
			}
		}
		System.out.println("\nALERT\nALERT\n");
		return "";
	}

	public String whomai() {
		// TODO Auto-generated method stub
		if(this.root_hacked==true) {
			return "root";
		} 
		return "Not root";
	}

	public String ftp1(String current_victim_ip_address) {
		// TODO Auto-generated method stub
		return "Command not found";
	}

	public String mysql(String current_victim_ip_address) {
		// TODO Auto-generated method stub
		return "Command not found";
	}

	public String distcc(String current_victim_ip_address) {
		// TODO Auto-generated method stub
		return "Command not found";
	}

	public String dirtyCow() {
		// TODO Auto-generated method stub
		for(Machine machine: this.machines) {
			if(machine.ip_address==this.ip_vulnerable) {
				if(machine.shell_open==true) {
					this.root_hacked=true;
					return "DirtyCow root privilege escalation \n Backing up /usr/bin/passwd to /tmp/bak \n mmap b7d9f000 \n \n ptrace 0 \n \n  \n (___)                                    \n (o o)_____/                              \n @@ `                                 \n  ____, //usr/bin/passwd                           \n //						    //                               \n ^^    ^^                                \n DirtyCow root privilege escalation \n Backing up /usr/bin/passwd to /tmp/bak \n mmap b7d9f000 \n \n madvise 0";
				} else {
					return "Command not found";
				}
			}
		}
		return null;
	}

	public String pivot_autoroute() {
		// TODO Auto-generated method stub
		if(this.backgrounded==true && this.last_opened_shell!="meterpreter" && this.last_opened_shell!=null) {
			for(Machine machine: this.machines) {
				if(machine.ip_address==this.last_opened_shell) {
					String result=machine.pivot_autoroute(this.session);
					if(result!="Command not found") {
						this.last_opened_shell="meterpreter";
						this.session+=1;
						return result;
					}
				}
			}
			return "Command not found";
		}
		return "Command not found";
	}

	public String glibc_origin_expansion_priv_esc() {
		// TODO Auto-generated method stub
		return "Command not found";
	}

	public void reinitialization() {
		// TODO Auto-generated method stub
		for(Machine machine: this.machines) {
			machine.reinitialisation();
		}
		this.root_hacked=false;
		this.backgrounded=true;
		this.last_opened_shell=null;
	}

}
