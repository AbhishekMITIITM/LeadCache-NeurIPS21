import pandas as pd
import numpy as np
import copy
import csv
import seaborn as sns
import matplotlib.pyplot as plt



threshold = 3000
dist_threshold = threshold
data = pd.read_csv("sigmetrics_truncated_data.txt", sep = ' ')
#data = pd.read_csv("../../ICML2021/codes/FinalCode/CMU_gigantic.txt", sep = ' ')


data.columns = ['Req_ID', 'File_ID', 'File_Size']
DataLength = len(data)


df = pd.DataFrame(data)
old_id = df.File_ID.unique()
old_id.sort()
new_id = dict(zip(old_id, range(len(old_id))))
df = df.replace({"File_ID": new_id})

# Reducing the library size

df = df[df.File_ID < threshold]
df = df.reset_index(drop=True)

library_size = df['File_ID'].max()+2
v = df['File_ID']
RawSeq = np.array(v)

Dist = np.empty([1,1])


for i in range(dist_threshold):
	counter = 0
	for j in range(len(RawSeq)):
		if (i == RawSeq[j]):
			counter = counter + 1
	Dist = np.append(Dist, counter)
			
			

# Plotting the density function of the inter-request times

#sns.set_theme("paper")
sns.set_style("dark")
sns.color_palette("gist_heat")

ax = plt.plot(figsize=(10,6))
ax = sns.distplot(Dist, hist = False, kde_kws={"shade": True, "linewidth": 2})
#ax.legend()
plt.ylabel(" Normalized Frequency ")
plt.xlabel("Popularity ")
plt.xlim(1, 1000)
ax.tick_params(axis='both', which='major', labelsize=13)
#ax.axes.yaxis.set_ticks([])
ax.grid()
#plt.legend(loc = 'upper right', frameon= False, labelspacing=.8)
plt.savefig("Popularity-plot-MovieLens.pdf") 




