from argparse import ArgumentParser
from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer

def get_hotel_location(filename):
    filename = open(filename, 'r')
    html = filename.readlines()
    filename.close()
    i = 0
    while i < len(html):
        line = html[i].strip()
        if "<meta" in line and "keywords" in line:
	    line = line.replace("&#39;","'")
	    line = line.lower()
            line = line.split("\"")[3].split(",")
	    return line
        i = i + 1

def main():
    parser = ArgumentParser()
    parser.add_argument("--folder", type=str, dest="folder")
    args = parser.parse_args()

    filename = "%s/batch_1.html" %args.folder
    info = get_hotel_location(filename)
    name = word_tokenize(info[0])
    location = word_tokenize(info[1])
    location += word_tokenize(info[2])
    location += word_tokenize(info[3])
    other = ["star", "etc"]

    outfile = "%s/hotel_info.txt" %args.folder
    outfile = open(outfile, 'w')
    outfile.write("\n".join(name) + "\n")
    outfile.write("\n".join(location) + "\n")
    outfile.write("\n".join(other))
    outfile.close()


if __name__ == "__main__":
    main()
