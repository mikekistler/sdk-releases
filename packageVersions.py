#!/usr/bin/env python3

import csv
import json
import matplotlib.pyplot as plt
import re

# Cannot use numpy genfromtxt as it does not handle commas within quotes
def loadcsv(filename):
    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile)
        return [row for row in csvreader]

qvals = ['03-31', '06-30', '09-30', '12-31']

# Convert yyyy-mm[-dd] to yyyy-mm-dd of quarter
def quarter_from_date(date):
    if re.match('\d{4}-\d\d(-\d\d)?$', date):
        month = int(date[5:7]) - 1 # 0 based
        quarter = int(month/3)
        year = date[:4]
        return f'{year}-{qvals[quarter]}'
    return None

# Convert yyyy-mm-dd to nQyy
def qlabel(date):
    month = int(date[5:7]) - 1 # 0 based
    quarter = int(month/3) + 1
    year = date[2:4]
    return f'{quarter}Q{year}'

# Return True if the package is a mgmt plane package
# Need to pass in the language to use the right convention
# - DotNet mgmt plane package names start with "Azure.ResourceManager."
# - Go: mgmt plane package names start with "sdk/resourcemanager
# - Java: mgmt plane package names start with "azure-resourcemanager-"
# - JavaScript: mgmt plane package names start with "@azure/arm-"
# - Python: mgmt plane package names start with 'azure-mgmt-'
def mgmtplane_pkg(lang, name):
    if lang == 'dotnet':
        return name.startswith('Azure.ResourceManager.')
    elif lang == 'go':
        return name.startswith('sdk/resourcemanager')
    elif lang == 'java':
        return name.startswith('azure-resourcemanager-')
    elif lang == 'js':
        return name.startswith('@azure/arm-')
    elif lang == 'python':
        return name.startswith('azure-mgmt-')
    else:
        return False

# Return True if the version is GA or Beta (not Patch)
def version_is_ga_or_beta(version: str):
    return re.match('^[0-9]+\.[0-9]+\.0(-.*)?$', version)

serviceVersions = loadcsv('serviceVersions.csv')

# Drop initial quarters with zero service versions
first_qtr = next((i for i in range(1,len(serviceVersions)) if any(v != '0' for v in serviceVersions[i][1:])))
serviceVersions[1:] = serviceVersions[first_qtr:]

quarters = [x[0] for x in serviceVersions[1:]]
langs = ['dotnet', 'java', 'js', 'python', 'go']

# Get releases from github repos

dataplane_packages = {lang:{key: set() for key in quarters} for lang in langs}
mgmtplane_packages = {lang:{key: set() for key in quarters} for lang in langs}

for lang in langs:
    with open(f'{lang}_tags.json', 'r') as f:
        lang_tags = json.load(f)
    sep = '/v' if lang == 'go' else '_'
    filtered_tags = [x for x in lang_tags if x['name'].count(sep) == 1]
    if lang == 'dotnet':
        filtered_tags = [x for x in filtered_tags if x['name'].startswith('Azure.')]
    # if lang == 'java':
    #     # Exclude Java Spring packages
    #     filtered_tags = [x for x in filtered_tags if x['name'].startswith('azure-')]
    for tag in filtered_tags:
        try:
            if 'committedDate' in tag['target']:
                tag_date = tag['target']['committedDate'][:10]
            else:
                tag_date = tag['target']['target']['committedDate'][:10]
        except KeyError as ex:
            print(f'{lang} {tag["name"]} has no committedDate')
            continue
        quarter = quarter_from_date(tag_date)
        package, version = tag['name'].split(sep, 1)
        if quarter in quarters and version_is_ga_or_beta(version):
            if mgmtplane_pkg(lang, package):
                mgmtplane_packages[lang][quarter].add(package)
            else:
                dataplane_packages[lang][quarter].add(package)

# print('\n'.join(sorted(dataplane_packages['java']['2022-06-30'])))

# Help on matplotlib
# https://matplotlib.org/stable/gallery/index.html

# Data plane services
fig = plt.figure(figsize=(12.5, 5.5))
plt.title('Data Plane Service Versions')
# plot ga + preview services as dashed line
plt.plot(quarters, [None]+[int(x[3])+int(x[4]) for x in serviceVersions[2:]], linestyle='--')

# Now plot the packages
for lang in langs:
    counts = [len(v) for (k,v) in dataplane_packages[lang].items()]
    plt.plot(quarters, [x if x>0 else None for x in counts])

plt.legend(['services - ga + preview'] + [f'{x} - stable+beta' for x in langs], loc='upper left')
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
plt.plot(quarters, [None]+[int(x[1])+int(x[2]) for x in serviceVersions[2:]], linestyle='--')

# Now plot the packages
for lang in langs:
    counts = [len(v) for (k,v) in mgmtplane_packages[lang].items()]
    plt.plot(quarters, [x if x>0 else None for x in counts])

plt.legend(['services - ga + preview'] + [f'{x} - stable+beta' for x in langs], loc='upper left')
# Make the labels compact
qlabels = [qlabel(x) for x in quarters]
plt.xticks(quarters, qlabels)
plt.tight_layout()
#plt.show()
fig.savefig('mgmtplane-versions.png')
