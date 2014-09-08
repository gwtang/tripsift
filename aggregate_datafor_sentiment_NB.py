from nltk import sent_tokenize, word_tokenize
from collections import defaultdict
import cPickle as pickle
import re, random

def main():
    sourcefolder = "TAwebpages"

    infile = "hotel_url_list.forNBsentiment.list"
    infile = open(infile, 'r')
    urllist = infile.read().splitlines()
    infile.close()

    keepreviewids = defaultdict(list)
    raw_reviews = {} 

    # Load the raw reviews
    folders = [url.split("-")[4] for url in urllist]
    for folder in folders:
        filename = "%s/%s/reviewtext.pyvar" %(sourcefolder, folder)
    	filename = open(filename, 'r')
     	raw_reviews.update(pickle.load(filename))
    	filename.close()

        # Load review star rating
        infile = "%s/%s/ratings.pyvar" %(sourcefolder, folder)
        infile = open(infile, 'r')
        ratings_byreviewid = pickle.load(infile)
        infile.close()

        for key in ratings_byreviewid:
 	    stars = ratings_byreviewid[key]
	    if stars in [1,5]:
		if key in raw_reviews:  # Remove non-english reviews
	            keepreviewids[stars].append(key)

    print "neg", len(keepreviewids[1])
    print "pos", len(keepreviewids[5])
    reviewids = keepreviewids[1] + keepreviewids[5]
    print "neg+pos",len(reviewids)

    # Convert raw text into sentences
    sent_tokens_byreviewid = {}
    for reviewid in reviewids:
        rawtext = raw_reviews[reviewid]
        rawtext = rawtext.replace("/", " ")
        rawtext = str(unicode(rawtext, 'ascii', 'ignore'))
        rawtext = rawtext.lower()
        sent_tokens = sent_tokenize(rawtext)
        sent_tokens_fixed = []
        for sent in sent_tokens:
            while re.search("[a-zA-Z][!?.][a-zA-Z]", sent):
                x,y = re.search("[a-zA-Z][!?.][a-zA-Z]", sent).span()
                sent_tokens_fixed.append(sent[:x+2])
                sent = sent[x+2:]
            sent_tokens_fixed.append(sent)
        sent_tokens_byreviewid[reviewid] = sent_tokens_fixed

    # Convert setences into words
    word_tokens_byreviewid = {}
    for reviewid in reviewids:
        sent_tokens = sent_tokens_byreviewid[reviewid]
        word_tokens_byreviewid[reviewid] = []
        for sent in sent_tokens:
            word_tokens = word_tokenize(sent)
            word_tokens_byreviewid[reviewid].append(word_tokens)

    # Output the tokenized reviews
    outfile = "%s/NB_trainingdata.wordtokens.pyvar" %resultfolder
    outfile = open(outfile, 'w')
    pickle.dump(sent_tokens_byreviewid, outfile)
    outfile.close()

    outfile = "%s/NB_trainingdata.senttokens.pyvar" %resultfolder
    outfile = open(outfile, 'w')
    pickle.dump(word_tokens_byreviewid, outfile)
    outfile.close()

    # Output the training reviewids
    outfile = "%s/NB_trainingdata.labels.pyvar" %resultfolder
    outfile = open(outfile, 'w')
    pickle.dump(keepreviewids, outfile)
    outfile.close()


if __name__ == "__main__":
    resultfolder = "NB_data"
    main()
