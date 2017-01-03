from flask import Flask, request, jsonify
from pymongo import MongoClient
import logging
import sys
import json
import os.path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def readDBConfigFile(dbConfigFileName):
    dbConfigDict = {}
    try:
        with open(dbConfigFileName) as jsonData:
            mongoDbConfig = json.load(jsonData)
        mongoDbConfig = mongoDbConfig[0]
        dbConfigDict['server'] = mongoDbConfig['server']
        dbConfigDict['port'] = mongoDbConfig['port']
        dbConfigDict['username'] = mongoDbConfig['username']
        dbConfigDict['password'] = mongoDbConfig['password']
        dbConfigDict['dbname'] = mongoDbConfig['dbname']
    except:
        logger.info('error in reading file: %s' % sys.exc_info()[0])
        sys.exit(2)
    return dbConfigDict

def connect(dbConfigDict):
    dbClient = None
    try:
        connection = MongoClient(dbConfigDict['server'], dbConfigDict['port'])
        dbClient = connection[dbConfigDict['dbname']]
        dbClient.authenticate(dbConfigDict['username'],
                              dbConfigDict['password'])
    except:
        logger.info('error in connecting to MongoDB: %s' % sys.exc_info()[0])
        sys.exit(2)
    return dbClient

app = Flask(__name__)
dbConfigFileName = '../mongoDbConfig.json'
if not os.path.isfile(dbConfigFileName):
    logger.info('db config file %s does not exist' % dbConfigFileName)
dbConfigDict = readDBConfigFile(dbConfigFileName)
print dbConfigDict
candle = connect(dbConfigDict)


@app.route("/leaderboard")
def ping():
    return "Welcome to leaderboard!\n"


@app.route("/leaderboard/test")
def test():
    return "Leaderboard test OK!\n"


@app.route('/leaderboard/insert/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):
    try:
        record = request.json
        benchmarkName = record['benchmarkName']
        candle[benchmarkName].insert(record)
    except:
        logger.info('error in inserting record to db: %s' % sys.exc_info()[0])
        uuid = -1
    return jsonify({"uuid": uuid})


@app.route('/leaderboard/query/<bname>', methods=['GET', 'POST'])
def queryBenchmarkResults(bname):
    """Query the benchmark table for the given benchmark name."""
    results = []
    benchmarkName = bname
    print benchmarkName
    if benchmarkName is not None:
        try:
            benchmarkData = candle[benchmarkName]
            results = list(benchmarkData.find({}, {'_id': 0}))
            logger.info('number of records fetched: %s' % len(results))
        except:
            logger.info('error in fetching record from db: %s' %
                        sys.exc_info()[0])
    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7137, debug=True)
