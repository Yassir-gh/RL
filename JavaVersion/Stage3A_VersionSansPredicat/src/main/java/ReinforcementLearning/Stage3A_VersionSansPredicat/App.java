package ReinforcementLearning.Stage3A_VersionSansPredicat;

import java.util.ArrayList;
import java.util.List;

import joinery.DataFrame;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args )
    {
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
