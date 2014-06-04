/*
 * Copyright 2012-14 Justin A. Debrabant <debrabant@cs.brown.edu> and Matteo Riondato <matteo@cs.brown.edu>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Random;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

import fim.fpgrowth.*; 

public class FIMReducer extends MapReduceBase implements Reducer<IntWritable, Text, Text, DoubleWritable>
{
	private int minFreqPercent;
	private int sampleSize;
	private int id;
	private float epsilon;
	private boolean set;

	@Override
	public void configure(JobConf conf) 
	{
		minFreqPercent = conf.getInt("PARMM.minFreqPercent", 20); 
		sampleSize = conf.getInt("PARMM.sampleSize", 1000);
		epsilon = conf.getFloat("PARMM.epsilon", 0.05f);
		id = conf.getInt("mapred.task.partition", -1);
		set = false;
	}

	@Override
	public void reduce(IntWritable key, Iterator<Text> values, 
			OutputCollector<Text,DoubleWritable> output, 
			Reporter reporter) throws IOException
	{			
		long startTime = System.currentTimeMillis();
		if (! set)
		{
			reporter.incrCounter("FIMReducerStart", String.valueOf(id), startTime);
			reporter.incrCounter("FIMReducerEnd", String.valueOf(id), startTime);
			set = true;
		}

		// This is a very crappy way of checking whether we got the
		// right number of transactions. It may not be too inefficient
		// though.
		ArrayList<Text> transactions = new ArrayList<Text>(sampleSize);
		while (values.hasNext())
		{
			Text trans = new Text(values.next().toString());
			transactions.add(trans);
		}
		if (sampleSize != transactions.size())
		{
			System.out.println("WRONG NUMBER OF TRANSACTIONS!");
		}
		System.out.println("samplesize: " + sampleSize + " received: " + transactions.size());
	  	FPgrowth.mineFrequentItemsets(transactions.iterator(), transactions.size(), minFreqPercent - (epsilon * 50) , output);
		
		long endTime = System.currentTimeMillis();
		reporter.incrCounter("FIMReducerEnd", String.valueOf(id), endTime-startTime);
	}
}



