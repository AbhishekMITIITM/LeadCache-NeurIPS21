import pandas as pd
import numpy as np
from Lead_cache import Lead_cache
import math
from Generate_network import generate_network_graph
from LRU import Bipartite_LRU
from LFU import Bipartite_LFU
from Perturbed_LFU import Perturbed_Bipartite_LFU
from offline_opt import MIN 
import random
import copy
import csv
import argparse
 
 
# Initialize parser
parser = argparse.ArgumentParser()
# Adding optional argument
parser.add_argument("-users", "--users", help = "number of users in the network")
parser.add_argument("-time_limit", "--time_limit", help = "number of timesteps for the algorithm")
parser.add_argument("-caches", "--caches", help = "number of caches")
parser.add_argument("-degree", "--degree", help = "right degree of the network")
parser.add_argument("-libsize", "--library_size", help = "library size")
parser.add_argument("-alpha", "--alpha", help = "cache_size")
parser.add_argument("-numseq", "--numseq", help = "number of non overlapping sequences")
parser.add_argument("-dataset", "--dataset", help="movie_lens or CMU_gigantic")
# Read arguments from command line
args = parser.parse_args()


users = 7
time_limit = 100
caches = 5
alpha = 0.1
d = 3
# Dropping all file requests with id larger than the threshold to reduce the library size
threshold = 300
NumSeq = 10  # denotes the number of non-overlapping sequences over which the experminent is run

if(args.users):
    users = int(args.users)
if(args.time_limit):
    time_limit = int(args.time_limit)
if(args.caches):
    caches = int(args.caches)
if(args.time_limit):
    d = int(args.degree)
if(args.library_size):
    threshold = int(args.library_size)
if(args.alpha):
    alpha = int(args.alpha)
if(args.numseq):
    NumSeq = int(args.numseq)

print("Users=", users, "caches=", caches, "Library_Size=", threshold, "time=", time_limit, "NumSeq=", NumSeq, file=open("parameters.log","w"))

# generates a random network
Adj = generate_network_graph(users, caches, d)

# saves the network 
print(Adj, file=open("network_adjacency_matrix.log", "w"))

# Setting up the arrays to store hits and downloads over multiple runs
LFU_Hits = []
perturbed_LFU_Hits = []
perturbed_LFU_Downloads = []
LRU_Hits = []
LeadCache_Hits = []
LFU_Downloads = []
LRU_Downloads = []
LeadCache_Downloads = []
OPT_Hits=[]
OPT_Downloads = []
LeadCache_Hits_Madow = []
LeadCache_Downloads_Madow = []

# Generating the request sequence

if(args.dataset == "CMU_gigantic"):
    data = pd.read_csv("CMU_gigantic.txt", sep = ' ')
    data.columns = ['Timestamp', 'File_ID', 'File_Size']
else:
    data = pd.read_csv("ratings1m.dat", sep = '::')
    data.columns = ['User_ID', 'File_ID', 'Ratings', 'Timestamp']


