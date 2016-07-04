# file: mergepop.py
#
# purpose: merges census pop data with chinadataonline.org data
#
# created by: Andrew MacDonald on 5/31/11.
#
# copyright: (c) 2016 Andrew MacDonald. All rights reserved.
# email: andrewwm@gmail.com

import csv 
import sys
import math

####
#### GLOBAL VARIABLES
####

DEFAULT_INFILE = "mergeddata-final.csv"
DEFAULT_OUTFILE = "revised "

PROVINCE_PLACE = 1000

NEW_POPULATION_LOCATION = 138
OLD_EPOP = 88
OLD_COUNTY_POP = 152
RPOP_OFFSET = 1
ID = 4
YEAR = 1

####
#### FUNCTIONS
####

def doProvincialDeflator(row, writer):

	towrite = ""

	

	return towrite

def combinePopulation(row):
	
	towrite = ""
	datumreader = csv.reader(row)
	# gets the row in parsed form
	datarow = datumreader.next()
	
	if(datarow[OLD_COUNTY_POP] != ''):
		datarow[NEW_POPULATION_LOCATION] = datarow[OLD_COUNTY_POP]
		
	if(datarow[OLD_COUNTY_POP + RPOP_OFFSET] != ''):
		datarow.insert(NEW_POPULATION_LOCATION + 1, datarow[OLD_COUNTY_POP + RPOP_OFFSET])
	elif(datarow[OLD_EPOP + RPOP_OFFSET] != ''):
		datarow.insert(NEW_POPULATION_LOCATION + 1, datarow[OLD_EPOP + RPOP_OFFSET])
	else:
		datarow.insert(NEW_POPULATION_LOCATION + 1, '')
	
	return datarow

# Digs out the two digit province code and returns it as a float
def getProvince(province_code):

	code = float(province_code)
	
	code = code / PROVINCE_PLACE

	code = floor(code)
	
	print "code " + code
	
	return code

def checkForDuplicates(row, rowlist):

	found = False

	for checkrow in rowlist:

		rowreader = csv.reader(checkrow)
		checkrowlist = rowreader.next()

		if(checkrowlist[ID] == row[ID] and checkrowlist[YEAR] == row[YEAR]):
				if(found == False):
					found = True
				else:
					print checkrowlist[ID]
					print checkrowlist[YEAR]


##########################################################
################### START OF MAIN CODE ###################
##########################################################

specified_infile = ""
specified_outfile = ""

# check command line; sys.argv[0] is the name of the file, [1] is the first arg
# will first check for an infile, then an outfile
try:
	print sys.argv[1]

	if(sys.argv[1] != ""):
		specified_infile = sys.argv[1]
	
	try:
		if(sys.argv[2] != ""):
			specified_outfile = sys.argv[2]
	except:
		specified_outfile = ""
except:
	specified_infile = ""

print "infile " + specified_infile
print "outfile " + specified_outfile	

# Opening files
infilename = ""
outfilename = ""

# Doing infile
if(specified_infile != ""):
	infilename = specified_infile
else:
	infilename = DEFAULT_INFILE

try:
	reader = csv.reader(open(infilename, 'rU'), dialect=csv.excel_tab)
except IOError:
	print "I/O Error, likely no such infile"
	sys.exit(0)

# Doing outfile
if(specified_outfile != ""):
	outfilename = specified_outfile
else:	
	outfilename = DEFAULT_OUTFILE+infilename

try:
	writer = csv.writer(open(outfilename, 'wb'))	
except IOError:
	print "I/O Error opening writer file. Exiting."
	sys.exit(0)
	
reader_list = []
reader_list.extend(reader)
i = 0

# Main part of logical code
for row in reader_list:
	rowreader = csv.reader(row)
	rowlist = rowreader.next()
	towrite = ""
	
	# doing header row
	if(i == 0):
		rowlist.insert(NEW_POPULATION_LOCATION + 1, "rural_popularion_revised")
		towrite = rowlist
	else:
		#towrite = combinePopulation(row)
		checkForDuplicates(rowlist, reader_list)
		
	#writer.writerow(towrite)	
	i = i+1
