package RL.Stage3A_VersionSansPredicats;

import java.util.ArrayList;

public class Machine {

	public String ip_address= "";
	public ArrayList<String> neighbors_ip_addresses;
	public ArrayList<Machine> neighbors_machines;
	public boolean shell_obtained= false;
	public boolean meterpreter_obtained_and_route_added= false;
	public boolean shell_open= false;

	public Machine(String ip_address, ArrayList<String> neighbors_ip_addresses) {
		// TODO Auto-generated constructor stub
		this.ip_address= ip_address;
		this.neighbors_ip_addresses= neighbors_ip_addresses;
	}

	public String nmap_hosts(String ip_visible) {
		// TODO Auto-generated method stub
		return "[*] exec: nmap -sP 192.168.56.0/24 \n Starting Nmap 4.53 ( http://insecure.org ) at 2019-05-31 00:31 EDT \n Host 192.168.56.1 appears to be up. \n MAC Address: 0A:00:27:00:00:00 (Unknown) \n Host " + ip_visible + " appears to be up. \n MAC Address: 08:00:27:82:94:FA (Cadmus Computer Systems) \n Host " + this.neighbors_ip_addresses.get(0) + " appears to be up." + ( (this.neighbors_ip_addresses.size()==2) ? ("\nHost " + this.neighbors_ip_addresses.get(1) + " appears to be up.") : " " ) + " \n MAC Address: 08:00:27:7D:34:9D (Cadmus Computer Systems) \n Nmap done: 256 IP addresses (4 hosts up) scanned in 42.505 seconds";
	}

	public String nmap_ports() {
		// TODO Auto-generated method stub
		for(Machine machine: this.neighbors_machines) {
			if( this.neighbors_ip_addresses.contains(machine.ip_address) && machine.shell_open==true) {
				return "Starting Nmap 7.70 ( https://nmap.org ) at 2019-06-25 11:46 CEST \n Nmap scan report for 192.168.56.101 \n Host is up (0.0043s latency). \n Not shown: 977 closed ports \n PORT     STATE SERVICE \n21/tcp   open  ftp \n22/tcp   open  ssh \n23/tcp   open  telnet \n25/tcp   open  smtp \n53/tcp   open  domain \n80/tcp   open  http \n111/tcp  open  rpcbind \n139/tcp  open  netbios-ssn \n445/tcp  open  microsoft-ds \n512/tcp  open  exec \n513/tcp  open  login \n514/tcp  open  shell \n1099/tcp open  rmiregistry \n1524/tcp open  ingreslock \n2049/tcp open  nfs \n2121/tcp open  ccproxy-ftp \n3306/tcp open  mysql \n5432/tcp open  postgresql \n5900/tcp open  vnc \n6000/tcp open  X11 \n6667/tcp open  irc \n8009/tcp open  ajp13 \n8180/tcp open  unknown \n Nmap done: 1 IP address (1 host up) scanned in 0.09 seconds";
			}
		}
		return "Starting Nmap 7.70 ( https://nmap.org ) at 2019-06-24 14:45 CEST \n Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn \n Nmap done: 1 IP address (0 hosts up) scanned in 3.04 seconds";
	}

	public void background() {
		// TODO Auto-generated method stub
		this.shell_open=false;
		return ;
	}

	public String ssh_login(int session, String ip_visible) {
		// TODO Auto-generated method stub
		if( this.ip_address==ip_visible) {
			this.shell_obtained=true;
			this.shell_open=true;
			return "RHOSTS => 192.168.56.101 \n USERPASS_FILE => /usr/share/metasploit-framework/data/wordlists/root_userpass.txt \n STOP_ON_SUCCESS => true \n [+] 192.168.56.101:22 - Success: 'msfadmin:msfadmin' 'uid=1000(msfadmin) gid=1000(msfadmin) groups=4(adm),20(dialout),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),107(fuse),111(lpadmin),112(admin),119(sambashare),1000(msfadmin) Linux metasploitable 2.6.24-16-server #1 SMP Thu Apr 10 13:58:00 UTC 2008 i686 GNU/Linux ' \n [*] Command shell session "+(session + 1)+ " opened (192.168.56.1:43183 -> 192.168.56.101:22) at 2019-06-24 15:54:31 +0200 \n [*] Scanned 1 of 1 hosts (100% complete) \n [*] Auxiliary module execution completed";
		}
		for(Machine machine: this.neighbors_machines) {
			if( this.neighbors_ip_addresses.contains(machine.ip_address) && machine.meterpreter_obtained_and_route_added==true) {
				this.shell_obtained=true;
				this.shell_open=true;
				return "RHOSTS => 192.168.56.101 \n USERPASS_FILE => /usr/share/metasploit-framework/data/wordlists/root_userpass.txt \n STOP_ON_SUCCESS => true \n [+] 192.168.56.101:22 - Success: 'msfadmin:msfadmin' 'uid=1000(msfadmin) gid=1000(msfadmin) groups=4(adm),20(dialout),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),107(fuse),111(lpadmin),112(admin),119(sambashare),1000(msfadmin) Linux metasploitable 2.6.24-16-server #1 SMP Thu Apr 10 13:58:00 UTC 2008 i686 GNU/Linux ' \n [*] Command shell session "+(session + 1)+ " opened (192.168.56.1:43183 -> 192.168.56.101:22) at 2019-06-24 15:54:31 +0200 \n [*] Scanned 1 of 1 hosts (100% complete) \n [*] Auxiliary module execution completed";
			}
		}
		return "Command not found";
	}

	public String pivot_autoroute(int session) {
		// TODO Auto-generated method stub
		this.meterpreter_obtained_and_route_added=true;
		
		return "[*] Meterpreter session "+(session + 1)+" opened (192.168.56.1:46550 -> 192.168.56.101:50174) at 2019-06-25 11:02:30 +0200 \n [*] Command stager progress: 100.00% (773/773 bytes) \n [*] Post module execution completed \n [*] Running module against metasploitable.localdomain \n [*] Searching for subnets to autoroute. \n [+] Route added to subnet 192.168.56.0/255.255.255.0 from host's routing table. \n [*] Post module execution completed";
	}

	public void reinitialisation() {
		// TODO Auto-generated method stub
		this.shell_obtained=false;
		this.meterpreter_obtained_and_route_added=false;
		this.shell_open=false;
	}

}
