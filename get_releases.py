
"""
Holy crap! https://datatracker.ietf.org/doc/html/rfc5988#section-5

gh docs: https://docs.github.com/en/rest/reference/repos#releases

curl -X GET https:/api.github.com/repos/azure/azure-sdk-for-js/releases



r = requests.get('https://api.github.com/repos/azure/azure-sdk-for-js/releases')
print(r.json())

js_releases[0].keys()

dict_keys(['url', 'assets_url', 'upload_url', 'html_url', 'id', 'author', 'node_id', 'tag_name',
 'target_commitish', 'name', 'draft', 'prerelease', 'created_at', 'published_at', 'assets',
 'tarball_url', 'zipball_url', 'body'])


 r.json() is an array of releases, each containing:
 - name, e.g. '@azure/mixed-reality-remote-rendering_1.0.0-beta.1'
 - tag_name, e.g. '@azure/mixed-reality-remote-rendering_1.0.0-beta.1'
 - created_at, e.g. '2021-09-21T18:45:26Z'
 - published_at, e.g. '2021-09-21T19:52:19Z'
 - prerelease, e.g. False
 - draft, e.g. False
 - body, e.g. ''## 1.0.0-beta.1 (2021-09-21)\n\n- Initial release.'

There is no 'version' -- I guess I have to parse this off the name or tagname.
'name' and 'tagname' appear to be the same in js sdk -- confirmed

>>> [x['name'] for x in not_samples if x['name'] != x['tag_name']]
[]

>>> not_draft = [x for x in not_samples if not x['draft']]
>>> len(not_draft)
775

Assumption that these come back in reverse order of created_at

Ah rate limiting:
>>> r
<Response [403]>
>>> r.text
'{"message":"API rate limit exceeded for 70.123.42.217. (But here\'s the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}\n'

No 'Retry-After' header. 

Well ... requests does not support bearer auth ... need to code auth header by hand.

https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

Create token with 'public_repo' scope AND authorize it for SSO.

https://docs.github.com/en/enterprise-cloud@latest/authentication/authenticating-with-saml-single-sign-on/authorizing-a-personal-access-token-for-use-with-saml-single-sign-on

"""

import json
import os
import re
import requests

token = os.environ.get('GITHUB_TOKEN')
auth_header = {'Authorization': 'bearer ' + token} if token else None

def get_releases(url):
    r = requests.get(url, headers = auth_header)
    releases = [x for x in r.json() if x['published_at']]
    while 'next' in r.links:
        r = requests.get(r.links['next']['url'], headers = auth_header)
        releases += [x for x in r.json() if not x['prerelease']]
    return releases

langs = ['dotnet', 'java', 'js', 'python', 'go', 'cpp']

for lang in langs:
    url = f'https://api.github.com/repos/azure/azure-sdk-for-{lang}/releases'
    if lang == 'dotnet':
        url = 'https://api.github.com/repos/Azure/azure-sdk-for-net/releases'
    lang_releases = get_releases(url)
    with open(f'{lang}_releases.json', 'w') as fp:
        json.dump(lang_releases, fp)

# js_releases = get_releases('https://api.github.com/repos/azure/azure-sdk-for-js/releases')

# len(js_releases) == 1134
# len([x for x in js_releases if not x['prerelease']]) == 545
# len([x['name'] for x in js_releases if 'samples' not in x['name']]) == 357
#
# Betas appear to be consistently marked as prerelease

not_samples = [x for x in js_releases if 'samples' not in x['name']]

[x['name'] for x in not_samples if x['name'].count('_') != 1]
# []
# So every release name has exactly one '_' -- good!

packages = {re.sub('_.*$', '', x['tag_name']) for x in not_samples}
# len(packages) == 43
# 10 of these are /azure-core packages

# Hmmm. There are 152 directories in 'sdk' in the js sdk repo.

# npm says there are 299 packages in @azure
# Some of these come from another repos, e.g. https://github.com/AzureAD/microsoft-authentication-library-for-js

# 395 packages in @aws-sdk
# 136 packages in @google-cloud
# 121 packages in @googleapis

# Does npm have an api?
# 

java_releases = get_releases('https://api.github.com/repos/azure/azure-sdk-for-java/releases')

with open('java_releases.json', 'w') as fp:
    json.dump(java_releases, fp)

# len(java_releases) == 1331

not_samples = [x for x in java_releases if 'samples' not in x['name']]

# len(no_samples) == 1309

[x['name'] for x in not_samples if x['name'].count('_') != 1]
# []
# So every release name has exactly one '_' -- good!

package = re.sub('_.*$', '', r.json()[6]['tag_name'])
version = re.sub('^.*_', '', r.json()[6]['tag_name'])

for x in not_samples:
    x['package'] = re.sub('_.*$', '', x['name'])
    x['version'] = re.sub('^.*_', '', x['name'])

majors = [x['version'].split('.')[0] for x in not_samples]

from collections import Counter
c = Counter(majors)

# Pie chart of majors
import matplotlib.pyplot as plt

fig1, ax1 = plt.subplots()
ax1.pie(c.values(), labels=c.keys(), autopct='%1.1f%%', startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title('JS Releases major version')

plt.show()
