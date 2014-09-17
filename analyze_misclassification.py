from argparse import ArgumentParser
from nltk.stem import WordNetLemmatizer
from sent_features import get_sent_features
import cPickle as pickle

def main():
    parser = ArgumentParser()
    parser.add_argument("--folder", type=str, dest="folder")
    args = parser.parse_args()

    # Load the NB classifier
    infile = "%s/NB_sentiment.model.pyvar" %args.folder
    infile = open(infile, 'r')
    classifier = pickle.load(infile)
    infile.close()
    classifier.show_most_informative_features(500)

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
    wnl = WordNetLemmatizer()

    correct = 0; incorrect = 0
    # Write out the mistakes made by the classifier
    outfile = "%s/mistakes_1star_reviews.txt" %args.folder
    outfile = open(outfile, 'w')
    for reviewid in keepreviewids[1]:
	for sent in word_tokens_byreviewid[reviewid]:
            words = [wnl.lemmatize(word) for word in sent]
	    score = classifier.prob_classify(get_sent_features(words, []))
	    pos_score = score.prob('pos')
	    if pos_score > 0.95:
		outfile.write("%s\t%.3f\t%s\n" %(reviewid, pos_score, " ".join(sent)))
	    if pos_score >= 0.5:
		incorrect += 1
	    else:
		correct += 1
    print "negatives correct %d incorrect %d" %(correct, incorrect)
    outfile.close()

    correct = 0; incorrect = 0
    outfile = "%s/mistakes_5star_reviews.txt" %args.folder
    outfile = open(outfile, 'w')
    for reviewid in keepreviewids[5]:
        for sent in word_tokens_byreviewid[reviewid]:
            words = [wnl.lemmatize(word) for word in sent]
            score = classifier.prob_classify(get_sent_features(sent, []))
            pos_score = score.prob('pos')
            if pos_score < 0.05:
		outfile.write("%s\t%.3f\t%s\n" %(reviewid, pos_score, " ".join(sent)))
	    if pos_score >= 0.5:
		correct += 1
	    else:
		incorrect += 1
    print "positives correct %d incorrect %d" %(correct, incorrect)
    outfile.close()


if __name__ == "__main__":
    main()
