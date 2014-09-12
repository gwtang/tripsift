from argparse import ArgumentParser
from nltk.classify import NaiveBayesClassifier
from nltk.stem import WordNetLemmatizer
from nltk import FreqDist
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from sent_features import get_sent_features, get_bad_words
from collections import defaultdict
from pandas import DataFrame
import nltk.classify.util
import cPickle as pickle
import random

def make_folds(vector, n):
    return [vector[i:i+n] for i in range(0, len(vector), n)]


def eval_classifier(traindata, testdata):
    classifier = NaiveBayesClassifier.train(traindata)
    truthsets = defaultdict(set)
    testsets = defaultdict(set)
 
    for i, (features, label) in enumerate(testdata):
        truthsets[label].add(i)
        prediction = classifier.classify(features)
        testsets[prediction].add(i)

    accuracy = nltk.classify.util.accuracy(classifier, testdata)
    posprecision = nltk.metrics.precision(truthsets['pos'], testsets['pos'])
    posrecall = nltk.metrics.recall(truthsets['pos'], testsets['pos'])
    negprecision = nltk.metrics.precision(truthsets['neg'], testsets['neg'])
    negrecall = nltk.metrics.recall(truthsets['neg'], testsets['neg'])
    return accuracy, posprecision, posrecall, negprecision, negrecall


def main():
    parser = ArgumentParser()
    parser.add_argument("--folder", type=str, dest="folder")
    args = parser.parse_args()

    # Load the tokenized reviews (sentences)
    infile = "%s/NB_trainingdata.senttokens.pyvar" %args.folder
    infile = open(infile, 'r')
    word_tokens_byreviewid = pickle.load(infile)
    infile.close()

    # Load the training reviewids
    infile = "%s/NB_trainingdata.labels.pyvar" %args.folder
    infile = open(infile, 'r')
    keepreviewids = pickle.load(infile)
    infile.close()

    # Stem the words in the sentences
    # Separate each sentence into a unique entry
    wnl = WordNetLemmatizer()
    word_tokens_byreviewid_expanded = {}
    negtags = []; postags = []
    for reviewid in word_tokens_byreviewid:
        sents = word_tokens_byreviewid[reviewid]
	for sent_idx in range(0, len(sents)):
	    tag = (reviewid, str(sent_idx))
            words = [wnl.lemmatize(word) for word in sents[sent_idx]]
	    word_tokens_byreviewid_expanded[tag] = words
	    if reviewid in keepreviewids[1]:
		negtags.append(tag)
	    if reviewid in keepreviewids[5]:
		postags.append(tag)

    # Get all words to analyze frequency of unigrams and bigrams
    all_words = [word for tag in word_tokens_byreviewid_expanded for word in word_tokens_byreviewid_expanded[tag]]
    # Get all the stop words
    stopwords = get_bad_words()

    # Unigrams
    word_freq_dist = DataFrame(dict(FreqDist(all_words)).items(), columns = ['word','count'])
    word_freq_dist = word_freq_dist[word_freq_dist['count'] > 100]
    good_features = list(word_freq_dist['word'])

    # Bigrams
    bigram_finder = BigramCollocationFinder.from_words(all_words)
    bigram_finder.apply_freq_filter(50)
    bigram_finder.apply_word_filter(lambda stopword: stopword in stopwords)
    bigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, 1000)
    good_features.extend(bigrams)
    print "Number unigrams + bigrams: %d" %len(good_features)

    # Calculate the features
    negfeatures = [(get_sent_features(word_tokens_byreviewid_expanded[fid], good_features), 'neg') 
                   for fid in negtags]
    posfeatures = [(get_sent_features(word_tokens_byreviewid_expanded[fid], good_features) , 'pos') 
                   for fid in postags]
    print "neg sents: %d\t pos sents: %d" %(len(negfeatures), len(posfeatures))

    # Shuffle and balance the two classes
    n_min = min([len(negfeatures), len(posfeatures)])
    random.shuffle(negfeatures)
    negfeatures = negfeatures[:n_min]
    random.shuffle(posfeatures)
    posfeatures = posfeatures[:n_min]
    print "neg examples: %d\t pos examples: %d" %(len(negfeatures), len(posfeatures))

    # Define training and testing data
    numfolds = 10
    foldsize = n_min/numfolds
    negfolds = make_folds(negfeatures, foldsize)
    posfolds = make_folds(posfeatures, foldsize)

    # 10 fold cross validation
    outfile = "%s/NB_sentiment.model.performance.tab" %args.folder
    outfile = open(outfile, 'w')
    outfile.write("Fold\taccuracy\tpos_precision\tpos_recall\tneg_precision\tneg_recall\n")
    for fold in range(0, numfolds):
	outfile.write("%d\t" %fold)
	testdata = negfolds[fold] + posfolds[fold]
	traindata = []
	for i in range(0, numfolds):
	    if i != fold:
		traindata += negfolds[i]
		traindata += posfolds[i]
    	print 'train on %d instances, test on %d instances' % (len(traindata), len(testdata))

    	result = eval_classifier(traindata, testdata)
	accuracy, posprecision, posrecall, negprecision, negrecall = result
        outfile.write("%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" 
                    %(accuracy, posprecision, posrecall, negprecision, negrecall))
    outfile.close()

    # Save the classifier trained using all data
    classifier = NaiveBayesClassifier.train(negfeatures + posfeatures)
    outfile = "%s/NB_sentiment.model.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(classifier, outfile)
    outfile.close()


if __name__ == "__main__":
    main()
