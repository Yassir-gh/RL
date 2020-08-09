package RL.Stage3A_VersionSansPredicats;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import RL.Stage3A_VersionSansPredicats.QLearningTable.Action;
import joinery.DataFrame;

//import joinery.DataFrame;

/**
 * Hello world!
 *
 */
public class App 
{
	
	static void update (QLearningTable RL) throws Exception {
		
		RL.nmap_host();
		
		int episode=0;
		int successive_victory=0;
		
		while(successive_victory != 1) {
			episode +=1 ;
			
			System.out.println("\n\n Partie " + Integer.toString(episode));
			System.out.println("----------------------------------------------------------------\\n");
			
			LinkedHashMap<String,LinkedHashMap> result_nmap_port= (LinkedHashMap<String, LinkedHashMap>) RL.nmap_ports();
			LinkedHashMap<String,LinkedHashMap> observation = new LinkedHashMap(); //Revoir s'il faut retourner une Map ou un String. J'ai choisi Map finalement car sur le code python j'avais eu besoin de reconvertir le String en Map à un moment
			LinkedHashMap<String,LinkedHashMap> observation_clone= new LinkedHashMap();
			for(String elt: result_nmap_port.keySet()) {
				observation_clone.put(elt, new LinkedHashMap(result_nmap_port.get(elt)));
			}
			for(String elt: result_nmap_port.keySet()) {
				observation.put(elt, new LinkedHashMap(observation_clone.get(elt)));
			}
			
			while(true) {
	            //RL choose action based on observation 
	            String action = RL.choose_action( observation_clone.toString() );
	            //RL take action and get next observation and reward
	            //observation_, reward, done = env.step(action)
	            Map<String,Object> observation2_reward_done = RL.step(action, observation_clone ); // Voir s'il faut retourner une Map ou un ArrayList. Ici on doit avoir en parametre une LinkedHashMap OBSERVATION

	            //RL learn from this transition
	            RL.learn(observation.toString() , action, observation2_reward_done.get("reward"), observation2_reward_done.get("s_").toString()); 

	            //swap observation
	            if( (boolean ) observation2_reward_done.get("done")==false) {
	            observation = new LinkedHashMap(); //Revoir s'il faut retourner une Map ou un String. J'ai choisi Map finalement car sur le code python j'avais eu besoin de reconvertir le String en Map à un moment
				for(String elt: ((LinkedHashMap<String, LinkedHashMap>) observation2_reward_done.get("s_")).keySet()) {
					observation.put(elt, new LinkedHashMap(((LinkedHashMap<String, LinkedHashMap>) observation2_reward_done.get("s_")).get(elt)));
				}
				for(String elt: observation.keySet()) {
					observation_clone.put(elt, new LinkedHashMap(observation.get(elt)));
				}
	            }
	            
	            if( (boolean) observation2_reward_done.get("done")==true) {
	            	
	            	if( ((float) observation2_reward_done.get("reward"))==1) { 
	            			successive_victory += 1; 
	            		} else {
	            			successive_victory = 0;
	            		}
	            	
	                RL.background(null);
	                RL.reinitialization();
	                break;
	            }
	            
	            System.out.println("\n\n------\n\n");
			}
			
		}
		
		System.out.println("Game over");
	}
	
	interface Action {
        String action();
    }
	public static Map initialise_all_actions() {
		// TODO Auto-generated method stub
		LinkedHashMap result= new LinkedHashMap();
		result.put("Action_7", new Action() { public String action() {return "Hellow" ;} } );
		result.put("Action_8", new Action() { public String action() {return "Hellow";} } );
		return result;
	}
	
    public static void main( String[] args ) throws Exception
    {
    	QLearningTable RL = new QLearningTable("192.168.56.101", "192.168.56.1", 0.1f, 0.9f, 0.95f, true);
    	update(RL);
    	
		/*
		 * List<String> columns= new ArrayList<>(); columns.add("a"); columns.add("b");
		 * 
		 * DataFrame<Object> df = new DataFrame<>(columns);
		 * 
		 * List<String> row= new ArrayList<>(); row.add("10"); row.add("20");
		 * 
		 * df.append(row); df.append(row);
		 * 
		 * Map<String,Object> test1 = new LinkedHashMap(); test1.put("nom","hinata");
		 * test1.put("prenom","shoyo");
		 * 
		 * Pattern session_regex = Pattern.compile("session ([0-9]+)"); Matcher matcher=
		 * session_regex.matcher("session 77");
		 * 
		 * System.out.println(df.row(0));
		 * 
		 * df.append("test", row); System.out.println(df.index());
		 * System.out.println(df.columns());
		 * System.out.println(test1.keySet().getClass().getName());
		 * System.out.println(test1.keySet().toArray().getClass().getName());
		 * System.out.println(test1.get("nom").getClass().equals(String.class));
		 * 
		 * Random r = new Random(); System.out.println(r.nextDouble());
		 * 
		 * System.out.println( ((Action)
		 * initialise_all_actions().get("Action_7")).action() );
		 * 
		 * Matcher matcher2= Pattern.compile("^([0-9]+)").
		 * matcher("22/tcp   open  ssh \n23/tcp   open  telnet \n25/tcp   open  smtp \n53/tcp   open  domain \n80/tcp   open  http \n111/tcp  open  rpcbind \n139/tcp  open  netbios-ssn \n445/tcp  open  microsoft-ds \n512/tcp  open  exec \n513/tcp  open  login \n514/tcp  open  shell \n1099/tcp open  rmiregistry \n1524/tcp open  ingreslock \n2049/tcp open  nfs \n2121/tcp open  ccproxy-ftp \n3306/tcp open  mysql \n5432/tcp open  postgresql \n 5900/tcp open  vnc \n6000/tcp open  X11 \n6667/tcp open  irc \n8009/tcp open  ajp13 \n8180/tcp open  unknown \n Nmap done: 1 IP address (1 host up) scanned in 0.09 seconds"
		 * ); matcher2.find(); System.out.println(matcher2.group());
		 * 
		 * 
		 * System.out.println("a.B.c".split("\\.")[0]);
		 */
        
    	 LinkedHashMap a= new LinkedHashMap();
    	 a.put("nom", "hinata");
    	 a.put("prenom", "test");
    	 a.put("k", "ko");
    	 a.put("r", "ro");
    	 System.out.println(a.keySet());
    }
}
