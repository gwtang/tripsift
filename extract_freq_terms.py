from argparse import ArgumentParser
from tokenization import my_sent_tokenizer, my_word_tokenizer
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import defaultdict
import cPickle as pickle

def main():
    parser = ArgumentParser()
    parser.add_argument("--folder", type=str, dest="folder")
    args = parser.parse_args()

    filename = "%s/reviewtext.pyvar" %args.folder
    filename = open(filename, 'r')
    raw_reviews = pickle.load(filename)
    filename.close()

    reviewids = raw_reviews.keys()
    print "# English Reviews: %d" %len(reviewids)

    # Convert raw text into sentences
    sent_tokens_byreviewid = my_sent_tokenizer(raw_reviews)

    # Output data
    outfile = "%s/sent_tokens_byreviewid.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(sent_tokens_byreviewid, outfile)
    outfile.close()

    # Convert setences into words
    word_tokens_byreviewid = my_word_tokenizer(sent_tokens_byreviewid)

    # Output data
    outfile = "%s/word_tokens_byreviewid.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(word_tokens_byreviewid, outfile)
    outfile.close()

    # Label sentence words with parts of speech (POS-tagging)
    # Clean up the words (stemming)
    # Keep only nouns
    wnl = WordNetLemmatizer()
    nouns = set(["NN", "NNS", "NNP", "NNPS"])
    pos_tags_byreviewid = {}
    for reviewid in reviewids:
        pos_tags_byreviewid[reviewid] = []
        for word_tokens in word_tokens_byreviewid[reviewid]:
            pos_tags = pos_tag(word_tokens)
	    new_pos_tags = []
	    for i in range(0, len(pos_tags)):
		w = pos_tags[i][0]
		p = pos_tags[i][1]
		if p in nouns:
		    new_pos_tags.append((wnl.lemmatize(w), p))
            pos_tags_byreviewid[reviewid].append(new_pos_tags)

    # Output data
    outfile = "%s/pos_tags_byreviewid.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(pos_tags_byreviewid, outfile)
    outfile.close()

    # Find all the nouns
    all_noun_tokens = []
    for reviewid in reviewids:
        sents = pos_tags_byreviewid[reviewid]
        for sent in sents:
            for word, pos in sent:
                if (word.isalpha()):
                    all_noun_tokens.append(word)

    # Remove bad words
    ignore = set(stopwords.words('english'))
    all_noun_tokens = set(all_noun_tokens) - ignore

    # Count document occurrence of each noun
    noun_document_membership = defaultdict(int)
    for term in set(all_noun_tokens):
        member_reviewids = []
        for reviewid in reviewids:
            for sent in pos_tags_byreviewid[reviewid]:
                for w, pos in sent:
                    if (w == term):
                        member_reviewids.append(reviewid)
        noun_document_membership[term] = set(member_reviewids)

    # Output data
    outfile = "%s/noun_document_membership.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(noun_document_membership, outfile)
    outfile.close()


if __name__ == "__main__":
    main()
