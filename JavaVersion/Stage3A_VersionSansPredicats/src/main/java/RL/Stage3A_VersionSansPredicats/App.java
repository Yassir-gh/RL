package RL.Stage3A_VersionSansPredicats;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import joinery.DataFrame;

/**
 * Hello world!
 *
 */
public class App 
{
	
	static void update (QLearningTable RL) {
		
		RL.nmap_host();
		
		for( int i=0; i<=100; i++) {
			System.out.println("\n\n Partie " + Integer.toString(i));
			System.out.println("----------------------------------------------------------------\\n");
			
			Map<String, Object> observation = RL.nmap_ports(); //Revoir s'il faut retourner une Map ou un String
			
			while(true) {
				RL.update_actions(observation);
	            
	            RL.update_q_tables(observation);
	            
	            //RL choose action based on observation
	            String action = RL.choose_action(observation);

	            //RL take action and get next observation and reward
	            //observation_, reward, done = env.step(action)
	            Map<String,Object> observation2_reward_done = RL.step(action, observation); // Voir s'il faut retourner une Map ou un ArrayList
	            
	            RL.update_actions( (Map<String,Object>) observation2_reward_done.get("observation2"));
	            RL.update_q_tables( (Map<String,Object>) observation2_reward_done.get("observation2"));

	            //RL learn from this transition
	            RL.learn(observation, action, observation2_reward_done.get("reward"), observation2_reward_done.get("observation2"));

	            //swap observation
	            observation = (Map<String,Object>) observation2_reward_done.get("observation2");
	            
	            if( (boolean) observation2_reward_done.get("observation2")==true) {
	                RL.background();
	                RL.reinitialization();
	                break;
	            }
	            
	            System.out.println("\n\n------");
			}
			
		}
		
		System.out.println("Game over");
	}
	
    public static void main( String[] args )
    {
    	QLearningTable RL = new QLearningTable("192.168.56.101", "192.168.56.1", 0.1f, 0.9f, 0.95f );
    	update(RL);
    	
    	List<String> columns= new ArrayList<>();
		columns.add("a");
		columns.add("b");
		
		DataFrame<Object> df = new DataFrame<>(columns);
		
		List<String> row= new ArrayList<>();
		row.add("10");
		row.add("20");
		
		df.append(row);
		df.append(row);
		
		System.out.println(df.columns());
    }
}
