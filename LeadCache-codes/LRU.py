import numpy as np
import random
from Phi import phi
import copy
def Bipartite_LRU(file_request, Adj, T, F, C):
    
    hit_rate = []
    download_rate = []
    I, J = np.shape(Adj)
    
    X = np.zeros((I,F)) # this cumulative
    x = np.zeros((I,F)) # it is at time instance t
    # we can just sample gamma once this does not change the upper bound gurarantees 
    LRU_cache = [] # each cache is such that the last element of the list is most recently used and the first element of the array is least
    
    # cache files in the beginning at random
    for cache in range(J):
        LRU_cache.append(random.sample(range(F), C))
    
    prev_cache = copy.deepcopy(LRU_cache)
    for t in range(T):
        
        hits = 0
        
        #calculates the number of hits
        for user in range(I):
            for cache in np.flatnonzero(Adj[user][:]):
                if file_request[user][t] in LRU_cache[cache]:
                    hits += 1
                    break
                    
        hit_rate.append(hits)
        
        #for each cache the files that were requested 
        cache_file_request = [set() for j in range(J)]
        
        for user in range(I):
            for cache in np.flatnonzero(Adj[user][:]):
                cache_file_request[cache].add(file_request[user][t])
        
        for cache in range(J): #going through every cache to update the files 
            
            files = list(set(list(cache_file_request[cache])))
            for file in files: 
                if file in LRU_cache[cache]:  #if a file requested by one of the users is not there 
                    LRU_cache[cache].remove(file)
                else:                         #otherwise
                    if (len(LRU_cache[cache]) > 0):
                        LRU_cache[cache].pop(0) #take the least recently used file out
                LRU_cache[cache].append(file)   #push the most recently file on the top 
               
        
        #calculate download rate
       
        download = 0
        for cache_index in range(J):
            for file in LRU_cache[cache_index]:
                
                if file not in prev_cache[cache_index]:
                    download = download + 1

        prev_cache = copy.deepcopy(LRU_cache)
        download_rate.append(download)
        
    return hit_rate, download_rate      