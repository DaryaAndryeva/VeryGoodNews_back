from natasha import Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab, Doc
from datetime import datetime, timedelta

segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
morph_vocab = MorphVocab()

def LemmatizeText(text):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    return " ".join([token.lemma if token.lemma else token.text for token in doc.tokens])

TIMEDELTA = timedelta(hours = 2)