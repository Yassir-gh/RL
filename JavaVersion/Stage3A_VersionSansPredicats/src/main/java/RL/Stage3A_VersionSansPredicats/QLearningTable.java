package RL.Stage3A_VersionSansPredicats;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import joinery.DataFrame;

//import joinery.DataFrame;

public class QLearningTable {
	
	private ArrayList<Object> actions = null; //liste d'actions
	private Map all_actions= new HashMap(); // sur python j'avais une sorte de Map<string,function>, en Java ça donne ?
	private float lr = 0;
	private float gamma = 0;
	private float epsilon = 0;
	private DataFrame<Float> q_table ;
	private String initial_victim_ip_address = "";
	private String current_victim_ip_address = "";
	private String local_ip_address = "";
	private boolean simulation = true;
	private SimulationEnvironment simulation_environment = null;
	
	private Map<String,HashMap> nmap_dict = new HashMap();
	private boolean success = false;
	private String whoami = "Not root";
	private boolean action_in_the_right_shell= true;
	private String session = "0";
	private Pattern session_regex = Pattern.compile("session ([0-9]+)");
	private Integer action_iteration = 0;
	private ArrayList<String> neighbors = new ArrayList<String>();
	private Integer nmap_ports_launched= 0;
	private Integer nmap_hosts_launched= 0;
	private Integer victim_number= 0;
	private boolean host_seems_down_nmap_ports= false;
	private boolean no_active_jobs= false;
	private Random random= new Random();
	
	public QLearningTable(String victim_ip_address, String local_ip_address, float learning_rate, float reward_decay, float e_greedy, boolean simulation) {
		this.actions = new ArrayList<Object>(Arrays.asList(this.initialise_all_actions().keySet().toArray()));   // A CORRIGER QUAND J'AI LA FONCTION INITIALISE_ALL_ACTIONS
		this.all_actions = this.initialise_all_actions(); // A CORRIGER QUAND J'AI LA FONCTION INITIALISE_ALL_ACTIONS
		this.q_table= new DataFrame<>(this.actions); //PROBLEME A RESOUDRE Object[] vs ArrayList
		System.out.println("Hellow");
		this.initial_victim_ip_address= victim_ip_address;
		this.current_victim_ip_address= victim_ip_address;
		this.lr= learning_rate;
		this.gamma= reward_decay;
		this.epsilon= e_greedy;
		this.simulation= simulation;
		if(simulation==true) {
			ArrayList<String> liste_ip_simulee = new ArrayList<String>( Arrays.asList("192.168.56.101","192.168.56.102","192.168.56.103","192.168.56.104","192.168.56.105","192.168.56.106","192.168.56.107","192.168.56.108") );
			this.simulation_environment= new SimulationEnvironment(liste_ip_simulee, liste_ip_simulee.get( liste_ip_simulee.size()-1 ), liste_ip_simulee.get(0) );
		}
	}
	
	public Map<String,HashMap> nmap_ports() {
		System.out.println("nmap ports en cours ... \n");
		this.action_iteration= 0;
		
		if ( this.nmap_dict.keySet().contains("victim_"+this.victim_number.toString()) == false){
			this.nmap_dict.put("victim_"+this.victim_number.toString(), new HashMap<String,String>());
		};
		
		String result= this.simulation_environment.nmap_ports(this.current_victim_ip_address);
		this.read_simulated_console(result);
		
		this.nmap_dict.get("victim_"+this.victim_number.toString()).put("victim_ip_address", this.current_victim_ip_address); 
		
		HashMap<String,HashMap> a= new HashMap( (HashMap<String,HashMap>) (((HashMap<String,HashMap>) this.nmap_dict).clone()) );
		return a;
	}
	
	public void nmap_host() { //ici je fais que la version simulée de cette fonction
		
		System.out.println("nmap hosts en cours ... \n");
		
		String result= this.simulation_environment.nmap_hosts();
		this.read_simulated_console(result);
		
		for(String elt : this.neighbors) {
			
			if( this.q_table.columns().contains(elt) == false) {
				ArrayList<Float> columnToAdd= new ArrayList(Collections.nCopies(q_table.index().size(), (float) 0));
				this.q_table.add(elt, columnToAdd);
			}
			
		}
		System.out.println("\n");
		
		this.all_actions= this.initialise_all_actions();
		
		for(String elt: this.neighbors) {
			this.all_actions.put(elt, elt);
		}
		this.actions = new ArrayList<Object>(Arrays.asList(this.all_actions.keySet().toArray()));
	    System.out.println("ACTIONS \n");
	    System.out.println(this.actions);
	    System.out.println('\n');
		
	}
	
	
	
