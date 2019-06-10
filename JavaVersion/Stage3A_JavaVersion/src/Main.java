import java.util.ArrayList;
import java.util.List;

import joinery.DataFrame;

public class Main {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		List<String> columns= new ArrayList<>();
		columns.add("a");
		columns.add("b");
		
		DataFrame<Object> df = new DataFrame<>(columns);
		
		List<String> row= new ArrayList<>();
		row.add("10");
		row.add("20");
		
		df.append(row);
		df.append(row);
		
		System.out.println(df);
	}

}
