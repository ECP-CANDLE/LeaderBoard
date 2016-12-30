from os.path import join, dirname
import datetime
import os.path
import sys
import pandas as pd
import json
from scipy.signal import savgol_filter

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.palettes import Blues4
from bokeh.plotting import figure

from pymongo import MongoClient
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


VALID_BENCHMARKS = ['P1B1', 'P1B2', 'P1B3', 'P2B1', 'P2B2', 'P2B3', 'P3B1',
                    'P3B2', 'P3B3']

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

def get_dataset(allDF, name):
    benchmarkDF = allDF[allDF.benchmarkName == name].copy()
    return ColumnDataSource(data=benchmarkDF)

def make_plot(source, title):
    plot = figure(x_axis_type="datetime", plot_width=800,
                  tools="crosshair,pan,reset,save,wheel_zoom",
                  toolbar_location=None)
    plot.title.text = title
    plot.line('unixTimeStamp', 'metricValue', source=source, line_width=3,
              line_alpha=0.6)
    plot.xaxis.axis_label = "Time"
    plot.yaxis.axis_label = "Accuracy"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.grid.grid_line_alpha = 0.3
    return plot

def update_plot(attrname, old, new):
    benchmark = benchmark_select.value
    plot.title.text = 'Leaderboard results for '+benchmark
    src = get_dataset(allDF, benchmark)
    # source.data.update(src.data)
    source.data = src.data

def printResult(result):
    """print the result; the result should iterator data type (list)."""
    for i, record in enumerate(result):
        print i, '==>', record


dbConfigFileName = '../mongoDbConfig.json'
if not os.path.isfile(dbConfigFileName):
    logger.info('db config file %s does not exist' % dbConfigFileName)
dbConfigDict = readDBConfigFile(dbConfigFileName)
print dbConfigDict
candle = connect(dbConfigDict)

allDF = pd.DataFrame()
for bname in VALID_BENCHMARKS:
    if bname in candle.collection_names():
        collection = candle[bname]
        result = list(collection.find({}, {'_id': 0, 'installedPackages': 0}))
        printResult(result)
        df = pd.DataFrame(result)
        allDF = allDF.append(pd.DataFrame(data=df), ignore_index=True)
print allDF


benchmark = allDF['benchmarkName'].values.tolist()[0]
benchmark_select = Select(value=benchmark, title='Benchmarks',
                          options=sorted(VALID_BENCHMARKS))

source = get_dataset(allDF, benchmark)
plot = make_plot(source, 'CANDLE Leaderboard Results for ' + benchmark)
benchmark_select.on_change('value', update_plot)
controls = column(benchmark_select)
curdoc().add_root(row(plot, controls))
curdoc().title = "CANDLE Leaderboard"