DataLength = len(data)
# splitting up the entire time axis into non-overlapping parts
for i in range(NumSeq):
    df = pd.DataFrame(data[int(i*DataLength/NumSeq) : int((i+1)*DataLength/NumSeq)])
    df.sort_values("Timestamp")

    #df= pd.DataFrame(data)

    # The Data is already sorted according to the Req_ID, so no need to sort it again
    # Renaming the annoynimized FileID's
    old_id = df.File_ID.unique()
    old_id.sort()
    new_id = dict(zip(old_id, range(len(old_id))))
    df = df.replace({"File_ID": new_id})
    df.sort_values("Timestamp")

    # Reducing the library size

    df = df[df.File_ID < threshold]
    df = df.reset_index(drop=True)

    library_size = df['File_ID'].max()+2
    C = math.floor(alpha*library_size)
    v = df['File_ID']
    RawSeq = np.array(v)
    time = int(np.floor(min(time_limit, len(v)/users)))-1
    print(time)
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

    hit_rates_Perturbed_LFU, download_rate_Perturbed_LFU = Perturbed_Bipartite_LFU(
    	df, Adj, time, library_size, C, d)
    hit_rates_Perturbed_LFU = pd.DataFrame(hit_rates_Perturbed_LFU)
    download_rate_Perturbed_LFU = pd.DataFrame(download_rate_Perturbed_LFU)

    perturbed_LFU_Hits.append(np.sum(hit_rates_Perturbed_LFU)/(time*users))
    perturbed_LFU_Downloads.append(np.sum(download_rate_Perturbed_LFU)/(time*caches))



    #print("Running LeadCache")

    hit_rates_Lead_cache, download_rate_Lead_cache, hit_rates_Madow, download_rates_Madow = Lead_cache(
        df, Adj, time, library_size, C, d)
    hit_rates_Lead_cache = pd.DataFrame(hit_rates_Lead_cache)
    download_rate_Lead_cache = pd.DataFrame(download_rate_Lead_cache)

    LeadCache_Hits.append(np.sum(hit_rates_Lead_cache)/(time*users))
    LeadCache_Downloads.append(np.sum(download_rate_Lead_cache)/(time*caches))

    hit_rates_Madow = pd.DataFrame(hit_rates_Madow)
    download_rates_Madow = pd.DataFrame(download_rates_Madow)

    LeadCache_Hits_Madow.append(np.sum(hit_rates_Madow)/(time*users))
    LeadCache_Downloads_Madow.append(np.sum(download_rates_Madow)/(time*caches))


    # #Outputting the result to stdout
    #print("LFU Hits=", LFU_Hits, "LRU Hits=", LRU_Hits, "OPT_Hits=", OPT_Hits, "Perturbed_LFU_Hits=", perturbed_LFU_Hits)
    #print("LFU Downloads=", LFU_Downloads, "LRU Downloads=", LRU_Downloads, "OPT_Downloads=", OPT_Downloads, "Perturbed_LFU_Downloads=", perturbed_LFU_Downloads)


# Saving the output files

pd.DataFrame(LFU_Hits).to_csv('LFU_Hits.csv',index=False)
pd.DataFrame(LFU_Downloads).to_csv('LFU_Downloads.csv',index=False)
pd.DataFrame(LRU_Hits).to_csv('LRU_Hits.csv',index=False)
pd.DataFrame(LRU_Downloads).to_csv('LRU_Downloads.csv',index=False)
pd.DataFrame(perturbed_LFU_Hits).to_csv('Perturbed_LFU_Hits.csv',index=False)
pd.DataFrame(perturbed_LFU_Downloads).to_csv('Perturbed_LFU_Downloads.csv',index=False) 
pd.DataFrame(LeadCache_Hits).to_csv('LeadCache_Hits.csv',index=False)
pd.DataFrame(LeadCache_Downloads).to_csv('LeadCache_Downloads.csv',index=False) 
pd.DataFrame(LeadCache_Hits_Madow).to_csv('LeadCache_Hits_Madow.csv',index=False)
pd.DataFrame(LeadCache_Downloads_Madow).to_csv('LeadCache_Downloads_Madow.csv',index=False) 
pd.DataFrame(OPT_Hits).to_csv('OPT_Hits.csv',index=False)
pd.DataFrame(OPT_Downloads).to_csv('OPT_Downloads.csv',index=False)
    
# Saving the dynamic hit-rate and download logs

pd.DataFrame(hit_rates_OPT).to_csv('OPT_Hits_Seq.csv',index=False)
pd.DataFrame(download_rate_OPT).to_csv('OPT_Downloads_Seq.csv',index=False)
pd.DataFrame(hit_rates_LRU).to_csv('LRU_Hits_Seq.csv',index=False)
pd.DataFrame(download_rate_LRU).to_csv('LRU_Downloads_Seq.csv',index=False)
pd.DataFrame(hit_rates_LFU).to_csv('LFU_Hits_Seq.csv',index=False)
pd.DataFrame(download_rate_LFU).to_csv('LFU_Downloads_Seq.csv',index=False)
pd.DataFrame(hit_rates_Lead_cache).to_csv('LeadCache_Hits_Seq.csv',index=False)
pd.DataFrame(download_rate_Lead_cache).to_csv('LeadCache_Downloads_Seq.csv',index=False)
pd.DataFrame(perturbed_LFU_Hits).to_csv('perturbed_LFU_Hits_Seq.csv',index=False)
pd.DataFrame(perturbed_LFU_Downloads).to_csv('perturbed_LFU_Downloads_Seq.csv',index=False)



