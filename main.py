import requests
from datetime import datetime, timedelta, timezone
from math import log10
import isodate

from config import API_KEY

API_KEY = "YOUR_API"
key = API_KEY

MIN_DURATION = 300


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

def search_by_keyword(keyword, max_results=50):
    # call youtube api to get videos by keyword
    videos = {}
    
    # set the maximum age to 59 days
    published_after = (
        datetime.now(timezone.utc)
        - timedelta(days=59)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")


    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": max_results,
        "publishedAfter": published_after,
        "key": API_KEY
    }


    print("Searching...")
    print("published_after:", published_after)
    print("params:", params)


    # get search results
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params=params
    )

    if r.status_code == 200:
        data = r.json()
        for item in data["items"]:
            video_id = item["id"]["videoId"]
            # dict of dicts (search videos (dicts) by video id (key))
            videos[video_id] = {
                "channel_id": item["snippet"]["channelId"],
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "views": None,
                "duration": None,
                "published": None,
                "subscribers": None
            }

    # get video details 
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "part": "statistics,snippet,contentDetails",
            "id": ",".join(videos.keys()),
            "key": API_KEY
        }
    )

    if r.status_code == 200:
        data = r.json()
        for item in data["items"]:
            # dict assignment by video id (item["id"])
            videos[item["id"]]["views"] = int(item["statistics"]["viewCount"])
            videos[item["id"]]["published"] = item["snippet"]["publishedAt"]
            videos[item["id"]]["duration"] = item["contentDetails"]["duration"]

    channel_ids = list({
        video["channel_id"] for video in videos.values()
    })
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={
            "part": "statistics",
            "id": ",".join(channel_ids),
            "key": API_KEY
        }
    )
    
    if r.status_code == 200:
        data = r.json()
        for item in data["items"]:
            channel_id = item["id"]
            subscribers = int(item["statistics"].get("subscriberCount", 1))
            for video in videos.values(): # individual video in videos dict
                if video["channel_id"] == channel_id:
                    video["subscribers"] = max(subscribers, 1)

    # filter out shorts
    videos = { 
        video_id:video 
        for video_id, video in videos.items() 
        if isodate.parse_duration(video["duration"]).total_seconds() >= MIN_DURATION
    }
    print(f"Longs found: {len(videos)}")

    # momentum
    get_momentum(videos)

    return videos

def get_top_videos(sorted_videos, n=10):
    return sorted_videos[:n]


def main():
    keyword = input("Enter a keyword to search for videos: ")
    videos = search_by_keyword(keyword)
    sorted_videos = sorted(
        videos.values(),
        key=lambda v: v["momentum"],
        reverse=True
    )
    top_videos = get_top_videos(sorted_videos, n=10)

    for i, video in enumerate(top_videos, start=1):
        print(f"{i}. {video['title']}")
        print(f"   Momentum:      {video['momentum']:.4f}")
        print(f"   Views:         {video['views']:,}")
        print(f"   Duration:      {video['duration']}")
        print(f"   Subscribers:  {video['subscribers']:,}")
        print(f"   Age (days):    {video['age_days']}")
        print(f"   Burst:         {video['burst']:.4f}")
        print(f"   Overperform:   {video['overperform']:.4f}")
        print(f"   URL:           {video['url']}")
        print()


if __name__ == "__main__":
    main()