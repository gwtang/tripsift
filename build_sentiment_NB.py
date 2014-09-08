from nltk.classify import NaiveBayesClassifier
from nltk.stem import WordNetLemmatizer
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from collections import defaultdict
import nltk.classify.util
import cPickle as pickle
import random, itertools

from nltk.corpus import stopwords
stopset = set(stopwords.words('english'))

# The feature is the word, it has been observed, thus True
def get_unigram_features(words):
    return dict([(word, True) for word in words])


def get_stopword_filtered_features(words):
    return dict([(word, True) for word in words if word not in stopset])


def get_bigram_features(words, score_fn=BigramAssocMeasures.chi_sq, n=1000):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return dict([(ngram, True) for ngram in itertools.chain(words, bigrams)])


def eval_classifier(negids, posids, word_tokens, feature_type):
    # Calculate the features
    negfeatures = [(feature_type(word_tokens[fid]), 'neg') for fid in negids]
    posfeatures = [(feature_type(word_tokens[fid]), 'pos') for fid in posids]

    # Shuffle and balance the two classes
    n_min = min([len(negfeatures), len(posfeatures)])
    random.shuffle(negfeatures)
    negfeatures = negfeatures[:n_min]
    random.shuffle(posfeatures)
    posfeatures = posfeatures[:n_min]

    # Define training and testing data
    n_training = n_min*3/4
    print "neg examples: %d\t pos examples: %d" %(len(negfeatures), len(posfeatures))

    traindata = negfeatures[:n_training] + posfeatures[:n_training]
    testdata = negfeatures[n_training:] + posfeatures[n_training:]
    print 'train on %d instances, test on %d instances' % (len(traindata), len(testdata))

    classifier = NaiveBayesClassifier.train(traindata)
    truthsets = defaultdict(set)
    testsets = defaultdict(set)
 
    for i, (features, label) in enumerate(testdata):
            truthsets[label].add(i)
            predicted = classifier.classify(features)
            testsets[predicted].add(i)

    print 'accuracy:', nltk.classify.util.accuracy(classifier, testdata)
    print 'pos precision:', nltk.metrics.precision(truthsets['pos'], testsets['pos'])
    print 'pos recall:', nltk.metrics.recall(truthsets['pos'], testsets['pos'])
    print 'neg precision:', nltk.metrics.precision(truthsets['neg'], testsets['neg'])
    print 'neg recall:', nltk.metrics.recall(truthsets['neg'], testsets['neg'])

    classifier.show_most_informative_features()

    # Save the classifier trained using all data
    #classifier = NaiveBayesClassifier.train(negfeatures + posfeatures)
    #outfile = "%s/NB_sentiment.model.pyvar" %resultfolder
    #outfile = open(outfile, 'w')
    #pickle.dump(classifier, outfile)
    #outfile.close()

def main():
    # Load the tokenized reviews (sentences)
    infile = "%s/NB_trainingdata.senttokens.pyvar" %resultfolder
    infile = open(infile, 'r')
    word_tokens_byreviewid = pickle.load(infile)
    infile.close()

    # Don't flatten, sentence by sentence level
    # Flatten the sentences of a reivew into 1D
    # Stem the words too
    word_tokens_byreviewid_flat = {}
    wnl = WordNetLemmatizer()
    for reviewid in word_tokens_byreviewid:
        flatten = [word for sent in word_tokens_byreviewid[reviewid] for word in sent]
        word_tokens_byreviewid_flat[reviewid] = [wnl.lemmatize(word) for word in sent]

    # Load the training reviewids
    infile = "%s/NB_trainingdata.labels.pyvar" %resultfolder
    infile = open(infile, 'r')
    keepreviewids = pickle.load(infile)
    infile.close()

    # Define the pos and neg sets
    negids = keepreviewids[1]  # 1 star
    posids = keepreviewids[5]  # 5 star

    #eval_classifier(negids, posids, word_tokens_byreviewid_flat, get_unigram_features)
    #eval_classifier(negids, posids, word_tokens_byreviewid_flat, get_stopword_filtered_features)
    eval_classifier(negids, posids, word_tokens_byreviewid_flat, get_bigram_features)


if __name__ == "__main__":
    resultfolder = "NB_data"
    main()
