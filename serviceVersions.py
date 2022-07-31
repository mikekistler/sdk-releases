#!/usr/bin/env python3

# Create a csv file of the number of new api-versions across all Azure services by quarter,
# split between management plane and data plane.

# General approach:
# - Check out azure-rest-api-specs at the end of each quarter starting at 1Q 2017 to the present
# - Collect GA and preview "service versions", which are
#   - GA services: a folder under “stable”
#   - Preview services: a folder under “preview”
# - "new" service versions for the quarter are service versions not present in the last quarter
# - When counting new service versions in a quarter, dedup multiple versions of a specific service

from datetime import datetime
import glob
import os
import sys

# Toggle print of new service versions with command line argument
print_list = any(x in sys.argv for x in ['--list', '-l'])

# get todays date in the format YYYY-MM-DD
today = datetime.today().strftime('%Y-%m-%d')
quarters = [v for v in [f'{y}-{q}' for y in range(2017, 2023) for q in ['03-31', '06-30', '09-30', '12-31']] if v < today]

def count_new(this_quarter, last_quarter):
    qservices = [x for x in this_quarter if x not in last_quarter]
    # Use set comprehension to get the number of new services (ignore multiple versions in one quarter)
    return len ({'/'.join(x.split('/')[:-2]) for x in qservices})

# Pull in the latest version of the Azure API docs (NO shallow clone)
# os.system('rm -rf azure-rest-api-specs')
# os.system('git clone https://github.com/Azure/azure-rest-api-specs.git')
os.chdir('azure-rest-api-specs')

# last_quarter_services is all service versions released before the end of the last quarter
last_quarter_services = None
print('Quarter, MgmtPlaneGA, MgmtPlanePreview, DataPlaneGA, DataPlanePreview') if not print_list else None
for quarter in quarters:
    os.system(f'git checkout `git rev-list -n 1 --before="{quarter} 23:59" main`')
    this_quarter_services = {'resource-manager': {}, 'data-plane': {}}
    for plane in ['resource-manager', 'data-plane']:
        for type in ['stable', 'preview']:
            this_quarter_services[plane][type] = glob.glob(f'specification/*/{plane}/**/{type}/*', recursive=True)
    if last_quarter_services:
        counts = [count_new(this_quarter_services[plane][type], last_quarter_services[plane][type]) for plane in ['resource-manager', 'data-plane'] for type in ['stable', 'preview']]
        print(quarter, *counts, sep=',') if not print_list else None
    # Print new service versions by plane and type
    if print_list:
        for plane in ['resource-manager', 'data-plane']:
            for type in ['stable', 'preview']:
                new_services = [x for x in this_quarter_services[plane][type] if x not in last_quarter_services[plane][type]]
                print(f'\n {quarter} {plane} {type}\n\t' + '\n\t'.join(sorted(new_services))) if new_services else None
    last_quarter_services = this_quarter_services
