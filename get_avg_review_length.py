import cPickle as pickle

infile = "hotel_urls.bigisland.txt"
infile = open(infile, 'r')
data = infile.read().splitlines()
infile.close()

folders = [line.split("-")[4]for line in data]

num_sents = []
num_words = []
for folder in folders:
    infile = "TAwebpages/%s/word_tokens_byreviewid.pyvar" %folder
    infile = open(infile, 'r')
    words_byreviewid = pickle.load(infile)
    infile.close()

    for reviewid in words_byreviewid:
 	n = len(words_byreviewid[reviewid])
	num_sents.append(n)

    for reviewid in words_byreviewid:
	for sent in words_byreviewid[reviewid]:
	    n = len(sent)
	    num_words.append(n)

print num_sents
print num_words
