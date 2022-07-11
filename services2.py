#!/usr/bin/env python3

# Create a csv file of the Azure services with public REST API docs by quarter,
# split between management plane and data plane.

from datetime import datetime
import glob
import os
import subprocess
import re

def sh(command):
    p = subprocess.run(command, shell=True, capture_output=True)
    return p.stdout.decode().strip()

def file_in_main(file, quarter):
    return sh(f'git rev-list -n 1 --before="{quarter} 23:59" main -- {file}')

def yearago(quarter):
    m = re.match('^(\d{4})(-\d\d-\d\d)$', quarter)
    return f'{int(m.group(1)) - 1}-{m.group(2)}'

# get todays date in the format YYYY-MM-DD
today = datetime.today().strftime('%Y-%m-%d')
quarters = [v for v in [f'{y}-{q}' for y in range(2017, 2023) for q in ['03-31', '06-30', '09-30', '12-31']] if v < today]

# Count the number of services that have a "GA" REST API definition.
# A service counts if either of the following is true:
# 1. It has a "stable" folder
# 2. The _oldest_ preview REST API definition is more than 12 months old (determined by when 'readme.md' merged to main)
def get_ga_services(plane, quarter):
    """
    plane = 'data-plane' or 'resource-manager'
    quarter = current quarter
    """
    ga_services = len(glob.glob(f'specification/*/{plane}/**/stable', recursive=True))
    preview_services = 0
    previews = glob.glob(f'specification/*/{plane}/**/preview', recursive=True)
    for preview in previews:
        dirname = os.path.dirname(preview)
        if not os.path.exists(os.path.join(dirname, 'stable')):
            # The readme.md might be a sibling of the preview folder or a sibling of the parent of the preview folder
            # Get the readme.md that is a sibling of the preview folder
            readme = os.path.join(dirname, 'readme.md')
            if not os.path.exists(readme):
                readme = os.path.join(os.path.dirname(dirname), 'readme.md')
            if os.path.exists(readme) and file_in_main(readme, yearago(quarter)):
                #print(f'{preview} counts as GA')
                ga_services += 1
            else:
                #print(f'{preview} does not count as GA')
                preview_services += 1
    return (ga_services, preview_services)

# Pull in the latest version of the Azure API docs (NO shallow clone)
# os.system('rm -rf azure-rest-api-specs')
# os.system('git clone https://github.com/Azure/azure-rest-api-specs.git')
os.chdir('azure-rest-api-specs')

print('Quarter, MgmtPlaneGA, MgmtPlanePreview, DataPlaneGA, DataPlanePreview')
for quarter in quarters:
    os.system(f'git checkout `git rev-list -n 1 --before="{quarter} 23:59" main`')
    data_plane = get_ga_services('data-plane', quarter)
    mgmt_plane = get_ga_services('resource-manager', quarter)
    if any(data_plane) or any(mgmt_plane):
        print(quarter, *mgmt_plane, *data_plane, sep=',')
