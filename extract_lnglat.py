from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("--filename", type=str, dest="filename")
    args = parser.parse_args()

    # Load the input KML file
    infile = open(args.filename, 'r')
    kml = infile.read().splitlines()
    infile.close()

    # Extract the hotel name + longitute + latitude
    result = []
    for line in kml:
	line = line.strip()

	if line.startswith("<name>"):
	    hotelname = line.split(">")[1].split("<")[0]
	elif line.startswith("<coordinates>"):
	    lng, lat, z = line.split(">")[1].split("<")[0].split(",")
	    print max([len(lng), len(lat)])
	    result.append([hotelname, lng, lat])

    # Output the hotel name + longitute + latitude into a tab-delimited
    # file for MySQL
    outfile = "hotel_lnglat_bigisland.tab"
    outfile = open(outfile, 'w')
    for entry in result:
	outfile.write("\t".join(entry) + "\n")
    outfile.close()


if __name__ == "__main__":
    main()
