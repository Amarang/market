import urllib, urllib2, json, time, datetime, math
import correlation

stockSymbol = "AA"
storageFolder = "storage/"

def getStock(stockSymbol, saveToTxt=False, loadFromSite=True):
    # print ">>> Fetching", stockSymbol
    fetchDict={"Normalized":"False","NumberOfDays":365,"DataPeriod":"Day","Elements":[{"Symbol":stockSymbol,"Type":"price","Params":["ohlc"]}]} # XXX
    # fetchDict={"Normalized":"False","NumberOfDays":25,"DataPeriod":"Day","Elements":[{"Symbol":stockSymbol,"Type":"price","Params":["ohlc"]}]}

    source = ""
    if(loadFromSite):
        source = urllib.urlopen(
            "http://dev.markitondemand.com/Api/v2/InteractiveChart/json?parameters=%s" % fetchDict
            ).read()
        if(len(source) < 100):
            print "Malformed data for", stockSymbol
            return
    else:
        fh = open("%s%sstock.txt" % (storageFolder, stockSymbol), "r")
        source = fh.read()
        fh.close()

    if(saveToTxt): 
        fh = open("%s%sstock.txt" % (storageFolder, stockSymbol), "w")
        fh.write(source)
        fh.close()
        print "Saved stock info for %s" % stockSymbol
        return 

    data = json.loads(source)

    dates =  data["Dates"]
    # the dates look like  2015-04-29T00:00:00  so we want to get rid of the T00 crap
    dates = map(lambda s: s.split("T")[0],dates)
    # convert them into unix time stamps
    timestamps = map(lambda s: time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d").timetuple()), dates)
    # convert them into days since 2000 to make numbers more readable
    timestamps = map(daysSince2000, timestamps)

    # shortcut to DataSeries
    dataseries = data["Elements"][0]["DataSeries"]

    # make a dictionary where we have open,high,low,close as keys and the corresponding prices as values
    values = {}
    values["open"]  = dataseries["open"]["values"]
    values["high"]  = dataseries["high"]["values"]
    values["low"]   = dataseries["low"]["values"]
    values["close"] = dataseries["close"]["values"]

    # make a dictionary to store all the stock's information
    stock = {}
    stock["dates"] = dates
    stock["timestamps"] = timestamps
    stock["values"] = values
    stock["symbol"] = stockSymbol

    return stock

def daysSince2000(unixtimestamp):
    return 1.0*(unixtimestamp-946684800)/86400
    

def printStock(stock):

    timestamps = stock["timestamps"]
    dates = stock["dates"]
    values = stock["values"]

    # print all the crap out nicely
    print ">>> Stock for %s" % stock["symbol"]
    print "%10s\t%10s\t%5s\t%5s\t%5s\t%5s" % ("date", "timestamp", "open", "high", "low", "close")
    print "-"*70
    for i in range(len(timestamps)):
        print "%10s\t%10s\t%5.2f\t%5.2f\t%5.2f\t%5.2f" % ( dates[i], str(timestamps[i]),
                values["open"][i],
                values["high"][i],
                values["low"][i],
                values["close"][i] )


def correlationTime(s1, s2):
    timestamps = s1["timestamps"]
    # let's just look at closing prices
    d1 = dict( zip(  timestamps , s1["values"]["close"] ) )
    d2 = dict( zip(  timestamps , s2["values"]["close"] ) )

    G = correlation.getCorrelation( timestamps, d1, d2, maxtimeunits=20 )
    peak = correlation.findPeak(G)

    # print "test={",
    # for key in G.keys():
    #     print "{",key,",",G[key],"},",
    # print "}"

    return peak
        

# symbols = ["EXR", "STON", "RGA", "BPK", "KPTI", "SKYW", "ETW"] #, "AA", "AAPL", "INTC"]
        
# for symbol in symbols: getStock(symbol, saveToTxt=True)
# getStock("DIS", saveToTxt=True)
# getStock("AA", saveToTxt=True)
# getStock("AAPL", saveToTxt=True)
# getStock("INTC", saveToTxt=True)


stocks = {}
symbols = ["RGA", "KPTI", "SKYW"] #, "AA", "AAPL", "INTC"]
# symbols = ["DIS", "AA", "AAPL", "INTC"]
for symbol in symbols:
    stocks[symbol] = getStock(symbol)

for symbol1 in stocks.keys():
    # print symbol1, symbol1, correlationTime(stocks[symbol1], stocks[symbol1])
    for symbol2 in stocks.keys():
        print symbol1, symbol2, correlationTime(stocks[symbol1], stocks[symbol2])
