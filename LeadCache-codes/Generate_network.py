import numpy as np
import random
def generate_network_graph(n, m, d): 
#where n is the number of users and m is the number of caches
	
	Graph = np.zeros((n,m))

	for user in range(n):
		adj_vertices = random.sample(range(m), d)
		Graph[user][adj_vertices] = 1

	return Graph


# In[ ]:




