from argparse import ArgumentParser
from collections import defaultdict
from numpy import average, std
import cPickle as pickle

def main():
    parser = ArgumentParser()
    parser.add_argument("--filename", type=str, dest="filename")
    args = parser.parse_args()
    
    # Find the folders for all hotels
    infile = open(args.filename, 'r')
    hotelurllist = infile.read().splitlines()
    infile.close()
    folders = [line.split("-")[4] for line in hotelurllist]

    # Define number of hotels
    num_hotels = len(folders)

    term_sentiment = defaultdict(list)
    for folder in folders:
	infile = "TAwebpages/%s/hotelterms.tab" %folder
	infile = open(infile, 'r')
	termdata = infile.read().splitlines()
	infile.close()

	for line in termdata:
	    line = line.split()
	    term = line[2]
	    sentiment = float(line[5])
	    term_sentiment[term].append(sentiment)

    uniques = []  # Rare terms (bottom 1/3)
    middle = []   # Intermediate terms (middle 1/3)  
    commons = {}  # Common terms (top 1/3) (average, std)
    for term in term_sentiment:
	num_hotels_with_term = len(term_sentiment[term])
	if num_hotels_with_term < num_hotels/4:
	    uniques.append(term)
	elif num_hotels_with_term > num_hotels/4*3:
	    term_avg = average(term_sentiment[term])
	    term_std = std(term_sentiment[term])
	    commons[term] = (term_avg, term_std)
	else:
	    middle.append(term)

    # Output the term class data
    outfile = "term_averages.pyvar"
    outfile = open(outfile, 'w')
    pickle.dump((uniques, middle, commons), outfile)
    outfile.close()


if __name__ == "__main__":
    main()
