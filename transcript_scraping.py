from youtube_transcript_api import YouTubeTranscriptApi
from keybert import KeyBERT

def get_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return transcript
    
    except Exception as e:
        print(f"Error fetching transcript for video ID {video_id}: {e}")
        return None
    
def get_frequent_words(transcript, n=20):
    if transcript:
        full_text = " ".join(
            snippet.text
            for snippet in transcript
        )
        
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(
            full_text,
            top_n=n
        )
        for word, score in keywords:
            print(word, score)

    else:
        print("No transcript available to process.")

def try_transcript(video_id):
    transcript = get_transcript(video_id)
    get_frequent_words(transcript)