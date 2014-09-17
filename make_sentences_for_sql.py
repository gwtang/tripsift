from argparse import ArgumentParser
import cPickle as pickle

def main():
    parser = ArgumentParser()
    parser.add_argument("--folder", type=str, dest="folder")
    args = parser.parse_args()

    # Load the review dates
    filename = "%s/dates.pyvar" %args.folder
    filename = open(filename, 'r')
    dates = pickle.load(filename)
    filename.close()

    # Load sentences
    infile = "%s/sent_tokens_byreviewid.pyvar" %args.folder
    infile = open(infile, 'r')
    sent_tokens_byreviewid = pickle.load(infile)
    infile.close()

    # Output the sentences indexed by review_id and sentence_id
    outfile = "%s/sentences.tab" %args.folder
    print outfile
    outfile = open(outfile, 'w')
    for review_id in sent_tokens_byreviewid:
        sents = sent_tokens_byreviewid[review_id]
	year = dates[review_id]
        for sent_id in range(0,len(sents)):
	    sent_text = sents[sent_id]
            outfile.write("%s\t%s\t%s\t%s\n" %(review_id, sent_id, year, sent_text))
    outfile.close()


if __name__ == "__main__":
    main()
