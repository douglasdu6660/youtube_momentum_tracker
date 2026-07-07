import re

def parse_url(url):
    # extract video id from url
    # find video id of 11 characters after v= or youtu.be
    match = re.search(r"(? : v= | youtu\.be/)([A-Za-z0-9_-]{11})" , url)

    if match:
        return match.group(1) # return captured group only after v= or youtu.be/
    
    return None