	interface Action {
        void action(HashMap<String, Object> result);
    }
	private Map initialise_all_actions() {
		// TODO Auto-generated method stub
		HashMap result= new HashMap();
		result.put("Action_1", new Action() { public void action(HashMap<String, Object> result) {background(result);} } );
		result.put("Action_2", new Action() { public void action(HashMap<String, Object> result) {ssh_login(result);} } );
		result.put("Action_3", new Action() { public void action(HashMap<String, Object> result) {ftp1(result);} } );
		result.put("Action_4", new Action() { public void action(HashMap<String, Object> result) {mysql(result);} } );
		result.put("Action_5", new Action() { public void action(HashMap<String, Object> result) {dirtyCow(result);} } );
		result.put("Action_6", new Action() { public void action(HashMap<String, Object> result) {distcc(result);} } );
		result.put("Action_7", new Action() { public void action(HashMap<String, Object> result) {pivot_autoroute_4(result);} } );
		result.put("Action_8", new Action() { public void action(HashMap<String, Object> result) {glibc_origin_expansion_priv_esc(result);} } );
		return result;
	}
	

	private void read_simulated_console(String console_data) {
		// TODO Auto-generated method stub
		System.out.println("\n Reading simulated console \n");
		
		if(console_data.contains("PORT") && console_data.contains("STATE")) {
			this.traitement_nmap_ports(console_data);
		}
		
		if(console_data.contains("nmap -sP")) {
			this.nmap_hosts_launched= 1;
		}
		
		if( (console_data.contains("Nmap scan report") && this.nmap_hosts_launched==1) || console_data.contains("appears to be up") ) {
			this.traitement_nmap_hosts(console_data);
            this.nmap_hosts_launched= 0;
		}
		
		if( console_data.contains("Success") || console_data.contains("opened") || console_data.contains("Route added") || console_data.contains("Added route") ) {
			this.success= true;
		} else if (console_data.contains("Invalid") || console_data.contains("no session") || console_data.contains("failed") ) {
			this.success= false;
		} else {
			System.out.println("\nSUCCESS UNKNOWN\n");
		}
		
		if( console_data.contains("root") ) {
			this.whoami= "root";
		} else {
			this.whoami= "Not root";
		}
		
		Matcher matcher= this.session_regex.matcher(console_data);
		if( matcher.find() ) {
			String session_number = matcher.group().split(" ")[1];
			if( Integer.parseInt(session_number) > Integer.parseInt(this.session) ) {
				this.session= session_number;
				System.out.println("\nSESSION: "+ this.session + "\n");
			}
		}
		
		if( console_data.contains("Unknown") || console_data.contains("not found") || console_data.contains("No such file or directory") || console_data.contains("Usage") || console_data.contains("failed") ) {
			this.action_in_the_right_shell= false;
		} else {
			this.action_in_the_right_shell= true;
		}
		
		if( console_data.contains("Host seems down") ) {
			this.host_seems_down_nmap_ports= true;
		} else {
			this.host_seems_down_nmap_ports= false;
		}
		
		if( console_data.contains("No active jobs") ) {
			this.no_active_jobs= true;
		} else {
			this.no_active_jobs= false;
		}
		
		System.out.println(console_data);
		
	}


	private void traitement_nmap_ports(String console_data) {
		// TODO Auto-generated method stub
		System.out.println("\ntraitement_nmap_ports\n");
		Pattern a = Pattern.compile("^([0-9]+)");
		Pattern b = Pattern.compile("open|closed");
		for(String elt: console_data.split("\n")) {
			Matcher a1= a.matcher(elt);
			Matcher b1= b.matcher(elt);
			if( a1.find() && b1.find()) {
				this.nmap_dict.get("victim_"+ this.victim_number.toString()).put(a1.group()+"_ip"+this.victim_number.toString(), b1.group());
				System.out.println("TEST- NMAP_DICT= "+this.nmap_dict.toString());
			}
		}
		
	}
	
