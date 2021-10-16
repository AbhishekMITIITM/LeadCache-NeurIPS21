import numpy as np
import math
import random
import copy



def MIN(df, Adj, time, library_size, C):

    hit_rate = []
    download_rate = []
    I, J = np.shape(Adj)
    
    X = np.zeros((I,library_size)) # this cumulative
    x = np.zeros((I,library_size)) # it is at time instance t
    # we can just sample gamma once this does not change the upper bound gurarantees 
    MIN_cache = [] # each cache is such that the last element of the list is most recently used and the first element of the array is least
    
    # cache files in the beginning at random
    for cache in range(J):
        MIN_cache.append(random.sample(range(library_size), C))
    
    prev_cache = copy.deepcopy(MIN_cache)

    request_time = []

    pointer = np.zeros((J, library_size))

    for cache in range(J):

        future_request = []
        for file in range(library_size):
            future_request.append([])
        
        for t in range(time):
            for user in np.flatnonzero(Adj[:,cache]):
                #print(df[user])
                file_request = df[user][t]
            future_request[file_request].append(t)

        for file in range(library_size):          # adding a dummy for infinity
            future_request[file].append(time + 1)

        request_time.append(future_request)


    for t in range(time):

        hits = 0
        
        #calculates the number of hits
        for user in range(I):
            for cache in np.flatnonzero(Adj[user][:]):
                if df[user][t] in MIN_cache[cache]:
                    hits += 1
                    break
                    
        hit_rate.append(hits)
        
        #for each cache the files that were requested 
        cache_file_request = [set() for j in range(J)]
        
        for user in range(I):
            for cache in np.flatnonzero(Adj[user][:]):
                cache_file_request[cache].add(df[user][t])
        #print(MIN_cache, "\n")
        for cache in range(J): #going through every cache to update the files 
            
            files = list(set(list(cache_file_request[cache])))
            for file in files: 
                if not file in MIN_cache[cache]:  #if a file requested by one of the users is not there
                #remove the file which is requested the furthest in time 
                    index_remove = -1
                    furtest_time = -1

                    for f_idx in range(len(MIN_cache[cache])): 

                        f = MIN_cache[cache][f_idx]
                        time_sequence = request_time[cache][f] # this is definitley non-empty 
                        #print(time_sequence, int(pointer[cache][f]))
                        while time_sequence[int(pointer[cache][f])]<=t: # the next time the file f was requested from the cache 
                            pointer[cache][f] +=1

                        if furtest_time < time_sequence[int(pointer[cache][f])]:
                            furtest_time = time_sequence[int(pointer[cache][f])]
                            index_remove = f_idx
                    
                    MIN_cache[cache].pop(index_remove) # pop the file furthest
                    MIN_cache[cache].append(file)


        #calculate download rate
       
        download = 0
        for cache_index in range(J):
            for file in MIN_cache[cache_index]:
                
                if file not in prev_cache[cache_index]:
                    download = download + 1

        prev_cache = copy.deepcopy(MIN_cache)
        download_rate.append(download)
        
    return hit_rate, download_rate