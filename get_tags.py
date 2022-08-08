#!/usr/bin/env python3

import json
import os
import requests

token = os.environ.get('GITHUB_TOKEN')
auth_header = {'Authorization': 'bearer ' + token} if token else None

url = 'https://api.github.com/graphql'

# https://docs.github.com/en/graphql/overview/explorer is a good tool for debugging these graph queries

def get_tag_query(repo, after):
    return '''{
      repository(owner: "Azure", name: "%s") {
        refs(refPrefix: "refs/tags/", after: %s, first: 100, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {
          nodes {
            target {
              ... on Commit {
                committedDate
              }
              ... on Tag {
                target {
                  ... on Commit {
                    committedDate
                  }
                }
              }
            }
            name
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    ''' % (repo, after)

def get_tags(repo):
    query = get_tag_query(repo, '""')
    r = requests.post(url, headers = auth_header, json = { 'query': query })
    tags = r.json()['data']['repository']['refs']['nodes']
    while(r.json()['data']['repository']['refs']['pageInfo']['hasNextPage']):
        after = r.json()['data']['repository']['refs']['pageInfo']['endCursor']
        query = get_tag_query(repo, f'"{after}"')
        r = requests.post(url, headers = auth_header, json = { 'query': query })
        tags.extend(r.json()['data']['repository']['refs']['nodes'])
    return tags

langs = ['dotnet', 'java', 'js', 'python', 'go', 'cpp']

for lang in langs:
    repo = f'azure-sdk-for-{lang}' if lang != 'dotnet' else 'azure-sdk-for-net'
    tags = get_tags(repo)
    with open(f'{lang}_tags.json', 'w') as fp:
        json.dump(tags, fp)
