import numpy as np
import random
from Phi import phi
import copy

def Bipartite_LFU(file_request, Adj, T, F, C):
    
    hit_rate = []
    download_rate = []
    I, J = np.shape(Adj)
    
    X = np.zeros((I,F)) # this cumulative
    x = np.zeros((I,F)) # it is at time instance t
    # we can just sample gamma once this does not change the upper bound gurarantees 
    LFU_cache = [] # each cache is such that the last element of the list is most recently used and the first element of the array is least
    frequency = np.zeros((J,F)) #the frequency of every file requested in that cache
    
    #in the beginning start with random files on every cache 
    for cache in range(J):
        LFU_cache.append(random.sample(range(F), C))
    
    prev_cache = copy.deepcopy(LFU_cache)
    for t in range(T):
        
        hits = 0
        #calculates the number of hits
        for user in range(I):
            for cache in np.flatnonzero(Adj[user][:]):
                if file_request[user][t] in LFU_cache[cache]:
                    hits += 1
                    break
                    
        hit_rate.append(hits)
        cache_file_request = [dict() for j in range(J)] # dictonary for each cache and the frequency of the files requested on each of these caches 
        
        #basically a counter to count the frequency 
        for user in range(I):
            for cache in np.flatnonzero(Adj[user][:]):
                if not file_request[user][t]  in cache_file_request[cache]: 
                    cache_file_request[cache][file_request[user][t]] = 1
                else:
                    cache_file_request[cache][file_request[user][t]] += 1
        
        download = 0
        for cache in range(J):
            files = cache_file_request[cache].keys()
            for file in files:
                frequency[cache][file] += cache_file_request[cache][file] #updating the frequency of the files in the cache
                # here we need to update frequency if the file is in the cache 
                # otherwise we would need to update the frequency and check if we can replace some other file with less frequency 
                # with this file
                
                if not file in LFU_cache[cache]:   
                    if (len(LFU_cache[cache]) > 0):
                        min_freq_file_index = 0
                        
                        for file_index in range(C):
                            if(frequency[cache][min_freq_file_index] > frequency[cache][file_index]):
                                min_freq_file_index = file_index
                                
                        LFU_cache[cache].pop(min_freq_file_index)
                    LFU_cache[cache].append(file)
        
        download = 0
        for cache_index in range(J):
            for file in LFU_cache[cache_index]:
                if file not in prev_cache[cache_index]:
                    download = download + 1

        prev_cache = copy.deepcopy(LFU_cache)
        download_rate.append(download)
        
    
    return hit_rate, download_rate       