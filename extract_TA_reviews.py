from argparse import ArgumentParser
from bs4 import BeautifulSoup
import cPickle as pickle
import os

def get_review_text(filename, reviewids):
    filename = open(filename, 'r')
    html = filename.readlines()
    filename.close()

    # Cycle through each line sequentially to find reviews (skip owner responses)
    # Cycle through each line to determine if Google translate is offered (skip non-english)
    reviews = {}
    i = 0; keep = False
    while i < len(html):
        line = html[i].strip()
        if "<div" in line and "ShowUserReviews" in line and "#CHECK_RATES_CONT" in line:
            temp = BeautifulSoup(line)
            reviewid = temp.a['id'][1:]
            if reviewid in reviewids:
                keep = True
        if "googleTranslation" in line:
            keep = False
        if line == "<p>" and keep:
            rawtext = html[i+1].strip()
            rawtext = rawtext.replace("<br/>", "")
            rawtext = rawtext.replace("&quot;", "\"")
            rawtext = rawtext.replace("&amp;", "and")
            reviews[reviewid] = rawtext
            keep = False
        i = i + 1
    return reviews


def main():
    parser = ArgumentParser()
    parser.add_argument("--folder", type=str, dest="folder")
    args = parser.parse_args()

    reviews = {}

    # Process each batch (page) of reviews scraped
    batch = 1
    infile = "%s/batch_%d.reviewids.txt" %(args.folder, batch)

    while os.path.exists(infile):
        # Get the review ids
        infile = open(infile, 'r')
        reviewids = infile.read().splitlines()
        infile.close()

        # Pull the review text
	filename = "%s/batch_full_%d.html" %(args.folder, batch)
        review_batch = get_review_text(filename, reviewids)
        reviews.update(review_batch)

	batch += 1
	infile = "%s/batch_%d.reviewids.txt" %(args.folder, batch)

    # Output the reviews
    # Format: dictionary
    # keys = reviewid ; values = text
    outfile = "%s/reviewtext.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(reviews, outfile)
    outfile.close()

    print "%s\tn_reviews: %d" %(args.folder, len(reviews))
if __name__ == "__main__":
    main()

