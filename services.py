#!/usr/bin/env python3

# Create a csv file of the Azure services with public REST API docs by quarter,
# split between management plane and data plane.

import glob
import os

# Pull in the latest version of the Azure API docs (NO shallow clone)
os.system('rm -rf azure-rest-api-specs')
os.system('git clone https://github.com/Azure/azure-rest-api-specs.git')
os.chdir('azure-rest-api-specs')

qvals = ['03-31', '06-30', '09-30', '12-31']

print('Quarter, Management Plane, Data Plane')
for year in range(2017, 2023):
    for quarter in range(0, 4):
        os.system(f'git checkout `git rev-list -n 1 --before="{year}-{qvals[quarter]} 23:59" main`')
        key = f'{year}-Q{quarter+1}'
        data_plane = len(glob.glob(f'specification/*/data-plane/**/readme.md', recursive=True))
        mgmt_plane = len(glob.glob(f'specification/*/resource-manager/**/readme.md', recursive=True))
        if data_plane or mgmt_plane:
            print(f'{key}, {mgmt_plane}, {data_plane}')

