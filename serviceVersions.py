#!/usr/bin/env python3

# Create a csv file of the number of new api-versions across all Azure services by quarter,
# split between management plane and data plane.

from datetime import datetime
import glob
import os

# get todays date in the format YYYY-MM-DD
today = datetime.today().strftime('%Y-%m-%d')
quarters = [v for v in [f'{y}-{q}' for y in range(2017, 2023) for q in ['03-31', '06-30', '09-30', '12-31']] if v < today]

def count_new(last_quarter, this_quarter):
    return len ([x for x in this_quarter if x not in last_quarter])

# Pull in the latest version of the Azure API docs (NO shallow clone)
# os.system('rm -rf azure-rest-api-specs')
# os.system('git clone https://github.com/Azure/azure-rest-api-specs.git')
os.chdir('azure-rest-api-specs')

last_quarter_services = None
print('Quarter, MgmtPlaneGA, MgmtPlanePreview, DataPlaneGA, DataPlanePreview')
for quarter in quarters:
    os.system(f'git checkout `git rev-list -n 1 --before="{quarter} 23:59" main`')
    this_quarter_services = {'resource-manager': {}, 'data-plane': {}}
    for plane in ['resource-manager', 'data-plane']:
        for type in ['stable', 'preview']:
            this_quarter_services[plane][type] = glob.glob(f'specification/*/{plane}/**/{type}/*', recursive=True)
    if last_quarter_services:
        counts = [count_new(last_quarter_services[plane][type], this_quarter_services[plane][type]) for plane in ['resource-manager', 'data-plane'] for type in ['stable', 'preview']]
        print(quarter, *counts, sep=',') if any(counts) else None
    last_quarter_services = this_quarter_services
