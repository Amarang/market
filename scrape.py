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
        # return 

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


    # the stock market data does not have weekends, so we 
    # add them in and use the price from the last weekday
    newPricesClose, newTimestamps, newDates = [], [], []
    prevWeekday = timestamps[0]-1
    prevClosing = dataseries["close"]["values"][0]
    for i,day in enumerate(timestamps):
        if day != prevWeekday+ 1:
            # then this is a Monday, so add weekend days with
            # last weekday's price
            for daysIntoWeekend in range(1,day - prevWeekday ):
                newTimestamps.append(prevWeekday+daysIntoWeekend)
                newDates.append( daysSince2000toUTC(prevWeekday+daysIntoWeekend) )
                newPricesClose.append(prevClosing)

            #  since we're on Monday, we need to set the previous day to a Sunday
            prevWeekday = day-1
       
        # not if-else, because if we just finished up a weekend, then we need
        # to take care of Monday
        if day == prevWeekday + 1:
            newTimestamps.append(day)
            newDates.append( daysSince2000toUTC(day) )
            newPricesClose.append( dataseries["close"]["values"][i] )
            prevClosing = dataseries["close"]["values"][i]
            prevWeekday = day


    # make a dictionary where we have open,high,low,close as keys and the corresponding prices as values
    values = {}
    # values["open"]  = dataseries["open"]["values"]
    # values["high"]  = dataseries["high"]["values"]
    # values["low"]   = dataseries["low"]["values"]
    # values["close"] = dataseries["close"]["values"]
    values["close"] = newPricesClose

    # make a dictionary to store all the stock's information
    stock = {}
    # stock["dates"] = dates
    # stock["timestamps"] = timestamps
    stock["dates"] = newDates
    stock["timestamps"] = newTimestamps
    stock["values"] = values
    stock["symbol"] = stockSymbol
    # stock["dates"] = dates
    # stock["timestamps"] = timestamps

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
    # print "%10s\t%10s\t%5s\t%5s\t%5s\t%5s" % ("date", "timestamp", "open", "high", "low", "close")
    print "%10s\t%10s\t%5s" % ("date", "timestamp", "close")
    print "-"*70
    for i in range(len(timestamps)):
        # print "%10s\t%10s\t%5.2f\t%5.2f\t%5.2f\t%5.2f" % ( dates[i], str(timestamps[i]),
        #         values["open"][i],
        #         values["high"][i],
        #         values["low"][i],
        #         values["close"][i] )
        print "%10s\t%10s\t%5.2f" % ( dates[i], str(timestamps[i]), values["close"][i] )


def correlationTime(s1, s2):
    timestamps = s1["timestamps"]
    # let's just look at closing prices
    s1vals = s1["values"]["close"] 
    s2vals = s2["values"]["close"] 

    # # generate dummy data XXX XXX
    # timestamps = [i for i in range(365)]
    # newvals = [random.random()*10+20 for i in range(365)]
    # # newvals = [abs(math.sin(2.0*3.14159 * i / 14.0)) for i in range(365)]
    # # newvals = [math.sin(2.0*3.14159 * i / 14.0) for i in range(365)]
    # newvals = scalePoints(newvals)
    # s1vals, s2vals = newvals, newvals

    # s1vals = correlation.deviationFromAvg( s1vals )
    # s2vals = correlation.deviationFromAvg( s2vals )

    s1vals = correlation.dailyChange( s1vals )
    s2vals = correlation.dailyChange( s2vals )


    # print len(s1vals), len(correlation.dailyChange(s1vals))

    # newvals = scalePoints(s2vals)
    d1 = dict( zip(  timestamps , s1vals ) )
    d2 = dict( zip(  timestamps , s2vals ) )

    G = correlation.getCorrelation( timestamps, d1, d2, maxdays=20 )
    peak = correlation.findPeak(G)

    plot.listPlot(s1vals, "pcorr1.png")
    plot.listPlot(s2vals, "pcorr2.png")
    plot.dictPlot(G, "pcorr.png")

    # print "test={",
    # for key in G.keys():
    #     print "{",key,",",G[key],"},",
    # print "}"

    return peak
    # return ""
        

# symbols = ["EXR", "STON", "RGA", "BPK", "KPTI", "SKYW", "ETW"] #, "AA", "AAPL", "INTC"]
        
# for symbol in symbols: getStock(symbol, saveToTxt=True)
# getStock("DIS", saveToTxt=True)
# getStock("AA", saveToTxt=True)
# getStock("AAPL", saveToTxt=True)
# getStock("INTC", saveToTxt=True)


stocks = {}
# symbols = ["AAPL", "INTC"]
symbols = ["V", "MA"]


for symbol in symbols:
    stocks[symbol] = getStock(symbol, loadFromSite=False)

correlationTime(stocks["V"], stocks["MA"])

# for symbol1 in stocks.keys():
#     # print symbol1, symbol1, correlationTime(stocks[symbol1], stocks[symbol1])
#     for symbol2 in stocks.keys():
#         print symbol1, symbol2, correlationTime(stocks[symbol1], stocks[symbol2])
