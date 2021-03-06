import matplotlib as mpl
mpl.use('Agg') # http://stackoverflow.com/questions/4931376/generating-matplotlib-graphs-without-a-running-x-server
import matplotlib.pyplot as plt


def listPlot(ls, filename, title=""):
    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=20)
    ax.plot(range(len(ls)), ls, 'ro-')
    fig.savefig("/home/Nick/desktop/market/plots/%s" % filename, bbox_inches='tight')



def dictPlot(d, filename, title=""):
    # d = { 1: 2, 2: 5, 1.5: 6, 8: 0.3 }

    xvals = d.keys()
    yvals = map(lambda x: d[x], xvals)

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=20)

    ax.plot(xvals, yvals, 'ro-')
    fig.savefig("./plots/%s" % filename, bbox_inches='tight')

