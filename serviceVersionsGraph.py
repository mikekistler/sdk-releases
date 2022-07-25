#!/usr/bin/env python3

# Disable cspell-checking for this file
# pylint: disable=cspell-checker

import csv
import itertools
import matplotlib.pyplot as plt
# import os
# import re

# Cannot use numpy genfromtxt as it does not handle commas within quotes
def loadcsv(filename):
    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile)
        return [row for row in csvreader]

qvals = ['03-31', '06-30', '09-30', '12-31']

# Convert yyyy-mm-dd to nQyy
def qlabel(date):
    month = int(date[5:7]) - 1 # 0 based
    quarter = int(month/3) + 1
    year = date[2:4]
    return f'{quarter}Q{year}'

services = loadcsv('serviceVersions.csv')
quarters = [x[0] for x in services[1:]]

# Help on matplotlib
# https://matplotlib.org/stable/gallery/index.html

def moving_average(data, window_size):
    ma = (window_size - 1) * [None]
    ma += [sum(data[i:i+window_size])/float(window_size) for i in range(len(data)-window_size+1)]
    return ma

# Data plane services
fig = plt.figure(figsize=(12.5, 5.5))
plt.title('Data Plane Service Versions')
# plot preview services as dashed line
plt.plot(quarters, [None]+[int(x[3])+int(x[4]) for x in services[2:]], linestyle='--')
plt.plot(quarters, [None]+[int(x[3]) for x in services[2:]])
plt.plot(quarters, [None]+moving_average([int(x[3])+int(x[4]) for x in services[2:]], 4))

plt.legend(['services - preview', 'services - ga', 'ga+preview - 4 quarter moving avg'])
# Make the labels compact
qlabels = [qlabel(x) for x in quarters]
plt.xticks(quarters, qlabels)
plt.tight_layout()
#plt.show()
fig.savefig('dataplane-versions.png')

# Management plane services
fig = plt.figure(figsize=(12.5, 5.5))
plt.title('Management Plane Service Versions')
# plot preview services as dashed line
plt.plot(quarters, [None]+[int(x[1])+int(x[2]) for x in services[2:]], linestyle='--')
plt.plot(quarters, [None]+[int(x[1]) for x in services[2:]])

plt.legend(['services - preview', 'services - ga'])
# Make the labels compact
qlabels = [qlabel(x) for x in quarters]
plt.xticks(quarters, qlabels)
plt.tight_layout()
#plt.show()
fig.savefig('mgmtplane-versions.png')
