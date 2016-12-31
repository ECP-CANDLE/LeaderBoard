# Leaderboard client side script

#see requirements.txt for the required python packages
pip install -r requirements.txt

# help
python leaderboard.py --help
usage: leaderboard.py [-h] [--version]
                      [--outputJsonFileName OUTPUTJSONFILENAME]
                      [--importJsonFileName JSONFILENAME]
                      [--benchmarkName BENCHMARKNAME]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --outputJsonFileName OUTPUTJSONFILENAME
                        Json file name to write the results from query

required arguments:
  --importJsonFileName JSONFILENAME
                        Json file that need to be imported
  --benchmarkName BENCHMARKNAME
                        benchmark name to query

#Usage
#=====

#import the data in the json file to the db
python leaderboard.py --importJsonFileName example.json

#query the results from db for benchmark P1B1
python leaderboard.py --benchmarkName P1B1
