from nltk import sent_tokenize, word_tokenize
import re

# Input: dict of reviews
# key = review ids
# value = raw text
# function returns raw text divided into sentences
def my_sent_tokenizer(raw_reviews):
    # Convert raw text into sentences
    reviewids = raw_reviews.keys()
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
    return sent_tokens_byreviewid


# Input: dict of reviews that have been broken into sentences
# key = review id
# value = list of sentences
# function returns sentences divided into words
def my_word_tokenizer(sent_tokens_byreviewid):
    # Convert setences into words
    reviewids = sent_tokens_byreviewid.keys()
    word_tokens_byreviewid = {}
    for reviewid in reviewids:
        sent_tokens = sent_tokens_byreviewid[reviewid]
        word_tokens_byreviewid[reviewid] = []
        for sent in sent_tokens:
            word_tokens = word_tokenize(sent)
            word_tokens_byreviewid[reviewid].append(word_tokens)
    return word_tokens_byreviewid
