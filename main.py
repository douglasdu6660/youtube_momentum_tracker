import scoring
import youtube_api

def get_top_videos(sorted_videos, n=10):
    return sorted_videos[:n]

def main():
    keyword = input("Enter a keyword to search for videos: ")
    videos = youtube_api.search_by_keyword(keyword)
    # momentum
    scoring.get_momentum(videos)
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