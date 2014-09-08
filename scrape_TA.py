from argparse import ArgumentParser
from urllib import urlopen
from subprocess import Popen, PIPE
import os, time, random

def get_html(url, filename, delay=0):
    if os.path.exists(filename):
	return
    print "downloading %s" %url
    time.sleep(delay)
    html = urlopen(url).read()
    outfile = open(filename, 'w')
    outfile.write(html)
    outfile.close()


def get_review_ids(filename):
    cmd = "egrep review_[0-9] %s | grep div " %filename
    stdout, stderr = Popen(cmd, shell=True, stdout=PIPE).communicate()
    stdout = stdout.strip().split("\n")
    reviewids = []
    for line in stdout:
	reviewids.append(line.split("_")[1].split("\"")[0])
    return reviewids


def get_num_reviews(filename):
    filename = open(filename, 'r')
    html = filename.readlines()
    filename.close()

    i = 0
    while i < len(html):
	line = html[i].strip()
	if line == "<span class=\"tabs_pers_titles\">Reviews</span>":
	    numreviews = re.findall('[0-9]+', html[i+1])[0]
	    return int(numreviews)
	i = i + 1


def get_hotel_reviews(locationid, hotelurl, hotelid, folder, batch, delay=2):
    # Define the url depending on the batch
    if batch != 1:
	temp = hotelurl.split("-")
	hotelurl = "%s-or%d0-%s" %("-".join(temp[:3]), batch-1, "-".join(temp[3:]))

    # Download the batch (incomplete reviews)
    filename = "%s/batch_%d.html" %(folder, batch)
    get_html(hotelurl, filename)

    # Get the review id numbers
    reviewids = get_review_ids(filename)
    outfile = "%s/batch_%d.reviewids.txt" %(folder, batch)
    outfile = open(outfile, 'w')
    outfile.write("\n".join(reviewids) + "\n")
    outfile.close()

    # Define the url to get the full reviews
    reviewids = ",".join(reviewids)
    reviewsurl = ("%s/ExpandedUserReviews-%s-d%s?target=%s&context=1&"
                  "reviews=%s&servlet=Hotel_Review&expand=1" 
                  %(base_url, locationid, hotelid, reviewids, reviewids))

    # Download the batch (complete reviews)
    filename = "%s/batch_full_%d.html" %(folder, batch)
    get_html(reviewsurl, filename, delay + random.randrange(0, 5))


def main():
    parser = ArgumentParser()
    parser.add_argument("--filename", type=str, dest="filename")
    parser.add_argument("--folder", type=str, dest="folder")
    args = parser.parse_args()

    infile = open(args.filename, 'r')
    hotelurllist = infile.read().splitlines()
    infile.close()

    for hotelurl in hotelurllist:
	header, locationid, hotelid, text, hotelname, locationstring = hotelurl.split("-")
	hotelid = hotelid[1:]

	# Create a folder to store all related files
	subfolder = "%s/%s" %(args.folder, hotelname)
	if not os.path.exists(subfolder):
	    os.mkdir(subfolder)

	# Scrape each page of reviews as a batch
	batch = 1
	get_hotel_reviews(locationid, hotelurl, hotelid, subfolder, batch)

	# Get number of reviews to expect
        filename = "%s/batch_1.html" %subfolder
	cmd = "grep pgCount %s | cut -d' ' -f4" %filename
	numreviews, stderr = Popen(cmd, shell=True, stdout=PIPE).communicate()
	numreviews = numreviews.replace(",","")
	numreviews = int(numreviews)
	numreviewpages = numreviews/reviews_per_page
	if numreviews % reviews_per_page > 0:
		numreviewpages += 1

	while batch < numreviewpages:
	    batch += 1
	    get_hotel_reviews(locationid, hotelurl, hotelid, subfolder, batch)

        print "%s n_reviews: %d n_pages: %d" %(hotelname, numreviews, numreviewpages)


if __name__ == "__main__":
    base_url = "http://www.tripadvisor.com"
    reviews_per_page = 10
    main()
