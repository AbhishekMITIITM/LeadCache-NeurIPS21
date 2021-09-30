import pandas as pd
import numpy as np
from Lead_cache import Lead_cache
import math
from Generate_network import generate_network_graph
from LRU import Bipartite_LRU
from LFU import Bipartite_LFU
from offline_opt import MIN 
import random
import copy
import csv

users = 1
time_limit = 500
caches = 1
alpha = 0.1
d = 1
# Dropping all file requests with id larger than the threshold to reduce the library size
threshold = 250
NumSeq = 15  # denotes the number of non-overlapping sequences over which the experminent is run
print("Users=", users, "caches=", caches, "Library_Size=", threshold, "time=", time_limit, "NumSeq=", NumSeq, file=open("parameters.log","w"))

Adj = generate_network_graph(users, caches, d)
# generates a random network

# Setting up the arrays to store hits and downloads over multiple runs
LFU_Hits = []
LRU_Hits = []
LeadCache_Hits = []
LFU_Downloads = []
LRU_Downloads = []
LeadCache_Downloads = []
OPT_Hits=[]
OPT_Downloads = []

# Generating the request sequence
#df=pd.read_csv('ratings.csv', sep=',',header=None)
#data = pd.read_csv("CMU_dataset.csv")
data = pd.read_csv("CMU_gigantic.txt", sep = ' ')
data.columns = ['Req_ID', 'File_ID', 'File_Size']
DataLength = len(data)
# splitting up the entire time axis into non-overlapping parts
for i in range(NumSeq):
    df = pd.DataFrame(data[int(i*DataLength/NumSeq) : int((i+1)*DataLength/NumSeq)])

    #df= pd.DataFrame(data)

    # The Data is already sorted according to the Req_ID, so no need to sort it again
    # Renaming the annoynimized FileID's
    old_id = df.File_ID.unique()
    old_id.sort()
    new_id = dict(zip(old_id, range(len(old_id))))
    df = df.replace({"File_ID": new_id})

    # Reducing the library size

    df = df[df.File_ID < threshold]
    df = df.reset_index(drop=True)

    library_size = df['File_ID'].max()+2
    C = math.floor(alpha*library_size)
    v = df['File_ID']
    RawSeq = np.array(v)
    time = int(np.floor(min(time_limit, len(v)/users)))-1

    # RawSeq contains an array of requests
    df = np.array_split(RawSeq, users)

    # Running the algorithms

    hit_rates_OPT, download_rate_OPT = MIN(df, Adj, time, library_size, C)
    hit_rates_OPT = pd.DataFrame(hit_rates_OPT)
    download_rate_OPT = pd.DataFrame(download_rate_OPT)

    OPT_Hits.append(np.sum(hit_rates_OPT)/(time*users))
    OPT_Downloads.append(np.sum(download_rate_OPT)/(time*caches))

    hit_rates_LFU, download_rate_LFU = Bipartite_LFU(
        df, Adj, time, library_size, C)
    hit_rates_LFU = pd.DataFrame(hit_rates_LFU)
    download_rate_LFU = pd.DataFrame(download_rate_LFU)

    LFU_Hits.append(np.sum(hit_rates_LFU)/(time*users))
    LFU_Downloads.append(np.sum(download_rate_LFU)/(time*caches))

    hit_rates_LRU, download_rate_LRU = Bipartite_LRU(
        df, Adj, time, library_size, C)
    hit_rates_LRU = pd.DataFrame(hit_rates_LRU)
    download_rate_LRU = pd.DataFrame(download_rate_LRU)

    LRU_Hits.append(np.sum(hit_rates_LRU)/(time*users))
    LRU_Downloads.append(np.sum(download_rate_LRU)/(time*caches))

    hit_rates_Lead_cache, download_rate_Lead_cache = Lead_cache(
        df, Adj, time, library_size, C, d)
    hit_rates_Lead_cache = pd.DataFrame(hit_rates_Lead_cache)
    download_rate_Lead_cache = pd.DataFrame(download_rate_Lead_cache)

    LeadCache_Hits.append(np.sum(hit_rates_Lead_cache)/(time*users))
    LeadCache_Downloads.append(np.sum(download_rate_Lead_cache)/(time*caches))

    #Outputting the result to stdout
    #print("LFU Hits=", LFU_Hits, "LRU Hits=", LRU_Hits, "LeadCache Hits=", LeadCache_Hits, "OPT_Hits=", OPT_Hits)
    #print("LFU Downloads=", LFU_Downloads, "LRU Downloads=", LRU_Downloads, "LeadCache Hits=", LeadCache_Downloads, "OPT_Downloads=", OPT_Downloads)


# Saving the output files

pd.DataFrame(LFU_Hits).to_csv('LFU_Hits.csv',index=False)
pd.DataFrame(LFU_Downloads).to_csv('LFU_Downloads.csv',index=False)
pd.DataFrame(LRU_Hits).to_csv('LRU_Hits.csv',index=False)
pd.DataFrame(LRU_Downloads).to_csv('LRU_Downloads.csv',index=False)
pd.DataFrame(LeadCache_Hits).to_csv('LeadCache_Hits.csv',index=False)
pd.DataFrame(LeadCache_Downloads).to_csv('LeadCache_Downloads.csv',index=False) 
pd.DataFrame(OPT_Hits).to_csv('OPT_Hits.csv',index=False)
pd.DataFrame(OPT_Downloads).to_csv('OPT_Downloads.csv',index=False)
    


