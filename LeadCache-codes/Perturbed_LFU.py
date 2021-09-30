import numpy as np
import random
from Phi import phi
import copy
import math

def Perturbed_Bipartite_LFU(cache_request, Adj, T, F, C, d):
    
    hit_rate = []
    download_rate = []
    
    I, J = np.shape(Adj)
    sanity_check = True # verify if every caching configuration was admissible 
    
    #gamma has to be of the form J*F
    # we can just sample gamma once this does not change the upper bound gurarantees 
    gamma = np.random.normal(0, 1, (J, F))
    
    eta_constant = d/(math.pow(4*math.pi*math.log(F/C)*C*C, 0.25))
    constr_violation_tol = 1.0
    #eta_constant = 0
    
    Xr = np.zeros((J,F)) # this accounts for the cumulative file request 

    for t in range(T):
        theta = Xr + eta_constant*(math.pow((t+1),0.5))*gamma #adding perturbations to cumulative frequency
        
        top_file_indices = np.argpartition(theta, -C, axis=1)[:, -C:]
        
        Y = np.zeros((J,F))

        for cache in range(J):
            for file in range(C):
                Y[cache][top_file_indices[cache][file]] = 1

        #calculating download_rate
        
        if(t> 0):
            difference = Y - Y_prev
            download = np.sum(difference[difference > 0]) 
            download_rate.append(download)
            Y_prev = copy.deepcopy(Y)
        else:
            Y_prev = copy.deepcopy(Y)
        #verify if the cache configurations are valid
        
        if(np.any(np.sum(Y,axis = 1) > C+ constr_violation_tol)): # checks if all the caches has less than or equal to C files
           
            print("trying to cache more than capacity")
            sanity_check = False
            
        #print('cache configuration',Y)
        #updating Xr
        for user in range(I):
            for cache in np.flatnonzero(Adj[user][:]):
                    Xr[cache][cache_request[user][t]] += 1
        #print('\n cumulative file request', Xr)
            
        # calculates the number of hits
        hits = 0
        
        for user in range(I): # goes through every user
            present = 0 
            for cache in np.flatnonzero(Adj[user][:]): # goes through every cache the user is connected to
                if Y[cache][int(cache_request[user][t])] > 0.9998: #checks if the requested file at time t is present in the cache configuration and we also deal with precision error
                    present = 1
                    break
            hits += present
            
           
        hit_rate.append(hits) 

    if(sanity_check == False):
        print("trying to cache more than capacity")
        
    return hit_rate, download_rate
