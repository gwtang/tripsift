from argparse import ArgumentParser
from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import defaultdict
import cPickle as pickle
import re, random


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

    # Label sentence words with parts of speech (POS-tagging)
    pos_tags_byreviewid = {}
    for reviewid in reviewids:
        pos_tags_byreviewid[reviewid] = []
        for word_tokens in word_tokens_byreviewid[reviewid]:
            pos_tags = pos_tag(word_tokens)
            pos_tags_byreviewid[reviewid].append(pos_tags)

    # Clean up the words (stemming)
    # Find all the nouns
    wnl = WordNetLemmatizer()
    nouns = set(["NN", "NNS", "NNP", "NNPS"])
    all_noun_tokens = []
    for reviewid in reviewids:
        sents = pos_tags_byreviewid[reviewid]
        for sent in sents:
            for word, pos in sent:
                if ((pos in nouns) and (word.isalpha())):
                    all_noun_tokens.append(wnl.lemmatize(word))

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
                    if (pos in nouns) and (wnl.lemmatize(w) == term):
                        member_reviewids.append(reviewid)
        noun_document_membership[term] = set(member_reviewids)

    # Output data
    outfile = "%s/sent_tokens_byreviewid.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(sent_tokens_byreviewid, outfile)
    outfile.close()

    outfile = "%s/word_tokens_byreviewid.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(word_tokens_byreviewid, outfile)
    outfile.close()

    outfile = "%s/pos_tags_byreviewid.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(pos_tags_byreviewid, outfile)
    outfile.close()

    outfile = "%s/noun_document_membership.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(noun_document_membership, outfile)
    outfile.close()


if __name__ == "__main__":
    main()
