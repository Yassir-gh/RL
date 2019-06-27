package RL.Stage3A_VersionSansPredicats;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import joinery.DataFrame;

public class QLearningTable {
	
	private ArrayList actions = new ArrayList();
	private Map all_actions= new HashMap(); // sur python j'avais une sorte de Map<string,function>, en Java ça donne ?
	private float lr = 0;
	private float gamma = 0;
	private float epsilon = 0;
	private DataFrame q_table = new DataFrame(actions);
	private String initial_victim_ip_address = "";
	private String current_victim_ip_addres = "";
	private String local_ip_address = "";
	private boolean simulation = false;
	private SimulationEnvironment simulation_environment = new SimulationEnvironment();
	
	private Map<String,Object> nmap_dict = new HashMap();
	private boolean success = false;
	private String whoami = "Not root";
	private boolean action_in_the_right_shell= true;
	private String session = "0";
	private Pattern session_regex = Pattern.compile("Hugo");
	private Integer action_iteration = 0;
	private List neighbors = new ArrayList();
	private Integer nmap_ports_launched= 0;
	private Integer nmap_hosts_launched= 0;
	private Integer victim_number= 0;
	private boolean host_seems_down_nmap_ports= false;
	private boolean no_active_jobs= false;
	
	public QLearningTable(String victim_ip_address, String local_ip_address, float learning_rate, float reward_decay, float e_greedy) {
		
	}
	
	public void nmap_host() {
		
	}
	
	public Map<String, Object> nmap_ports() {
		
		return null;
	}

	public String choose_action(Map<String, Object> observation) {
		// TODO Auto-generated method stub
		return null;
	}

	public Map<String,Object> step(String action, Map<String, Object> observation) {
		// TODO Auto-generated method stub
		return null;
	}

	public void learn(Map<String, Object> observation, String action, Object reward, Object observation2) {
		// TODO Auto-generated method stub
		
	}

	public void background() {
		// TODO Auto-generated method stub
		
	}

	public void reinitialization() {
		// TODO Auto-generated method stub
		
	}

}
