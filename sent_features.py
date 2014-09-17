from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

def get_sent_features(words, good_features=[]): 
    score_fn=BigramAssocMeasures.raw_freq

    # Find the trigrams
    trigram_finder = TrigramCollocationFinder.from_words(words)
    trigrams = trigram_finder.nbest(score_fn, 1000)

    # Find the bigrams
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, 1000)

    features = []
    features.extend(words)
    features.extend(bigrams)
    features.extend(trigrams)

    if good_features == []:
	good_features = features

    features = list(set(features).intersection(set(good_features)))
    return dict([(ngram, True) for ngram in features])


from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
def get_bad_words():
    wnl = WordNetLemmatizer()
    ignore = [wnl.lemmatize(word) for word in stopwords.words('english')]
    ignore.extend([',', '.', '!','?', ';', '(', ')','-',':','...','``',"''"])
    ignore = set(ignore)
    return ignore
