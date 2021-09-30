import numpy as np
from LPsolver import SolveLP
from rounding import cache_by_cache_pipage_rounding
from Phi import phi
from Phi2 import phi2
import math
# the data will come in a table with variable name cache_request
# where every row gives us the information about which user wants to access which file at that time t
# cache_request is the data matrix of form T*I
# Adj is the adjacency matrix of the network is of the form I*J
# T is the time uptill you want to run
# F is the libtrary size
# We just need to return the number of hit rates
# C is the number of files per cache
# returns a list of hit_rate over time.

def Lead_cache(cache_request, Adj, T, F, C, d):
    
    hit_rate = []
    I, J = np.shape(Adj)
    
    #gamma has to be of the form I*F
    gamma = np.random.normal(0, 1, (I, F))
    eta_constant = math.pow(F, 0.75)/(math.pow(2*(math.log(I/C) + 1), 0.5)*(math.pow(d*J*C, 0.5)))
    
    X = np.zeros((I,F)) # this cumulative
    x = np.zeros((I,F)) # at time instance t
    # we can just sample gamma once this does not change the upper bound gurarantees 
    
    for t in range(T):

        theta = np.maximum(X + eta_constant*(math.pow((t+1),0.5))*gamma, 0) # taking the non-negative part of theta only
        if t>0:
        	(Y_f, prev) = SolveLP(Adj, theta, C, start, t) # solves the LP and gets a fractional solution 
        else:
            (Y_f, prev) = SolveLP(Adj, theta, C, 0, t) # dummy initializaton for t=0

        start = prev # setting the next initialization
        Y = cache_by_cache_pipage_rounding(Y_f, theta, Adj) # rounding
        
        #updating X
        for i in range(I):
            x[i][cache_request[i][t]] += 1
            X[i][cache_request[i][t]] += 1
            
        hit_rate.append(phi2(Adj, Y, x))
        #reverting X back to zero
        for i in range(I):
            x[i][cache_request[i][t]] -= 1
        
    return hit_rate
