# Leaderboard client side script


# command line options
python leaderboard.py --help

usage: leaderboard.py [-h] [-v] [-o OUTPUTJSONFILENAME] [-i JSONFILENAME]  
                      [-q BENCHMARKNAME]

optional arguments:  
  -h, --help            show this help message and exit  
  -v, --version         show program's version number and exit  
  -o OUTPUTJSONFILENAME, --outputJsonFileName OUTPUTJSONFILENAME  
                        Json file name to write the results from query  

required arguments:  
  -i JSONFILENAME, --importJsonFileName JSONFILENAME  
                        Json file that need to be imported  
  -q BENCHMARKNAME, --queryBenchmarkname BENCHMARKNAME  
                        benchmark name to query  

# usage

##import the data in the json file to the db
python leaderboard.py -i example1.json  
python leaderboard.py -i example2.json

##query the results from db for benchmark P1B1
python leaderboard.py -q P1B2  
python leaderboard.py -q P1B1 -o output.json
