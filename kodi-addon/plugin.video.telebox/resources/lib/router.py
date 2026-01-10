import sys
import urllib.parse

def get_params():
    if len(sys.argv) < 3:
        return {}
    return dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
