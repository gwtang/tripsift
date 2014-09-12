from argparse import ArgumentParser
from tokenization import my_sent_tokenizer, my_word_tokenizer
from collections import defaultdict
import cPickle as pickle

def main():
    parser = ArgumentParser()
    parser.add_argument("--sourcefolder", type=str, dest="sourcefolder")
    parser.add_argument("--outputfolder", type=str, dest="resultfolder")
    parser.add_argument("--file", type=str, dest="filename")
    args = parser.parse_args()

    infile = open(args.filename, 'r')
    urllist = infile.read().splitlines()
    infile.close()

    keepreviewids = defaultdict(list)
    raw_reviews = {} 

    # Load the raw reviews
    folders = [url.split("-")[4] for url in urllist]
    for folder in folders:
        filename = "%s/%s/reviewtext.pyvar" %(args.sourcefolder, folder)
    	filename = open(filename, 'r')
	hoteldata = pickle.load(filename)
     	raw_reviews.update(hoteldata)
    	filename.close()

        # Load review star rating
        infile = "%s/%s/ratings.pyvar" %(args.sourcefolder, folder)
        infile = open(infile, 'r')
        ratings_byreviewid = pickle.load(infile)
        infile.close()

	# Keep extreme reviews
	reviewids = hoteldata.keys()
	numkept = 0
        for reviewid in reviewids:
 	    stars = ratings_byreviewid[reviewid]
	    if stars in [1, 5]:
	        keepreviewids[stars].append(reviewid)
		numkept += 1
	    else:
		del raw_reviews[reviewid]
	print "%5d extreme reviews for %s" %(numkept, folder)

    print "%5d 1-star reviews" %len(keepreviewids[1])
    print "%5d 5-star reviews" %len(keepreviewids[5])
    reviewids = keepreviewids[1] + keepreviewids[5]

    # Convert raw text into sentences
    sent_tokens_byreviewid = my_sent_tokenizer(raw_reviews)

    # Convert setences into words
    word_tokens_byreviewid = my_word_tokenizer(sent_tokens_byreviewid)

    # Output the tokenized reviews
    outfile = "%s/NB_trainingdata.wordtokens.pyvar" %args.resultfolder
    outfile = open(outfile, 'w')
    pickle.dump(sent_tokens_byreviewid, outfile)
    outfile.close()

    outfile = "%s/NB_trainingdata.senttokens.pyvar" %args.resultfolder
    outfile = open(outfile, 'w')
    pickle.dump(word_tokens_byreviewid, outfile)
    outfile.close()

    # Output the training reviewids
    outfile = "%s/NB_trainingdata.labels.pyvar" %args.resultfolder
    outfile = open(outfile, 'w')
    pickle.dump(keepreviewids, outfile)
    outfile.close()


if __name__ == "__main__":
    main()
