#!/usr/bin/python3

import json
import gzip
import os
import re
import sys
from urllib.request import urlopen

# Latest nightly nightly.json file from the taskcluster index
NIGHTLY_JSON_URL = "https://firefox-ci-tc.services.mozilla.com/api/index/v1/task/project.application-services.v2.nightly.latest/artifacts/public%2Fbuild%2Fnightly.json"

VERSION_RE = re.compile(r'val VERSION = "[\d\.]+"')
CHANNEL_RE = re.compile(r'val CHANNEL = ApplicationServicesChannel.[A-Z_]+')

def main():
    with open(kt_module_path(), "r+t") as f:
        f.seek(0)
        current_source = f.read()
        new_source = make_replacements(current_source)
        f.seek(0)
        f.write(new_source)

def kt_module_path():
    root_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(root_dir, "plugins/dependencies/src/main/java/ApplicationServices.kt")

def make_replacements(source):
    if VERSION_RE.search(source) is None:
        print("Couldn't find VERSION initialization line")
        sys.exit(1)
    if CHANNEL_RE.search(source) is None:
        print("Couldn't find CHANNEL initialization line")
        sys.exit(1)
    nightly_config = fetch_nightly_config()
    version = nightly_config['version']
    if nightly_config['channel'] == 'maven-release':
        channel = "RELEASE"
    elif nightly_config['channel'] == 'maven-staging':
        channel = "STAGING"
    elif nightly_config['channel'] == 'maven-nightly-production':
        channel = "NIGHTLY"
    elif nightly_config['channel'] == 'maven-nightly-staging':
        channel = "NIGHTLY_STAGING"
    else:
        print("Unknown `channel` value: {}".format(nightly_config['channel']))
        sys.exit(1)

    source = VERSION_RE.sub(f'val VERSION = "{version}"', source)
    source = CHANNEL_RE.sub(f'val CHANNEL = ApplicationServicesChannel.{channel}', source)
    return source

def fetch_nightly_config():
    response = urlopen(NIGHTLY_JSON_URL)
    return json.loads(gzip.decompress(response.read()))

if __name__ == '__main__':
    main()
