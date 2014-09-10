from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

def get_sent_features(words, score_fn=BigramAssocMeasures.chi_sq, n=1000):
    # Determine the bad words
    bad_words = get_bad_words()

    # Find the bigrams
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    final_terms = list(set(words) - bad_words)
    for word1, word2 in bigrams:
        if (word1 in bad_words) or (word2 in bad_words):
            pass
        else:
            final_terms.append((word1, word2))
    # The feature is the word/wordpair; it has been observed, thus True
    return dict([(ngram, True) for ngram in final_terms])


from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
def get_bad_words():
    wnl = WordNetLemmatizer()
    ignore = [wnl.lemmatize(word) for word in stopwords.words('english')]
    ignore.extend([',', '.', '!','?', ';', '(', ')','-',':'])
    ignore = set(ignore)
    return ignore
