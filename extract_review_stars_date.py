from argparse import ArgumentParser
from subprocess import Popen, PIPE
import cPickle as pickle
import glob

def get_stars(filename):
    cmd = "grep -B2 ratingDate %s | grep stars | cut -d'\"' -f6" %filename
    stdout, stderr = Popen(cmd, shell=True, stdout=PIPE).communicate()
    stdout = stdout.strip().split("\n")
    if stdout != ['']:
	return [line[0] for line in stdout]
    else:
	print "Error"

def get_dates(filename):
    months = {"January": 1, "February": 2, "March": 3, "April": 4, "May":5, 
              "June": 6, "July": 7, "August": 8, "September": 9, 
              "October": 10, "November": 11, "December": 12}
    cmd = "grep ratingDate %s" %filename
    stdout, stderr = Popen(cmd, shell=True, stdout=PIPE).communicate()
    stdout = stdout.strip().split("\n")
    if stdout != ['']:
	dates = []
	for line in stdout:
	    line = line.split()
	    if line[2] == "relativeDate\"":
		month = months[line[3][7:]]
		year = line[5][:4]
	    else:
	    	month = months[line[2]]
	    	year = line[4]
	    dates.append([month,year])
	return dates
    else:
	print "Error"


def get_reviewids(filename):
    filename = open(filename, 'r')
    reviewids = filename.read().splitlines()
    filename.close()
    return reviewids


def main():
    parser = ArgumentParser()
    parser.add_argument("--folder", type=str, dest="folder")
    args = parser.parse_args()

    result = {}

    filenames = glob.glob('%s/batch_full_[0-9]*.html' %args.folder)
    for filename in filenames:
        filename = filename.replace("\\","/")

	ratings = get_stars(filename)
	# Output the ratings
    	outfile = filename[:-4] + "ratings.txt"
	outfile = open(outfile, 'w')
	outfile.write("\n".join(ratings) + "\n")
	outfile.close()

	dates = get_dates(filename)
	# Output the review dates
        outfile = filename[:-4] + "reviewdates.txt"
        outfile = open(outfile, 'w')
	for month,year in dates:
	    outfile.write("%s\t%s\n" %(month, year))
        outfile.close()

	# Load the reivew ids
	batch = filename.split("_")[-1].split(".")[0]
	filename = "%s/batch_%s.reviewids.txt" %(args.folder, batch)
	reviewids = get_reviewids(filename)

	if len(reviewids) == len(ratings):
	    for i in range(0, len(reviewids)):
		result[reviewids[i]] = int(ratings[i])
	else:
	    print "Error: ratings"

    # Output the result dictionary
    outfile = "%s/ratings.pyvar" %args.folder
    outfile = open(outfile, 'w')
    pickle.dump(result, outfile)
    outfile.close()



if __name__ == "__main__":
    main()
