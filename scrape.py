import urllib, urllib2, json, time, datetime, math

stockSymbol = "AA"
storageFolder = "storage/"

def getStock(stockSymbol, saveToTxt=False, loadFromSite=True):
    # fetchDict={"Normalized":"False","NumberOfDays":365,"DataPeriod":"Day","Elements":[{"Symbol":stockSymbol,"Type":"price","Params":["ohlc"]}]} # XXX
    fetchDict={"Normalized":"False","NumberOfDays":25,"DataPeriod":"Day","Elements":[{"Symbol":stockSymbol,"Type":"price","Params":["ohlc"]}]}

    source = ""
    if(loadFromSite):
        source = urllib.urlopen(
            "http://dev.markitondemand.com/Api/v2/InteractiveChart/json?parameters=%s" % fetchDict
            ).read()
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


def correlation(s1, s2):
    pass
    # for price in s1["values"]["close"]:
        


# getStock("DIS", saveToTxt=True)
# getStock("AA", saveToTxt=True)
# getStock("AAPL", saveToTxt=True)
# getStock("INTC", saveToTxt=True)

intc = getStock("INTC")
aapl = getStock("AAPL")


correlation(intc, aapl)

printStock(intc)
