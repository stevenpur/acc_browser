#%% import modules
import utils
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import pandas as pd
import pickle

# %% read arguments
file = '/users/doherty/imh310/eating_detect/data/acc_data/P022_eating.pkl'
label_column = 'label'
time_column = 'time'
time_window = 60
target_labels = ['sedantry eating', 'mixed']
output_dir = '/users/doherty/imh310/acc_browser/github/'

data = pd.DataFrame()
if file.endswith('.pkl'):
    data = pd.read_pickle(file)# check file type
elif file.endswith('.csv'):
    data = pd.read_csv(file)
elif file.endswith('.txt') or file.endswith('.tsv'):
    data = pd.read_csv(file, sep='\t')
if label_column not in data.columns:
    raise ValueError(f'{label_column} not in the data columns')

data_gp = data.groupby(label_column)

X, Y, T = utils.make_windows(data, winsec=time_window, y_column=label_column)

# group X, Y, T into different labels
labels = data[label_column].unique()
gp = {label: {} for label in labels}
for label in labels:
    index = [i for i in range(len(Y)) if Y[i] == label]
    gp[label]['X'] = [X[i] for i in index]
    gp[label]['Y'] = [Y[i] for i in index]
    gp[label]['T'] = [T[i] for i in index]


# plot the target labels
plt.figure()
index = 10 
label = 'sedantry eating'
x = [ entry[0] for entry in gp[label]['X'][index] ]
y = [ entry[1] for entry in gp[label]['X'][index] ]
z = [ entry[2] for entry in gp[label]['X'][index] ]
plt.plot(x)
plt.plot(y)
plt.plot(z)
plt.title(f'{label} labels')
plt.xlabel('Time')
plt.ylabel('Label')
plt.savefig(output_dir + 'labels.png')
plt.close()

