#!/usr/bin/env python3

# Disable cspell-checking for this file
# pylint: disable=cspell-checker

import csv
import itertools
import matplotlib.pyplot as plt
import os
import re

# Cannot use numpy genfromtxt as it does not handle commas within quotes
def loadcsv(filename):
    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile)
        return [row for row in csvreader]

qvals = ['03-31', '06-30', '09-30', '12-31']

# Convert mm/dd/yyyy to yyyy-mm-dd of quarter
def quarter_from_date(date):
    if re.match('\d\d/\d\d/\d{4}$', date):
        month = int(date[:2]) - 1 # 0 based
        quarter = int(month/3)
        year = date[6:]
        return f'{year}-{qvals[quarter]}'
    return None

# Convert yyyy-mm-dd to nQyy
def qlabel(date):
    month = int(date[5:7]) - 1 # 0 based
    quarter = int(month/3) + 1
    year = date[2:4]
    return f'{quarter}Q{year}'

services = loadcsv('services2.csv')
quarters = [x[0] for x in services[1:]]

langs = ['dotnet', 'java', 'js', 'python', 'go', 'cpp']

# Pull in the latest version of the Azure SDK repo
os.system('rm -rf azure-sdk')
os.system('git clone https://github.com/Azure/azure-sdk.git')
os.chdir('azure-sdk/_data/releases/latest')

dataplane_packages = {lang:{key: set() for key in quarters} for lang in langs}
mgmtplane_packages = {lang:{key: set() for key in quarters} for lang in langs}

for lang in langs:
    lang_packages = loadcsv(f'{lang}-packages.csv')
    # Get index of the columns we need
    display_name = lang_packages[0].index('DisplayName')
    type = lang_packages[0].index('Type')
    first_ga_date = lang_packages[0].index('FirstGADate')
    for row in lang_packages[1:]:
        quarter = quarter_from_date(row[first_ga_date])
        if quarter in quarters:
            if row[type] == 'client':
                dataplane_packages[lang][quarter].add(row[display_name])
            elif row[type] == 'mgmt':
                mgmtplane_packages[lang][quarter].add(row[display_name])
        elif quarter is None and row[first_ga_date]:
            print(f'{lang} {row[0]} Invalid FirstGaDate: {row[first_ga_date]}')

os.chdir('../../../..')

# Help on matplotlib
# https://matplotlib.org/stable/gallery/index.html

# Data plane services
fig = plt.figure(figsize=(12.5, 5.5))
plt.title('Data Plane Services and Track2 Packages')
# plot preview services as dashed line
plt.plot(quarters, [int(x[3])+int(x[4]) for x in services[1:]], linestyle='--')
plt.plot(quarters, [int(x[3]) for x in services[1:]])

# Now plot the packages
for lang in langs:
    counts = [len(v) for (k,v) in dataplane_packages[lang].items()]
    plt.plot(quarters, [x if x>0 else None for x in itertools.accumulate(counts)])

plt.legend(['services - preview', 'services - ga'] + langs)
# Make the labels compact
qlabels = [qlabel(x) for x in quarters]
plt.xticks(quarters, qlabels)
plt.tight_layout()
#plt.show()
fig.savefig('dataplane.png')

# Management plane services
fig = plt.figure(figsize=(12.5, 5.5))
plt.title('Management Plane Services and Track2 Packages')
# plot preview services as dashed line
plt.plot(quarters, [int(x[1])+int(x[2]) for x in services[1:]], linestyle='--')
plt.plot(quarters, [int(x[1]) for x in services[1:]])

# Now plot the packages
for lang in langs:
    counts = [len(v) for (k,v) in mgmtplane_packages[lang].items()]
    plt.plot(quarters, [x if x>0 else None for x in itertools.accumulate(counts)])

plt.legend(['services - preview', 'services - ga'] + langs)

# Make the labels compact
qlabels = [qlabel(x) for x in quarters]
plt.xticks(quarters, qlabels)
plt.tight_layout()
#plt.show()
fig.savefig('mgmtplane.png')
