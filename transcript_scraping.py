from youtube_transcript_api import YouTubeTranscriptApi
from keybert import KeyBERT
import spacy
import keyword_spacy

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
        
        nlp = spacy.load("en_core_web_md")
        nlp.add_pipe(
            "keyword_extractor",
            last=True,
            config={"top_n": 10, "min_ngram": 3, "max_ngram": 3, "strict": True}
        )

        doc = nlp(full_text)

        candidates = []
        for chunk in doc.noun_chunks:
            valid_tokens = [token for token in chunk if token.pos_ in {"NOUN", "PROPN", "ADJ"} 
                            and not token.is_stop and not token.is_punct]
            if valid_tokens:
                if len(valid_tokens) == 1:
                    lemma_word = valid_tokens[0].lemma_.lower()
                    candidates.append(lemma_word)
                else:
                    phrase = " ".join([token.text.lower() for token in valid_tokens])
                    candidates.append(" ".join(phrase))
            
        candidates = list(set([c for c in candidates if len(c.strip()) > 1]))

        kw_model = KeyBERT()
        if ngram > 1:
            # mix unigrams with multigrams to diversify results
            keywords = kw_model.extract_keywords(
                full_text,
                candidates=candidates,
                use_mmr=True,
                diversity=diversity, # diversify keywords
                top_n=n
            )

            for word, score in keywords:
                print(word, score)

    else:
        print("No transcript available to process.")

def try_transcript(video_id):
    transcript = get_transcript(video_id)
    get_frequent_words(transcript, 0.4, 2)