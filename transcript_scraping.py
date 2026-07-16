from youtube_transcript_api import YouTubeTranscriptApi
from keybert import KeyBERT
import spacy
import keyword_spacy
import re


def get_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        # turn to string
        full_text = " ".join(
            snippet.get('text', '') if isinstance(snippet, dict) else getattr(snippet, 'text', '')
            for snippet in transcript
        )
        return full_text
    
    except Exception as e:
        print(f"Error fetching transcript for video ID {video_id}: {e}")
        return None

def strip_hashtags(text):
    if text:
        pattern = r"(?:^|\s)#\w+" # start of line or after white space, find continuous alphabetical character after hashtag
        clean_text = re.sub(pattern, " ", text) # substitute found hashtags with white space
        
        return re.sub(r'\s+', ' ', clean_text).strip() # substitute continuous white space with singular white space

def get_keywords(transcript, diversity=0.5, n=20):
    if transcript:
        nlp = spacy.load("en_core_web_md")
        nlp.add_pipe(
            "keyword_extractor",
            last=True,
            config={"top_n": 10, "min_ngram": 1, "max_ngram": 3, "strict": True}
        )

        doc = nlp(transcript) # get noun chunks

        # filter for nouns with adjectives so noun chunks center nouns
        candidates = []
        for chunk in doc.noun_chunks:
            # skip any urls, emails, pure numbers
            if any(token.like_url or token.like_email or token.is_digit or token.like_num for token in chunk):
                continue

            valid_tokens = [token for token in chunk if token.pos_ in {"NOUN", "PROPN", "ADJ"} 
                            and not token.is_stop and not token.is_punct]
            if valid_tokens:
                if len(valid_tokens) == 1:
                    lemma_word = valid_tokens[0].lemma_.lower() # lemmatize singular words
                    candidates.append(lemma_word)
                else:
                    phrase = " ".join([token.text.lower() for token in valid_tokens]) # tokenize phrase as 1
                    candidates.append(phrase)
            
        candidates = list(set([c for c in candidates if len(c.strip()) > 1])) # dedupe

        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(
            transcript,
            candidates=candidates,
            use_mmr=True,
            diversity=diversity, # diversify keywords
            top_n=n,
            keyphrase_ngram_range=(1, 3)
        )

        for word, score in keywords:
            print(word, score)

    else:
        print("No transcript available to process.")

def try_transcript(video_id, description):
    all_text = f"{get_transcript(video_id)}\n\n{strip_hashtags(description)}"
    get_keywords(all_text)