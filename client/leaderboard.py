# -*- coding: utf-8 -*-
import sys
import argparse
import json
import requests
import uuid
import logging

"""Modules for importing and querying benchmark data to CANDLE leaderboard
database.

The CANDLE users can use this module to import the data the central CANDLE
leaderboard database and query the results.
"""

__author__ = "Prasanna Balaprakash"
__maintainer__ = "Prasanna Balaprakash"
__email__ = "pbalapra@anl.gov"
__status__ = "Developement"


URL = 'http://pubseed.theseed.org/leaderboard'
URL_LOCAL = 'http://0.0.0.0:7137/leaderboard'

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

'''Allow insertion only for the following valid benchmarks'''
VALID_BENCHMARKS = ['P1B1', 'P1B2', 'P1B3', 'P2B1', 'P2B2', 'P2B3', 'P3B1',
                    'P3B2', 'P3B3']
"""JSON record should have the following keys"""
FIELDS = ['benchmarkName', 'user', 'type', 'metric', 'metricValue']

class LeaderBoard:
    """The main class for the leaderboard."""

    def __init__(self, jsonFileName, localtest=False):
        """Initialize required vars for the leaderboard class."""
        self.jsonFileName = jsonFileName
        self.serverUrl = URL
        if localTest:
            self.serverUrl = URL_LOCAL
        logger.info('Server URL = %s', self.serverUrl)

    def validateRecord(self, record):
        """validate the json record."""
        keys = record.keys()
        for key in keys:
            print(key)
            if key not in FIELDS:
                logger.info('key %s is missing in JSON file' % key)
                sys.exit(2)

    def importJsonFile(self, jsonFileName):
        """Read the json file."""
        with open(jsonFileName) as json_data:
            data = json.load(json_data)
            for record in data:
                benchmarkName = record['benchmarkName']
                if 'benchmarkName' in record.keys():
                    if benchmarkName in VALID_BENCHMARKS:
                        logger.info('sending record to server')
                        print(record)
                        print(benchmarkName)
                        self.sendJsonData(record)
                    else:
                        logger.info('benchmark name %s not found' %
                                    benchmarkName)
                else:
                    logger.info('benchmarkName key is missing in JSON file')
                    sys.exit(2)

    def sendJsonData(self, record):
        """Send the json record."""
        idStr = str(uuid.uuid4())
        URL_VAL = self.serverUrl+'/insert/'+idStr
        try:
            res = requests.post(URL_VAL, json=record)
            if res.ok:
                content = res.json()
                idStrRet = content['uuid']
                if idStr == idStrRet:
                    logger.info('insertion success')
        except:
            logger.info('error in inserting record to DB: %s' %
                        sys.exc_info()[0])

    def printResult(self, result):
        """print the result; the result should iterator data type (list)."""
        if len(results) > 0:
            for i, record in enumerate(result):
                logger.info('%d ==> %s' % (i, record))

    def saveJsonResults(self, results, outputJsonFileName):
        """print the result; """
        if len(results) > 0:
            if outputJsonFileName is None:
                print(json.dumps(results, indent=4, sort_keys=True))
            else:
                try:
                    with open(outputJsonFileName, 'w') as outfile:
                        json.dump(results, outfile, indent=4, sort_keys=True)
                except:
                    logger.info('error in writing to file: %s' %
                                sys.exc_info()[0])

    def queryBenchmarkResults(self, benchmarkName):
        """Query the benchmark table for the given benchmark name."""
        URL_VAL = self.serverUrl+'/query/'+str(benchmarkName)
        results = []
        if benchmarkName not in VALID_BENCHMARKS:
            logger.info('Not a valid benchmark name: %s' % benchmarkName)
            logger.info('Query with valid benchmark name')
            return results
        try:
            res = requests.post(URL_VAL)
            if res.ok:
                content = res.json()
                results = content['results']
        except:
            logger.info('error in getting results from DB: %s' %
                        sys.exc_info()[0])
        return results

if __name__ == '__main__':
    jsonFileName = None
    benchmarkName = None
    outputJsonFileName = None
    outputJsonFileName = False
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.1')
    parser.add_argument('-o', '--outputJsonFileName', action='store',
                        dest='outputJsonFileName',
                        help='Json file name to write the results from query')
    parser.add_argument('--local', action='store_true', dest='localTest',
                        help=argparse.SUPPRESS)
    group = parser.add_argument_group('required arguments')
    group.add_argument('-i', '--importJsonFileName', action='store',
                       dest='jsonFileName',
                       help='Json file that need to be imported')
    group.add_argument('-q', '--queryBenchmarkname', action='store',
                       dest='benchmarkName', help='benchmark name to query')
    cmdLineArgs = parser.parse_args()
    if cmdLineArgs.benchmarkName is not None:
        logger.info('Benchmark name = %s', cmdLineArgs.benchmarkName)
    if cmdLineArgs.jsonFileName is not None:
        logger.info('Import JSON filename = %s', cmdLineArgs.jsonFileName)
    if cmdLineArgs.outputJsonFileName is not None:
        logger.info('Output JSON filename = %s',
                    cmdLineArgs.outputJsonFileName)
    if cmdLineArgs.localTest:
        logger.info('Local test flag = %s', cmdLineArgs.localTest)

    jsonFileName = cmdLineArgs.jsonFileName
    benchmarkName = cmdLineArgs.benchmarkName
    outputJsonFileName = cmdLineArgs.outputJsonFileName
    localTest = cmdLineArgs.localTest

    """ Initialize LeaderBoard class """
    lb = LeaderBoard(jsonFileName, localTest)

    """ Upload the data in the json file """
    if jsonFileName is not None:
        lb.importJsonFile(jsonFileName)

    if benchmarkName is not None:
        results = lb.queryBenchmarkResults(benchmarkName)
        lb.saveJsonResults(results, outputJsonFileName)
