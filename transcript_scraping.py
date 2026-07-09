from youtube_transcript_api import YouTubeTranscriptApi
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

def get_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return transcript
    
    except Exception as e:
        print(f"Error fetching transcript for video ID {video_id}: {e}")
        return None
    
def get_frequent_words(transcript, n=20):
    chunk_size = 1000 # 1000 words chunk

    if transcript:
        # for TF-IDF
        string_transcript = " ".join(snippet.text for snippet in transcript) # combine into 1 string
        
        words = string_transcript.split() # split into individual words
        documents = [" ".join(words[i:i+chunk_size]) # rejoin words within chunk   
                     for i in range(0, len(words), chunk_size)] # find next chunk
        
        # TF-IDF

        CUSTOM_STOP_WORDS = list(ENGLISH_STOP_WORDS.union({
            "just",
            "actually",
            "really",
            "like",
            "think",
            "felt",
            "feels",
            "kind",
            "thing",
            "things",
            "want",
            "make"
        }))

        vectorizer = TfidfVectorizer(
            stop_words=CUSTOM_STOP_WORDS,
            ngram_range=(2,3) # group words into 2-3 word phrases; known as ngrams
        )
        X = vectorizer.fit_transform(documents) # compute TF-IDF matrix
        feature_names = vectorizer.get_feature_names_out() # get words
        scores = X.mean(axis=0).A1 # compute mean TF-IDF score for each term across all documents
        ranked_terms = sorted(
            zip(feature_names, scores),
            key=lambda x: x[1],
            reverse=True # descending
        )
        for term, score in ranked_terms[:20]:
            print(term, score)

    else:
        print("No transcript available to process.")

def try_transcript(video_id):
    transcript = get_transcript(video_id)
    get_frequent_words(transcript)