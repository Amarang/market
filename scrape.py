import urllib, urllib2, json, time, datetime, math
import correlation, plot
import random

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
    timestamps = map(UTCtoDaysSince2000, timestamps)

    # shortcut to DataSeries
    dataseries = data["Elements"][0]["DataSeries"]

    # print timestamps

    # timestamps = timestamps[:30] # XXX
    pricesClose, newTimestamps, newDates = [], [], []
    prevWeekday = timestamps[0]-1
    prevPrice = dataseries["close"]["values"][0]
    daysIntoWeekend = 0
    for i,day in enumerate(timestamps):
        if day != prevWeekday + 1:
            daysIntoWeekend += 1
            # then this is a weekend, so add last weekday's price
            newTimestamps.append(prevWeekday+daysIntoWeekend)
            newDates.append( daysSince2000toUTC(prevWeekday+daysIntoWeekend) )
            pricesClose.append(prevPrice)
        else:
            newTimestamps.append(day)
            newDates.append( daysSince2000toUTC(day) )
            pricesClose.append( dataseries["close"]["values"][i] )
            prevPrice = dataseries["close"]["values"][i]

            daysIntoWeekend = 0
            prevWeekday = day

    print newTimestamps
    print newDates
    print pricesClose



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

def UTCtoDaysSince2000(unixtimestamp):
    return int(1.0*(unixtimestamp-946684800)/86400)
    
def daysSince2000toUTC(ds2000):
    return 1.0*ds2000*86400+946684800

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
    s1vals = s1["values"]["close"] 
    s2vals = s2["values"]["close"] 

    # # generate dummy data XXX XXX
    # timestamps = [i for i in range(len(s1vals))]
    # newvals = [random.random()*10+20 for i in range(len(s1vals))]
    # s1vals, s2vals = newvals, newvals


    d1 = dict( zip(  timestamps , s1vals ) )
    d2 = dict( zip(  timestamps , s2vals ) )

    G = correlation.getCorrelation( timestamps, d1, d2, maxdays=30 )
    peak = correlation.findPeak(G)

    plot.plotDict(G, "pcorr.png")

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
# symbols = ["RGA", "KPTI", "SKYW"] #, "AA", "AAPL", "INTC"]
# symbols = ["DIS", "AA", "AAPL", "INTC"]
symbols = ["DIS"]

for symbol in symbols:
    stocks[symbol] = getStock(symbol, loadFromSite=False)

for symbol1 in stocks.keys():
    # print symbol1, symbol1, correlationTime(stocks[symbol1], stocks[symbol1])
    for symbol2 in stocks.keys():
        print symbol1, symbol2, correlationTime(stocks[symbol1], stocks[symbol2])
