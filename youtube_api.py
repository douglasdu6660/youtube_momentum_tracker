import requests
import isodate
from datetime import timedelta, datetime, timezone

from config import API_KEY

MIN_DURATION = 300

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
    else:
        print(f"Error: {r.status_code} - {r.text}")
        return {}

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
    else:
        print(f"Error: {r.status_code} - {r.text}")
        return {}
    
    # set up channel query
    channel_ids = list({
        video["channel_id"] for video in videos.values()
    })
    # get channels
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={
            "part": "statistics",
            "id": ",".join(channel_ids),
            "key": API_KEY
        }
    )
    
    channel_subs = {}
    if r.status_code == 200:
        data = r.json()
        for item in data["items"]:
            channel_id = item["id"]
            channel_subs[channel_id] = int(item["statistics"].get("subscriberCount", 1))
        for video in videos.values(): # individual video in videos dict
            video["subscribers"] = channel_subs[video["channel_id"]] # assign subscriber count to video dict
    else:
        print(f"Error: {r.status_code} - {r.text}")
        return {}
    
    # filter out shorts
    videos = { 
        video_id:video 
        for video_id, video in videos.items() 
        if isodate.parse_duration(video["duration"]).total_seconds() >= MIN_DURATION
    }
    print(f"Longs found: {len(videos)}")

    return videos