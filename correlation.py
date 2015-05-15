import math


# ls1 = [0.,0.0998334,0.198669,0.29552,0.389418,0.479426,0.564642,0.644218,0.717356,0.783327,0.841471,0.891207,0.932039,0.963558,0.98545,0.997495,0.999574,0.991665,0.973848,0.9463,0.909297,0.863209,0.808496,0.745705,0.675463,0.598472,0.515501,0.42738,0.334988,0.239249,0.14112,0.0415807,-0.0583741,-0.157746,-0.255541,-0.350783,-0.44252,-0.529836,-0.611858,-0.687766,-0.756802,-0.818277,-0.871576,-0.916166,-0.951602,-0.97753,-0.993691,-0.999923,-0.996165,-0.982453,-0.958924,-0.925815,-0.883455,-0.832267,-0.772764,-0.70554,-0.631267,-0.550686,-0.464602,-0.373877,-0.279415,-0.182163,-0.0830894,0.0168139,0.116549,0.21512,0.311541,0.40485,0.494113,0.57844,0.656987,0.728969,0.793668,0.850437,0.898708,0.938,0.96792,0.988168,0.998543,0.998941,0.989358,0.96989,0.940731,0.902172,0.854599,0.798487,0.734397,0.662969,0.584917,0.501021,0.412118,0.319098,0.22289,0.124454,0.0247754,-0.0751511,-0.174327,-0.271761,-0.366479,-0.457536,-0.544021]

# ls2 = [-0.841471,-0.783327,-0.717356,-0.644218,-0.564642,-0.479426,-0.389418,-0.29552,-0.198669,-0.0998334,0.,0.0998334,0.198669,0.29552,0.389418,0.479426,0.564642,0.644218,0.717356,0.783327,0.841471,0.891207,0.932039,0.963558,0.98545,0.997495,0.999574,0.991665,0.973848,0.9463,0.909297,0.863209,0.808496,0.745705,0.675463,0.598472,0.515501,0.42738,0.334988,0.239249,0.14112,0.0415807,-0.0583741,-0.157746,-0.255541,-0.350783,-0.44252,-0.529836,-0.611858,-0.687766,-0.756802,-0.818277,-0.871576,-0.916166,-0.951602,-0.97753,-0.993691,-0.999923,-0.996165,-0.982453,-0.958924,-0.925815,-0.883455,-0.832267,-0.772764,-0.70554,-0.631267,-0.550686,-0.464602,-0.373877,-0.279415,-0.182163,-0.0830894,0.0168139,0.116549,0.21512,0.311541,0.40485,0.494113,0.57844,0.656987,0.728969,0.793668,0.850437,0.898708,0.938,0.96792,0.988168,0.998543,0.998941,0.989358,0.96989,0.940731,0.902172,0.854599,0.798487,0.734397,0.662969,0.584917,0.501021,0.412118]

ls1 = [1, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
ls2 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0];



times = range(len(ls1))
times = [2*i for i in range(len(ls1))]
# print times

# turn into dictionary where keys are the time and values are the price at that time
d1 = dict(zip(times,ls1))
d2 = dict(zip(times,ls2))


def getCorrelation(times, d1, d2, maxdays=20):
    # This function requires a list of times, and dictionaries of 
    # time:value pairs for two stocks

    # Here I compute G(tau) = (1/N)*integral of f(t)g(t+tau) dt
    G = {}

    # we want to find the correlation time if it's between say 0 time 
    # units and maxdays time units
    # if maxdays>the amount of timestamps we have, just use the latter
    # time units will be something like [1 day, 2 days, 3 days, etc.]
    timeunits = [int(times[i] - times[0]) for i in range(min(len(times), maxdays))]
    # actually, we want timeunits to possibly include weekends, and we
    # will set the weekend price to the closing price on the last
    # weekday to avoid this weird week peak problem
    timeunits = [i for i in range(min(len(times), maxdays))]

    # scan over correlation times
    for tau in timeunits:
        s = 0.0
        # perform integral
        for i in range(len(times)):
            # we require that we are within the range of times for d2
            try:
                # if times[i] + tau <= len(d2.keys()):
                # f(t) g(t+tau) dt
                dt = 1.0* (times[i+1] - times[i])
                s += 1.0*(d1[ times[i] ] * d2[ times[i] +tau ] * dt)
            except: pass

        G[tau] = s/len(times) # multiply by 1/N

    # Now normalize by G(tau=0)
    norm = G[0]
    for tcorr in G.keys():
        G[tcorr] = G[tcorr]/norm

    return G

def findPeak(d1):
    # XXX CHANGEME. RIGHT NOW IT JUST FINDS THE MAXIMUM, BUT WE WANT A TRUE PEAKFINDER
    # This function requires a dictionary of time:value pairs
    maxkey, maxval = 0.0, 0.0
    for key in d1:
        if(key == 0.0): continue # obviously, we don't care about the initial peak

        if d1[key] > maxval:
            maxkey, maxval = key, d1[key]
    return (maxkey, maxval)

# G = getCorrelation(times, d1, d2)
# print G
# print findPeak(G)
    



