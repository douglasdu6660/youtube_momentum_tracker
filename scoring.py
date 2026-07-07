from datetime import datetime, timezone
from math import log10

def get_age_days(start_time):
    start_time_dt = datetime.strptime(
        start_time,
        "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)

    return max((datetime.now(timezone.utc) - start_time_dt).days, 1)

def get_momentum(videos, w1=0.5, w2=0.5):
    for video in videos.values():
        age_by_days = (get_age_days(video["published"]))
        burst = log10(video["views"] / (1 + log10(age_by_days)))
        overperform = video["views"] / (video["subscribers"] or 1)
        video["age_days"] = age_by_days
        video["burst"] = burst
        video["overperform"] = overperform
        video["momentum"] = w1*burst + w2*overperform