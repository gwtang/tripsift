from argparse import ArgumentParser
from nltk import WordNetLemmatizer
from sent_features import get_sent_features
from math import pow
import cPickle as pickle

def delete_terms(term_dict, bad_terms):
    all_terms = term_dict.keys()
    for term in all_terms:
	if term in set(bad_terms):
	    del term_dict[term]
    return


def get_date_score(date_vec):
    score = 0
    for date in date_vec:
	delta2014 = 2014 - date
        score += 1/(pow(2, delta2014))
    n = len(date_vec)
    return round(1.0*score/n, 2)


# Get the sentence ids with the term of interest
def get_sentence_ids(sentences, term):
    sentence_ids = []
    n_sent = len(sentences)
    for sent_id in range(0, n_sent):
        for word, postag in sentences[sent_id]:
            if word == term:
		sentence_ids.append(sent_id)
                break
    return sentence_ids

# Determine if a term is rare or common or inbetween
# If common, determine if average, above avg, below avg
def compare_to_average(uniques, commons, term, sentiment):
    if term in commons:
        avg, stdev = commons[term]
        if sentiment > avg + stdev:
            return "class_icons-03.png"   # above average
        elif sentiment < avg - stdev:
            return "class_icons-01.png"  # below average
        else:
            return "class_icons-02.png"  # average
    elif term in uniques: 
            return "class_icons-04.png" # unique
    else:
	    return  # not common or unique


def main():
    parser = ArgumentParser()
    parser.add_argument("--folder", type=str, dest="folder")
    parser.add_argument("--cutoff", type=float, dest="cutoff")
    args = parser.parse_args()

    hotelname = args.folder.split("/")[1]

    # Load the NB classifier
    infile = "NB_data/NB_sentiment.model.pyvar"
    infile = open(infile, 'r')
    classifier = pickle.load(infile)
    infile.close()

    # Load the review dates
    filename = "%s/dates.pyvar" %args.folder
    filename = open(filename, 'r')
    dates = pickle.load(filename)
    filename.close()
    num_reviews = len(dates)

    # Load information for the hotel
    filename = "%s/hotel_info.txt" %args.folder
    filename = open(filename, 'r')
    bad_terms = filename.read().split()
    filename.close()

    # Load excluded words (manually defined)
    filename = "custom_exclude_words.txt" 
    filename = open(filename, 'r')
    bad_terms.extend(filename.read().split())
    filename.close()

    # Load the term - reviewid mapping
    filename = "%s/noun_document_membership.pyvar" %args.folder
    filename = open(filename, 'r')
    noun_reviewids = pickle.load(filename)
    filename.close()

    # Remove infrequent terms and single letters
    for term in noun_reviewids:
        count = len(noun_reviewids[term])
        if count < num_reviews*args.cutoff:
            bad_terms.append(term)
        elif len(term) == 1:
            bad_terms.append(term)

    # Remove bad terms
    delete_terms(noun_reviewids, bad_terms)

    # Load POS tagged words
    filename = "%s/pos_tags_byreviewid.pyvar" %args.folder
    filename = open(filename, 'r')
    pos_tags_byreviewid = pickle.load(filename)
    filename.close()

    # Load the sentences
    filename = "%s/sent_tokens_byreviewid.pyvar" %args.folder
    filename = open(filename, 'r')
    sent_tokens_byreviewid = pickle.load(filename)
    filename.close()

    # Load the sentences with words split out
    filename = "%s/word_tokens_byreviewid.pyvar" %args.folder
    filename = open(filename, 'r')
    word_tokens_byreviewid = pickle.load(filename)
    filename.close()

    # Load the term averages and standard deviations
    filename = "term_averages.pyvar"
    filename = open(filename, 'r')
    uniques, middle, commons = pickle.load(filename)
    filename.close()

    wnl = WordNetLemmatizer()

    # Define the list of frequent terms
    freqterms = noun_reviewids.keys()

    outfile1 = "%s/hotelterms.tab" %args.folder
    print outfile1
    outfile1 = open(outfile1, 'w')
    outfile2 = "%s/mapping.tab" %args.folder
    print outfile2
    outfile2 = open(outfile2, 'w')

    for term_id in range(0, len(freqterms)):
	freqterm = freqterms[term_id]
        reviewids_forterm = noun_reviewids[freqterm]

        # Determine a score for the review dates
	review_dates = [int(dates[reviewid]) for reviewid in reviewids_forterm]
        dscore = get_date_score(review_dates)

        sents_as_words = []
        for reviewid in reviewids_forterm:
	    sent_ids = get_sentence_ids(pos_tags_byreviewid[reviewid], freqterm)
	    for sent_id in sent_ids:
                outfile2.write("%s\t%s\t%s\t%s\n" %(hotelname, term_id, reviewid, sent_id))
		sents_as_words.append(word_tokens_byreviewid[reviewid][sent_id])

        predictions = []
        for i in range(0, len(sents_as_words)):
	    words = [wnl.lemmatize(word) for word in sents_as_words[i]]
	    words = [word for word in words if word != freqterm]
            pred = classifier.classify(get_sent_features(words))
	    predictions.append(pred)
        pos_percent = round(100.0*predictions.count("pos")/len(predictions),2)

	# Determine how this sentiment compares to other hotels
	label = compare_to_average(uniques, commons, freqterm, pos_percent)

        num_term = len(noun_reviewids[freqterm])
        outfile1.write("%s\t%s\t%s\t%s\t%.3f\t%s\t%.2f\t%s\n" %(hotelname, term_id, 
                      freqterm, num_term, 100.0*num_term/num_reviews, pos_percent, dscore, label))
    outfile1.close()
    outfile2.close()


if __name__ == "__main__":
    main()
