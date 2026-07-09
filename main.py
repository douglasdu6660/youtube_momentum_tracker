import reverse_search
import scoring
import youtube_api
import transcript_scraping

def get_top_videos(sorted_videos, n=10):
    return sorted_videos[:n]

def main():
    mode = input("Enter '1' to search by keyword or '2' to search by video URL: ")
    if mode == "1":
        keyword = input("Enter a keyword to search for videos: ")
        videos = youtube_api.search_by_keyword(keyword)
    elif mode == "2":
        url = input("Enter a YouTube video URL: ")
        video_id = reverse_search.parse_url(url)
        if not video_id:
            print("Invalid YouTube URL")
            return
        videos = youtube_api.search_by_id(video_id)
        transcript_scraping.try_transcript(video_id)
    else:
        print("Invalid mode")
        return

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