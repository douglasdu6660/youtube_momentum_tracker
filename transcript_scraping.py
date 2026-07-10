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
    
def get_frequent_words(transcript, diversity=0, ngram=1, n=20):
    if transcript:
        # turn to string
        full_text = " ".join(
            snippet.get('text', '') if isinstance(snippet, dict) else getattr(snippet, 'text', '')
            for snippet in transcript
        )
        
        kw_model = KeyBERT()
        if ngram > 1:
            # mix unigrams with multigrams to diversify results
            keywords1 = kw_model.extract_keywords(
                full_text,
                keyphrase_ngram_range=(1, 1), # force unigram first since multigrams domnianate
                use_mmr=True,
                diversity=diversity, # diversify keywords
                top_n=n//2
            )

            keywords2 = kw_model.extract_keywords(
                full_text,
                keyphrase_ngram_range=(ngram, ngram), # ngram
                use_mmr=True,
                diversity=diversity, # diversify keywords
                top_n=n//2
            )
            
            keywords = keywords1 + keywords2 # join
            keywords.sort(key=lambda x: x[1], reverse=True)

            for word, score in keywords:
                print(word, score)


    else:
        print("No transcript available to process.")

def try_transcript(video_id):
    transcript = get_transcript(video_id)
    get_frequent_words(transcript, 0.4, 2)