	private void traitement_nmap_hosts(String console_data) {
		// TODO Auto-generated method stub
		Pattern a = Pattern.compile("Host is up");
		Pattern b = Pattern.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}");
		Pattern d = Pattern.compile("Host \\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3} appears to be up.");
		for(int i=0; i<console_data.split("\n").length; i++) {
			Matcher a1= a.matcher(console_data.split("\n")[i]);
			Matcher b1= b.matcher(console_data.split("\n")[i]);
			Matcher d1= d.matcher(console_data.split("\n")[i]);
			if(a1.find()) {
				Matcher b2= b.matcher(console_data.split("\n")[i-1]);
				String c="";
				if(b2.find()) {
					c= b2.group();
				}
				if( c != this.local_ip_address && this.neighbors.contains(c)==false) {
					this.neighbors.add(c);
				}
			}
			if(d1.find()) {
				String c="";
				if(b1.find()) {
					c= b1.group();
				}
				if( c!=this.local_ip_address && this.neighbors.contains(c)==false && c!="192.168.56.100") {
					this.neighbors.add(c);
				}
			}
		}
		System.out.println("Neighbors: "+ this.neighbors.toString());
		
	}

	public String choose_action(String observation) {
		// TODO Auto-generated method stub
		System.out.println("\nOBSERVATION: " + observation);
		this.check_state_exist(observation);
		String action="";
		if( this.random.nextDouble() < this.epsilon) {
			List<Float> state_action= this.q_table.row(observation);
			System.out.println(state_action);
			System.out.println("Yoow");
			System.out.println(Collections.max(state_action));
			Float max= Collections.max(state_action);
			Integer max_index=0;
			for(int i=0; i<state_action.size(); i++) {
				if(state_action.get(i)==max) {
					max_index=i;
					break;
				}
			}
			System.out.println("\nq_table.comulns()= "+this.q_table.columns().toString());
			action= (String) this.q_table.columns().toArray()[max_index];
		} else {
			Integer random_index= this.random.nextInt(this.q_table.columns().size());
			action= (String) this.q_table.columns().toArray()[random_index];
		}
		System.out.println("\nACTION: "+action);
		return action;
	}

	private void check_state_exist(String state) {
		// TODO Auto-generated method stub
		if( this.q_table.index().contains(state)==false) {
			ArrayList<Float> rowToAdd= new ArrayList(Collections.nCopies(q_table.columns().size(), (float) 0));
			this.q_table.append(state, rowToAdd);
		}
		
	}

	public Map<String, Object> step(String action, Map<String, HashMap> obs) {
		// TODO Auto-generated method stub
		HashMap<String, Object> result= new HashMap<String, Object>();
		
		this.action_iteration += 1;
		Map<String, HashMap> past_observation_dict= new HashMap((HashMap<String, HashMap>)((HashMap<String, HashMap>)obs).clone());
		Map<String, HashMap> observation_dict= new HashMap((HashMap<String, HashMap>)((HashMap<String, HashMap>)obs).clone());

		observation_dict.get("victim_"+this.victim_number.toString()).put("action "+this.action_iteration.toString(), action);
		System.out.println("blup: "+this.nmap_dict.toString());
		
		if( this.all_actions.get(action).getClass().equals(String.class)) {
			this.change_ip(action, observation_dict, past_observation_dict, result);
		} else {
			((Action) this.all_actions.get(action)).action(result);
		}
		
		this.success= false;
		System.out.println("STEP-RESULT: "+ result.toString());
		
		if(result.get("whoami2")=="root") {
			result.put("reward", (float) 1.0);
			result.put("done", true);
			result.put("s_", "terminal");
			System.out.println("\nsuccess= "+result.get("success2").toString());
			System.out.println("whoami= "+result.get("whoami2"));
			System.out.println("reward= "+result.get("reward").toString());
		} else if ( result.get("whoami2")!="root" && ((boolean) result.get("success2"))==true) {
			result.put("reward", (float) 0.0);
			result.put("done", false);
			result.put("s_", observation_dict);
			System.out.println("\nsuccess= "+result.get("success2").toString());
			System.out.println("whoami= "+result.get("whoami2"));
			System.out.println("reward= "+result.get("reward").toString());
		} else {  //cas success2==false
			result.put("reward", (float) -1.0);
			result.put("done", true);
			result.put("s_", "terminal");
			System.out.println("\nsuccess= "+result.get("success2").toString());
			System.out.println("whoami= "+result.get("whoami2"));
			System.out.println("reward= "+result.get("reward").toString());
		}
		
		return result;
	}

	private void change_ip(String action, Map<String, HashMap> observation_dict,
			Map<String, HashMap> past_observation_dict, HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		System.out.println("\nPAST IPs \n");
		for(String victim: past_observation_dict.keySet()) {
			System.out.println(past_observation_dict.get(victim).get("victim_ip_address"));
		}
		if( action != this.current_victim_ip_address ) {
			ArrayList<String> victim_ip_address_list= new ArrayList<String>();
			for(String victim: past_observation_dict.keySet()) {
				victim_ip_address_list.add((String) past_observation_dict.get(victim).get("victim_ip_address"));
			}
			if(victim_ip_address_list.contains(action)==false) {
				System.out.println("TEST");
				this.current_victim_ip_address= action;
				this.victim_number += 1;
				Map<String,HashMap> a = this.nmap_ports();
				if( this.host_seems_down_nmap_ports==true ) {
					this.victim_number -= 1;
					result.put("success2", false);
					result.put("whoami2", "Not root");
					return ;
				}
				for(String elt: a.keySet()) {
					if(observation_dict.keySet().contains(elt)==false) {
						observation_dict.put(elt, a.get(elt));
					}
				}
				System.out.println(observation_dict.toString());
				System.out.println("REVOIR CETTE FONCTION, JE DOIS PEUT ETRE PAS CLONER observation_dict FINALEMENT");
				result.put("success2", true);
				result.put("whoami2", "Not root");
				return ;
			} else {
				result.put("success2", false);
				result.put("whoami2", "Not root");
				return ;
			}
		} else {
			result.put("success2", false);
			result.put("whoami2", "Not root");
			return ;
		}
	}

	public void learn(String obs, String action, Object reward, String observation2) {
		// TODO Auto-generated method stub
		this.check_state_exist(observation2);
		System.out.println(observation2);
		System.out.println("Yoow2");
		System.out.println(this.q_table.index());
		float q_predict= (float) this.q_table.get(obs, action);
		float q_target=0;
		if(observation2 != "terminal") {
			q_target= ((float) reward)+ (this.gamma)*((float)Collections.max(this.q_table.row(observation2)) );
		} else {
			q_target= (float) reward;
		}
		this.q_table.set(obs, action, ( (float)this.q_table.get(obs, action) + (this.lr*(q_target-q_predict) ) ) );
	}
	
	public void reinitialization() {
		// TODO Auto-generated method stub
		this.simulation_environment.reinitialization();
		this.current_victim_ip_address= this.initial_victim_ip_address;
		this.nmap_dict = new HashMap();
		this.action_iteration= 0;
		this.victim_number= 0;
	}

	public void background(HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		String simulation_result= this.simulation_environment.background();
		this.read_simulated_console(simulation_result);
		boolean c = this.action_in_the_right_shell;
		if(result!=null) {
			if(c==true) {
				result.put("success2", true);
				result.put("whoami2", "Not root");
				return ;
			} else {
				result.put("success2", false);
				result.put("whoami2", "Not root");
				return ;
			}
		}
		return ;
	}
	
	public void ssh_login(HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		String RPORT="22"+"_ip"+this.victim_number.toString();
		if( this.nmap_dict.get("victim_"+this.victim_number.toString()).get(RPORT)=="open" ) {
			String simulation_result= this.simulation_environment.ssh_login(this.current_victim_ip_address);
			this.read_simulated_console(simulation_result);
			
			boolean c = this.action_in_the_right_shell;
			
			if(c==true) {
				boolean a = this.success;
				if(a==true) {
					this.nmap_host();
				}
				String b = this.simulation_environment.whomai();
				
				result.put("success2", a);
				result.put("whoami2", b);
				return ;
			} else {
				result.put("success2", false);
				result.put("whoami2", "Not root");
				return ;
			}
		}
		result.put("success2", false);
		result.put("whoami2", "Not root");
		return ;
	}
	
	public void ftp1(HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		String RPORT="21"+"_ip"+this.victim_number.toString();
		if( this.nmap_dict.get("victim_"+this.victim_number.toString()).get(RPORT)=="open" ) {
			String simulation_result= this.simulation_environment.ftp1(this.current_victim_ip_address);
			this.read_simulated_console(simulation_result);
			
			boolean c = this.action_in_the_right_shell;
			
			if(c==true) {
				boolean a = this.success;
				if(a==true) {
					this.nmap_host();
				}
				String b= this.simulation_environment.whomai();
				result.put("success2", a);
				result.put("whoami2", b);
				return ;
			} else {
				result.put("success2", false);
				result.put("whoami2", "Not root");
				return ;
			}
		}
		result.put("success2", false);
		result.put("whoami2", "Not root");
		return ;
	}
	
	public void mysql(HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		String RPORT="3306"+"_ip"+this.victim_number.toString();
		if( this.nmap_dict.get("victim_"+this.victim_number.toString()).get(RPORT)=="open" ) {
			String simulation_result= this.simulation_environment.mysql(this.current_victim_ip_address);
			this.read_simulated_console(simulation_result);
			boolean c = this.action_in_the_right_shell;
			
			if(c==true) {
				boolean a = this.success;
				if(a==true) {
					this.nmap_host();
				}
				String b= this.simulation_environment.whomai();
				result.put("success2", a);
				result.put("whoami2", b);
				return ;
			} else {
				result.put("success2", false);
				result.put("whoami2", "Not root");
				return ;
			}
		}
		result.put("success2", false);
		result.put("whoami2", "Not root");
		return ;
	}
	
	public void distcc(HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		String RPORT="3632"+"_ip"+this.victim_number.toString();
		if( this.nmap_dict.get("victim_"+this.victim_number.toString()).get(RPORT)=="open" ) {
			String simulation_result= this.simulation_environment.distcc(this.current_victim_ip_address);
			this.read_simulated_console(simulation_result);
			boolean c = this.action_in_the_right_shell;
			
			if(c==true) {
				boolean a = this.success;
				if(a==true) {
					this.nmap_host();
				}
				String b= this.simulation_environment.whomai();
				result.put("success2", a);
				result.put("whoami2", b);
				return ;
			} else {
				result.put("success2", false);
				result.put("whoami2", "Not root");
				return ;
			}
		}
		result.put("success2", false);
		result.put("whoami2", "Not root");
		return ;
	}
	
	public void dirtyCow(HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		String simulation_result=this.simulation_environment.dirtyCow();
	    this.read_simulated_console(simulation_result);
	            
	    boolean c= this.action_in_the_right_shell;
	    if(c==true) {
	    	String b = this.simulation_environment.whomai();
	    	if(b=="root") {
	    		result.put("success2", true);
	    		result.put("whoami2", "root");
	    		return ;
	    	} else {
	    		result.put("success2", false);
	    		result.put("whoami2", "Not root");
	    		return ;
	    	}
	    }
	    result.put("success2", false);
		result.put("whoami2", "Not root");
		return ;
	}
	
	public void pivot_autoroute_4(HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		String simulation_result=this.simulation_environment.pivot_autoroute();
		this.read_simulated_console(simulation_result);
		boolean c= this.action_in_the_right_shell;
	    if(c==true) {
	    	boolean a = this.success;
	    	result.put("success2", a);
    		result.put("whoami2", "Not root");
    		return ;
	    } else {
	    	result.put("success2", false);
    		result.put("whoami2", "Not root");
    		return ;
	    }
	}
	
	public void glibc_origin_expansion_priv_esc(HashMap<String, Object> result) {
		// TODO Auto-generated method stub
		if(Integer.parseInt(this.session)>0) {
			String simulation_result= this.simulation_environment.glibc_origin_expansion_priv_esc();
			this.read_simulated_console(simulation_result);
			boolean a = this.success;
			String b= this.simulation_environment.whomai();
			result.put("success2", a);
    		result.put("whoami2", b);
    		return ;
		} else {
			result.put("success2", false);
    		result.put("whoami2", "Not root");
    		return ;
		}
	}
	

}
