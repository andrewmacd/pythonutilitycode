# file: mergecountydata.py
#
# purpose: merge data from chinadataonline.org and census county data
#
# created by: Andrew MacDonald on 5/31/11.
#
# copyright: (c) 2016 Andrew MacDonald. All rights reserved.
# email: andrewwm@gmail.com

import csv 
import sys

####
#### GLOBAL VARIABLES
####

STATAFILE = "statamerge.csv"
COUNTYFILE = "counties1979-2007.csv"
NOT_FOUND = 0
OUT_FILE = "mergeddata.csv"
OUT_FILE_ALL = "mergedata-all.csv"
COUNTY_HEADERS = ['Year', 'Province ID', 'Province', 'District', 'DistrictID', 'Number of Towns(unit)', 'Number of Villagers Committees(unit)', 'Area of Administrative Region(10000sq.km)', 'Total Agricultural Machinery Power(10000 kw)', 'Number of Local Telephone Subscribers(10000 subscribers)', 'Electricity Amount Used in Rural Area(100 million kwh)', 'Number of Households at Year-end(household)', 'Of which: Number of Households(household)', 'Population at the Year-end(10000 persons)', 'Of which: Rural Population(10000 persons)', 'Number of Employed Persons at Year-end(10000 persons)', 'Number of Rural Labors(10000 persons)', 'Of which: Farming, Forestry, Animal Husbandry and Fishery(10000 persons)', 'GDP(100 million yuan)', 'Value-added of Primary Industry(100 million yuan)', 'Value-added of Secondary Industry(100 million yuan)', 'Industrial Value-added(100 million yuan)', 'GDP Index(%)', 'Annual Per Capita Net Income of Rural Households(yuan)', 'Local Government Revenue(100 million yuan)', 'Local Government Expenditure(100 million yuan)', 'Outstanding Amount of Savings Deposits of Urban Households(100 million yuan)', 'Outstanding Loan of Financial Institutes at Year-end(100 million yuan)', 'Grain Output(10000 tons)', 'Cotton Output(10000 tons)', 'Oilbearing Output(10000 tons)', 'Meat Output(10000 tons)', 'Number of Industrial Enterprises above Designated Size(unit)', 'Output of Industrial Enterprises above Designated Size (at current)(100 million yuan)', 'Completed Investment in Capital Construction(100 million yuan)', 'Exports Value(1,000 US dollars)', 'Foreign Capital Actually Used in This Year(USD 10000)', 'Contractual Foreign Investment(USD 10000)', 'Student Enrollment in Regular Secondary Schools(10000 persons)', 'Student Enrollment in Primary Schools(10000 persons)', 'Number of Beds in Hospitals and Sanitation Agencies(10000 units)', 'Number of Social Welfare Nursing Centers(unit)', 'Number of Beds in Social Welfare Nursing Centers(unit)']

COUNTY_ID = 3
COUNTY_YEAR = 0
COUNTY_NAME = 4
COUNTY_PROV_NAME = 2
COUNTY_MISSING_VALUE = -9999

STATA_ID = 3
STATA_YEAR = 1
STATA_NAME = 5
STATA_PROV_NAME = 3
STATA_COLUMNS = 248

####
#### FUNCTIONS
####

def findRecord(data, countyreader_list, found_counties):

	i = 0

	for row in countyreader_list:
		# avoiding header row
		if(i != 0):
			rowreader = csv.reader(row)
			rowlist = rowreader.next()
		
			# check to make sure year and ID are matching
			if(int(rowlist[COUNTY_ID]) == int(data[STATA_ID])):
				if(int(rowlist[COUNTY_YEAR]) == int(data[STATA_YEAR])):				
					found_counties.append(rowlist)
					return rowlist, found_counties
			
		i = i+1
					
	print "Didn't find entry"
	print "\t\tstata id is: " + data[STATA_ID] + "; stata year is: " + data[STATA_YEAR]

	return NOT_FOUND, found_counties

def concatRecords(county_record, stata_record):

	i = 0

	# changes the dumb NA that I had earlier for the county file to a more sensible one
	for datum in county_record:
		
		try:		
			if(int(datum) == COUNTY_MISSING_VALUE):
				county_record[i] = "" 
		except ValueError:
			# don't really care if it's a non int, just move one
			pass
		
		i = i+1

	# replace bogus name
	if(county_record[COUNTY_NAME] != ""):
		stata_record[STATA_NAME] = county_record[COUNTY_NAME]
		
	row = stata_record + county_record

	# add prov name to the beginning of the datarow
	row.insert(STATA_PROV_NAME, county_record[COUNTY_PROV_NAME])

	return row

def searchCountyfile(record, found_counties):
	
	for data in found_counties:
		if(data[COUNTY_ID] == record[COUNTY_ID]):
			if(data[COUNTY_YEAR] == record[COUNTY_YEAR]):
				return True
	
	return False

def prepCountyForWriting(record):
	
	emptyStata = []
	
	for i in range(STATA_COLUMNS):
		emptyStata.append("")
	
	return emptyStata + record

##########################################################
################### START OF MAIN CODE ###################
##########################################################

# check command line; sys.argv[0] is the name of the file, [1] is the first arg
try:
	print sys.argv[1]

	if(sys.argv[1] == "-a"):
		doall = True
	else:
		doall = False
except:
	doall = False

# open csv files
statareader = csv.reader(open(STATAFILE, 'rU'), dialect=csv.excel_tab)
countyreader = csv.reader(open(COUNTYFILE, 'rU'), dialect=csv.excel_tab)

if(doall == True):
	writer = csv.writer(open(OUT_FILE_ALL, 'wb'))
else:
	writer = csv.writer(open(OUT_FILE, 'wb'))

# there's something funky about the way stata/excel outputs the file. so we have to 
# dump everything into a  mega list and process it while doing the loops
statareader_list = []
countyreader_list = []

statareader_list.extend(statareader)
countyreader_list.extend(countyreader)

# keeps a list of matched counties, so that when we're done appending county data
# to 
found_counties = []

i = 0
n = 0

# Loops through all of the stata entries; for those with a matching county record, it concats the two
for row in statareader_list:
	rowreader = csv.reader(row)
	rowlist = rowreader.next()
	towrite = ""
	
	# doing header row
	if(i == 0):
		rowlist.insert(STATA_PROV_NAME, "provname")
		towrite = rowlist+COUNTY_HEADERS		
	else:
		foundRecord, found_counties = findRecord(rowlist, countyreader_list, found_counties)

		# if we have found the record, then concat and write it to file
		if(foundRecord != NOT_FOUND):
			towrite = concatRecords(foundRecord, rowlist)
		else:
			# blank row for counties if not found
			blank = [""] * len(COUNTY_HEADERS)
			towrite = concatRecords(blank, rowlist)
			
			n = n+1
	
	writer.writerow(towrite)
	i = i+1
	
print "i: " 
print i 
print "\n"
print "n: "
print n

# adding back all of the counties we didn't match to a stata record earlier
if(doall == True):	  

	i = 0

	for record in countyreader_list:
		wasFound = searchCountyfile(record, found_counties)
		
		if(wasFound == False):
			record = prepCountyForWriting(record)
			writer.writerow(record)

			i = i + 1
			
	print "num not found: " + i		
