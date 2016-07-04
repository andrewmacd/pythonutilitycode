# file: chinesedata.py
#
# purpose: grab one of several datasets from the AllChina Datacenter 
#
# created by: Andrew MacDonald on 11/24/08.
#
# copyright: (c) 2008, 2009, 2010, 2013 Andrew MacDonald. All rights reserved.
# email: andrewm@stanfordalumni.org


import csv
import httplib
httplib.HTTPConnection.debuglevel = 1                             
import urllib
import urllib2
import os.path
import cookielib
import time
import re
import getopt, sys
from bs4 import BeautifulSoup

####
#### GLOBAL VARIABLES
####

##
## INTERNET VARIABLES
##

# cookiejar variables
cj = None
COOKIEFILE = 'cookies.lwp'

# url to start the session
LOGIN_URL = 'http://chinadataonline.org'

# The string we get when login doesn't work - we are merely guests, not our university name
# note the double backslash because python gives a special meaning to \s; to make python
# understand we mean the regular expression \s, you have to preface it with an extra \
# 
LOGIN_FAIL = 'Welcome\\s*<font color="yellow">Guest</font>'

# base url to get county data
BASE_URL = 'http://chinadataonline.org/member/'

# fake a user agent, the website may not like automated exploration
TX_HEADERS =  {'User-agent' : 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4'}

# amount of time to wait after failure to open a page or login, so as not to overload the server
WAIT_TIME = 30

# number of times we try a server after failure before giving up
NUM_SERVER_TRIES = 3

# this specifies the ordering on the page of the dropdown menus
PROVINCE_DD = 0
SUBUNIT_DD = 1

##
## DATA VARIABLES
##

# missing value code for our data
MISSING_VALUE = "NA"

##
## DATASET VARIABLES
##

#
# COUNTY VARIABLES
#

COUNTY_DATASET = "county"

# array of county page codes
COUNTY_PAGES = ['A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A10', 'A11']
# headers of the data columns
COUNTY_HEADERS = ['Year', 'Province ID', 'Province', 'District', 'DistrictID', 'Number of Towns(unit)', 'Number of Villagers Committees(unit)', 'Area of Administrative Region(10000sq.km)', 'Total Agricultural Machinery Power(10000 kw)', 'Number of Local Telephone Subscribers(10000 subscribers)', 'Electricity Amount Used in Rural Area(100 million kwh)', 'Number of Households at Year-end(household)', 'Of which: Number of Households(household)', 'Population at the Year-end(10000 persons)', 'Of which: Rural Population(10000 persons)', 'Number of Employed Persons at Year-end(10000 persons)', 'Number of Rural Labors(10000 persons)', 'Of which: Farming, Forestry, Animal Husbandry and Fishery(10000 persons)', 'GDP(100 million yuan)', 'Value-added of Primary Industry(100 million yuan)', 'Value-added of Secondary Industry(100 million yuan)', 'Industrial Value-added(100 million yuan)', 'GDP Index(%)', 'Annual Per Capita Net Income of Rural Households(yuan)', 'Local Government Revenue(100 million yuan)', 'Local Government Expenditure(100 million yuan)', 'Outstanding Amount of Savings Deposits of Urban Households(100 million yuan)', 'Outstanding Loan of Financial Institutes at Year-end(100 million yuan)', 'Grain Output(10000 tons)', 'Cotton Output(10000 tons)', 'Oilbearing Output(10000 tons)', 'Meat Output(10000 tons)', 'Number of Industrial Enterprises above Designated Size(unit)', 'Output of Industrial Enterprises above Designated Size (at current)(100 million yuan)', 'Completed Investment in Capital Construction(100 million yuan)', 'Exports Value(1,000 US dollars)', 'Foreign Capital Actually Used in This Year(USD 10000)', 'Contractual Foreign Investment(USD 10000)', 'Student Enrollment in Regular Secondary Schools(10000 persons)', 'Student Enrollment in Primary Schools(10000 persons)', 'Number of Beds in Hospitals and Sanitation Agencies(10000 units)', 'Number of Social Welfare Nursing Centers(unit)', 'Number of Beds in Social Welfare Nursing Centers(unit)']
# url specifying the county pages
COUNTY_BASE_URL = 'county/countytshow.asp'
# number of left-hand side array variables that will be spliced on a the end
COUNTY_NUM_HEADER_VARIABLES = 3

#
# NATIONAL VARIABLES
#

NATIONAL_DATASET = "national"

# array of national page codes
NATIONAL_PAGES = ['A0101', 'A0102', 'A0103', 'A0104', 'A0201', 'A0202', 'A0301', 'A0302', 'A0401', 'A0402', 'A0501', 'A0502', 'A0503', 'A0504', 'A0601', 'A0603', 'A0604', 'A0607', 'A0608', 'A0609', 'A0610', 'A0611', 'A0612', 'A0613', 'A0616', 'A0617', 'A0619', 'A0701', 'A0801', 'A0802', 'A0803', 'A0804', 'A0805', 'A0901', 'A0902', 'A0903', 'A0904', 'A1001', 'A1002', 'A1101', 'A1102', 'A1103', 'A1104', 'A1105', 'A1106', 'A1107', 'A1108', 'A1109', 'A1110', 'A1111', 'A1112', 'A1113', 'A1201', 'A1202', 'A1301', 'A1302', 'A1303', 'A1304', 'A1305', 'A1306', 'A1307', 'A1308', 'A1309', 'A1401', 'A1402', 'A1403', 'A1404', 'A1405', 'A1406', 'A1408', 'A1410', 'A1412', 'A1414', 'A1416', 'A1418', 'A1419', 'A1420', 'A1421', 'A1422', 'A1423', 'A1424', 'A1501', 'A1502', 'A1503', 'A1504', 'A1601']
NATIONAL_HEADERS = ['Year', 'Gross National Product(100 million yuan)', 'Gross Domestic Product(100 million yuan)', 'Gross Domestic Product - Primary Industry(100 million yuan)', 'Gross Domestic Product - Secondary Industry(100 million yuan)', 'Gross Domestic Product - Secondary Industry - Industry(100 million yuan)', 'Gross Domestic Product - Secondary Industry - Construction(100 million yuan)', 'Gross Domestic Product - Tertiary Industry(100 million yuan)', 'Gross Domestic Product - Tertiary Industry - Transportation Post and Telecommunications(100 million yuan)', 'Gross Domestic Product - Tertiary Industry - Wholesale Retail and Catering(100 million yuan)', 'Per Capita GDP(yuan person)', 'Gross National Product(%)', 'Gross Domestic Product(%)', 'Gross Domestic Product - Primary Industry(%)', 'Gross Domestic Product - Secondary Industry(%)', 'Gross Domestic Product - Secondary Industry - Industry(%)', 'Gross Domestic Product - Secondary Industry - Construction(%)', 'Gross Domestic Product - Tertiary Industry(%)', 'Gross Domestic Product - Tertiary Industry - Transportation Post and Telecommunications(%)', 'Gross Domestic Product - Tertiary Industry - Wholesale Retail and Trade(%)', 'Per Capita GDP(%)', 'Gross National Product(growth)', 'Gross Domestic Product(growth)', 'Gross Domestic Product - Primary Industry(growth)', 'Gross Domestic Product - Secondary Industry(growth)', 'Gross Domestic Product - Secondary Industry - Industry(growth)', 'Gross Domestic Product - Secondary Industry - Construction(growth)', 'Gross Domestic Product - Tertiary Industry(growth)', 'Gross Domestic Product - Tertiary Industry - Transportation Post and Telecommunications(growth)', 'Gross Domestic Product - Tertiary Industry - Wholesale Retail and Trade(growth)', 'Per Capita GDP(growth)', 'Gross Domestic Product by Expenditure Approach(100 million yuan)', 'Gross Domestic Product by Expenditure Approach - Final Consumption Expenditure(100 million yuan)', 'Gross Domestic Product by Expenditure Approach - Final Consumption Expenditure - Household(100 million yuan)', 'Gross Domestic Product by Expenditure Approach - Final Consumption Expenditure - Government(100 million yuan)', 'Gross Domestic Product by Expenditure Approach - Gross Capital Formation(100 million yuan)', 'Gross Domestic Product by Expenditure Approach - Gross Capital Formation - Fixed Capital(100 million yuan)', 'Gross Domestic Product by Expenditure Approach - Gross Capital Formation - Changes in Inventories(100 million yuan)', 'Gross Domestic Product by Expenditure Approach - Net Exports of Goods and Services(100 million yuan)', 'Total Permanent Population(year-end)(10000 persons)', 'Total Permanent Population - Male(year-end)(10000 persons)', 'Total Permanent Population - Female(year-end)(10000 persons)', 'Total Permanent Population - Urban Areas(year-end)(10000 persons)', 'Total Permanent Population - Rural Areas(year-end)(10000 persons)', 'Total Household registed Population(year-end)(10000 persons)', 'Total Household registed Population - Male(year-end)(10000 persons)', 'Total Household registed Population - Female(year-end)(10000 persons)', 'Total Household registed Population - Agriculture(year-end)(10000 persons)', 'Total Household registed Population - non-Agriculture(year-end)(10000 persons)', 'Birth Rate(e)', 'Death Rate(e)', 'Natural Growth Rate(e)', 'Total Number of Employed Persons(10000 persons)', 'Total Number of Employed Persons - Urban(10000 persons)', 'Total Number of Employed Persons - Rural(10000 persons)', 'Total Number of Employed Persons - Primary Industry(10000 persons)', 'Total Number of Employed Persons - Secondary Industry(10000 persons)', 'Total Number of Employed Persons - Tertiary Industry(10000 persons)', 'Staff and Workers(10000 persons)', 'Staff and Workers - State Owned(10000 persons)', 'Staff and Workers - Urban Collective Owned Units(10000 persons)', 'Staff and Workers - Other Ownership Units(10000 persons)', 'Total Investmentin Fixed Assets(100 million yuan)', 'Total Investmentin Fixed Assets - State Owned Units(100 million yuan)', 'Total Investmentin Fixed Assets - Collective Owned Units(100 million yuan)', 'Total Investmentin Fixed Assets - Individuals(100 million yuan)', 'Floor Space of Buildings - Under Construction(10000 sq.m)', 'Floor Space of Buildings - Completed(10000 sq.m)', 'Floor Space of Commercial House Actually Sold(10000 sq.m)', 'Floor Spaceof Commercial House Actually Sold - Residential Buildings(10000 sq.m)', 'Commercial House Purchased by Individuals(10000 sq.m)', 'Total Sales of Commercial House(100 million yuan)', ' General Retail Price Index(1978=100)(%)', 'General Consumer Price Index(1985=100)(%)', 'Consumer Price Index Urban Area(1985=100)(%)', 'Consumer Price Index - Rural Area(1985=100)(%)', 'Ex-factory Price Indices of Industrial Products(1985=100)(%)', 'Purchasing Price Indices of Raw Material,Fuel and Power (1990=100)(%)', 'General Retail Price Index(%)', 'General Consumer Price Index(%)', 'Consumer Price Index - Urban Area(%)', 'Consumer Price Index - Rural Area(%)', 'Purchasing Price Indices of Raw Material Fuel and Power(%)', 'Investment in Fixed Assets Price Index(%)', 'Urban Households - Per Capita Annual Disposable Income(yuan)', 'Urban Households - Per Capital Annual Disposable Income Index(%)', 'Urban Households - Living Expenditure(yuan)', 'Urban Households - Living Expenditure - Food(yuan)', 'Rural Households - Net Income(yuan)', 'Rural Households - Net Income Index(%)', 'Rural Households - Living Expenditure(yuan)', 'Rural Households - Living Expenditure - Food(yuan)', 'Household Consumption - Value - All Households(yuan)', 'Household Consumption - Value - Rural Households(yuan)', 'Household Consumption - Value - Urban Households(yuan)', 'Household Consumption - Index - All Households(%)', 'Household Consumption - Index - Rural Households(%)', 'Household Consumption - Index - Urban Households(%)', 'Household Consumption - Index - All Households(%)', 'Household Consumption - Index - Rural Households(%)', 'Household Consumption - Index - Urban Households(%)', 'Urban - Per Capita Using Space(sq.m)', 'Urban - Per Capita Living Space(sq.m)', 'Per Capita Living Spacein Rural(sq.m)', 'Total Outstading Amount of Savings Deposit(100 million yuan)', 'Fixed Deposits(100 million yuan)', 'Current Deposits(100 million yuan)', 'Total Wages(100 million yuan)', 'Total Wages - State-owned Units(100 million yuan)', 'Total Wages - Urban Colletive-owned Units(100 million yuan)', 'Total Wages - Other Units(100 million yuan)', 'Total Wages - Index - Total(%)', 'Total Wages - Index - State-owned Units(%)', 'Total Wages - Index - Urban Colletive-owned Units(%)', 'Total Wages - Index - Other Units(%)', 'Total Revenue(100 million yuan)', 'Total Expenditures(100 million yuan)', 'Government Revenue Increase Rates(%)', 'Government Expenditure Increase Rates(%)', 'Total Tax Revenue(100 million yuan)', 'Value-added Tax(100 million yuan)', 'Business Tax(100 million yuan)', 'Consumption Tax(100 million yuan)', 'Tariffs(100 million yuan)', 'Agricultural and Related Tax(100 million yuan)', 'Expenditures for Capital Construction(100 million yuan)', 'Additional Appropriation for Circulating Capital of Enterprises(100 million yuan)', 'Innovation Fundsand Science and Technology Promotion Funds(100 million yuan)', 'GeologicalProspecting Expenses(100 million yuan)', 'Operating Expenses of Industrial Transportation and Commercial Departments(100 million yuan)', 'Expenditure for Supporting Agricultural Production and Agricultural Operating Expenses(100 million yuan)', 'Operating Expenses for Culture Education Science & Health Care(100 million yuan)', 'Pensions Social and Relief Funds(100 million yuan)', 'Expenditure for National Defense(100 million yuan)', 'Expenditure for Government Administration(100 million yuan)', 'Price Subsidies(100 million yuan)', 'Total Debt Payments(100 million yuan)', 'Expenditure on Scientific Research(100 million yuan)', 'Expenditure on Scientific Research - Expense on S&T Promotion(100 million yuan)', 'Expenditure on Scientific Research - Operating Expenses for Sciences(100 million yuan)', 'Expenditure on Scientific Research - Expenses for Capital Construction of S&T Institutes(100 million yuan)', 'Expenditure on Scientific Research - Other S&T Operating Expenses(100 million yuan)', 'Government Expenditure for Agriculture(100 million yuan)', 'Expenditure for Supporting Agricultural Production and Agricultural Operating Expenses(100 million yuan)', 'Government Expenditure for Agriculture - Expenditure for Capital Construction(100 million yuan)', 'Government Expenditure for Agriculture - Science & Technology Promotion Funds(100 million yuan)', 'Government Expenditure for Agriculture - Rural Relief Funds(100 million yuan)', 'Government Expenditure for Pensions and Social Welfare(100 million yuan)', 'Pension for Handicapped and Bereaved Families(100 million yuan)', 'Pension for Retirees(100 million yuan)', 'Social Welfare and Relief Funds(100 million yuan)', 'Expenses on Disaster Relief(100 million yuan)', 'Government Expenditure for Pensions and Social Welfare - Others(100 million yuan)', 'Government Revenue(100 million yuan)', 'Government Revenue - Central Government(100 million yuan)', 'Government Revenue - Local Government(100 million yuan)', 'Government Extra-Budgetary Revenue(100 million yuan)', 'Government Extra-Budgetary Revenue - Central Government(100 million yuan)', 'Government Extra-Budgetary Revenue - Local Government(100 million yuan)', 'Government Expenses(100 million yuan)', 'Government Expenses - Central Government(100 million yuan)', 'Government Expenses - Local Government(100 million yuan)', 'Government Extra-Budgetary Expenses(100 million yuan)', 'Government Extra-Budgetary Expenses - Central Government(100 million yuan)', 'Government Extra-Budgetary Expenses - Local Government(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - All Sources(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Deposits(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Deposits - Deposits of Enterprises(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Deposits - Treasury Deposits(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Deposits - Deposits of Government Agencies and Organizations(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Deposits - Urban and Rural Savings Deposits(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Deposits - Agricultural Deposits(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Deposits - Other Deposits(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Bonds(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Liabilities to International Financial Institutions(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Currency in Circulation(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Sources of Funds - Others(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - All Uses(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Loans(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Loans - Industrial Loans(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Loans - Commercial Loans(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Loans - Loans to Private & Urban Collective Enterprises(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Loans - Agricultural Loans(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Loans - Medium-term & Long-term Loans(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Loans - Loans to Sino-Foreign Joint Venture & Cooperative Enterprises(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Loans - Other Loans(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Securities and Investment(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Purchase of Gold & Silver(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Purchase of Foreign Exchanges(100 million yuan)', 'Credit Funds Balance Sheet of State Banks - Uses of Funds - Assets in International Financial Institutions(100 million yuan)', 'Cash Statistics of Financial Institutions - Cash Income(100 million yuan)', 'Cash Statistics of Financial Institutions - Cash Expenditures(100 million yuan)', 'Cash Statistics of Financial Institutions - Currency Issuance(100 million yuan)', 'Gold Reserve(10000 fine troy ounce)', 'Foreign Exchange Reserve(USD 100 million)', 'Balance of Payments - Current Account(USD 10000)', 'Balance of Payments - Current Account - Goods(USD 10000)', 'Balance of Payments - Current Account - Goods - Exports(USD 10000)', 'Balance of Payments - Current Account - Goods - Imports(USD 10000)', 'Balance of Payments - Service(USD 10000)', 'Balance of Payments - Service - Transportation(USD 10000)', 'Balance of Payments - Service - Tourism(USD 10000)', 'Balance of Payments - Service - Communication Service(USD 10000)', 'Balance of Payments - Service - Construction Service(USD 10000)', 'Balance of Payments - Service - Insurance Service(USD 10000)', 'Balance of Payments - Service - Financial Service(USD 10000)', 'Balance of Payments - Service - Computer and Information Service(USD 10000)', 'Balance of Payments - Service - Fee for Patent or Royalty(USD 10000)', 'Balance of Payments - Service - Consultation(USD 10000)', 'Balance of Payments - Service - Advertisement and Publicity(USD 10000)', 'Balance of Payments - Service - Movies and Audio-video Products(USD 10000)', 'Balance of Payments - Service - Other Comercial Service(USD 10000)', 'Balance of Payments - Service - Government Service not Elsewhere Classified(USD 10000)', 'Balance of Payments - Income and Profit(USD 10000)', 'Balance of Payments - Income and Profit - Compensation of Staff and Workers(USD 10000)', 'Balance of Payments - Income and Profit - Profit from Investment(USD 10000)', ' Balance of Payments - Current Transfer(USD 10000)', 'Balance of Payments - Current Transfer - Governments(USD 10000)', 'Balance of Payments - Current Transfer - Other Departments(USD 10000)', 'Balance of Payments - Capital and Finance Account(USD 10000)', 'Balance of Payments - Capital and Finance Account - Capital Account(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Direct Investments(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Direct Investments - Chinese Direct Investments Abroad(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Direct Investments - Foreign Direct Investment in China(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Securities(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Securities - Assets(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Securities - Assets - Capital Securities(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Securities - Assets - Debt Securities(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Securities - Liabilities(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Securities - Liabilities - Capital Securities(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Securities - Liabilities - Debt Securities(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Assets(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Assets - Trade Credit(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Assets - Loans(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Assets - Currencies and Deposits(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Assets - Other Assets(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Liabilities(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Liabilities - Trade Credit(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Liabilities - Loans(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Liabilities - Currencies and Deposits(USD 10000)', 'Balance of Payments - Capital and Finance Account - Financial Account - Other Investments - Liabilities - Other Liabilities(USD 10000)', 'Balance of Payments - Net Error and Omission(USD 10000)', 'Balance of Payments - Change in Reserve Assets(USD 10000)', 'Balance of Payments - Change in Reserve Assets - Gold Reserves(USD 10000)', 'Balance of Payments - Change in Reserve Assets - Foreign Exchange(USD 10000)', 'Balance of Payments - Change in Reserve Assets - SDR (Special Drawing Rights)(USD 10000)', 'Balance of Payments - Change in Reserve Assets - Chinas Reserve in IMF (International Monetary Fund)(USD 10000)', 'Production Capacity of Tap Water(10000tons-day)', 'Length of Water Supply Pipelines(km)', 'Total Annual Volume of Water Supply(100 million tons)', 'Total Annual Volume of Water Supply - For Residential Use(100 million tons)', 'Total Annual Volume of Water Supply - For Productive Use(100 million tons)', 'Per cpita Daily Consumption of Tap Water for Residential Use(ton)', 'Number of Public Transportation Vehicles(unit)', 'Number of Public Transportation Vehicles - Buses(unit)', 'Number of Public Transportation Vehicles - Trolley(unit)', 'Number of Public Transportation Vehicles - Subways(unit)', 'Number of Passengers Carried(10000 person-times)', 'Number of Taxis(unit)', 'Production Capacity of Coal Gas(10000tons-day)', 'Length of Gas Pipelines - CoalGas(km)', 'Length of Gas Pipelines - Natural Gas(km)', 'Total Gas Supply - Coal Gas(100 million cu.m)', 'Total Gas Supply - Liquefied Petroleum Gas(10000 tons)', 'Total Gas Supply - Natural Gas(100 million cu.m)', 'Roads - Length of Paved Roads(10000 km)', 'Roads - Area of Paved Roads(10000 sq.m)', 'Number of Bridges(unit)', 'Sewer Pipelines(10000 km)', 'Daily Disposal Capacity of Sewage(10000 sq.m)', 'Number of Street Lights(unit)', 'Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Total(100 million yuan)', 'Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Farming(100 million yuan)', 'Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Forestry(100 million yuan)', 'Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Animal Husbandry(100 million yuan)', 'Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Fishery(100 million yuan)', 'Indices of Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Total(%)', 'Indices of Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Farming(%)', 'Indices of Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Forestry(%)', 'Indices of Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Animal Husbandry(%)', 'Indices of Gross Output Value of Farming Forestry Animal Husbandry and Fishery - Fishery(%)', 'Cultivated Area(1000 hectares)', 'Total Sown Area(1000 hectares)', 'Total Sown Area - Grain Crops(1000 hectares)', 'Total Power of Agricultural Machinery(10000 kw)', 'Irrigated Area(1000 hectares)', 'Consumption of Chemical Fertilizers(10000 tons)', 'Electricity Consumed in Rural Area(100 million kwh)', 'Grain(10000 tons)', 'Cotton Crops(10000 tons)', 'Oil-Bearing Crops(10000 tons)', 'Jute andAmbary Hemp(10000 tons)', 'Sugar(10000 tons)', 'Tea(10000 tons)', 'Fruits(10000 tons)', 'Large Animals(year-end)(10000 heads)', 'Hogs(year-end)(10000 heads)', 'Sheep and Goats(year-end)(10000 heads)', 'Output of Meat(10000 tons)', 'Output of Meat - Pork Beef and Mutton(10000 tons)', 'Total Aquatic Products(10000 tons)', 'Total Aquatic Products - Seawater Aquatic Products(10000 tons)', 'Total Aquatic Products - Freshwater Aquatic Products(10000 tons)', 'Natural Disasters of China - Areas Covered(1000 hectares)', 'Natural Disasters of China - Areas Affected(1000 hectares)', 'Natural Disasters of China - Flood - Areas Covered(1000 hectares)', 'Natural Disasters of China - Flood - Areas Affected(1000 hectares)', 'Natural Disasters of China - Drought - Areas Covered(1000 hectares)', 'Natural Disasters of China - Drought - Areas Affected(1000 hectares)', 'Number of Industrial Enterprises(unit)', 'Number of Industrial Enterprises(unit) - State-owned(unit)', 'Number of Industrial Enterprises(unit) - Collective-owned(unit)', 'Gross Industrial Output Value(100 million yuan)', 'Gross Industrial Output Value - State-owned(100 million yuan)', 'Gross Industrial Output Value - Collective-owned(100 million yuan)', 'Indices of Gross Industrial Output Value(1952=100)(%)', 'Indices of Gross Industrial Output Value(1952=100) - State-owned(%)', 'Indices of Gross Industrial Output Value(1952=100) - Collective-owned(%)', 'Indices of Gross Industrial Output Value(Preceding year=100)(%)', 'Indices of Gross Industrial Output Value(Preceding year=100) - State-owned(%)', 'Indices of Gross Industrial Output Value(Preceding year=100) - Collective-owned(%)', 'Value of Light Industry(100 million yuan)', 'Value of Heavy Industry(100 million yuan)', 'Indices of Light Industry(%)', 'Indicies of Heavy Industry(%)', 'Chemical Fiber(10000 tons)', 'Yarn(10000 tons)', 'Cloth(100 million m)', 'Woolen(10000 m)', 'Silk(tons)', 'Paper and Paperboards(10000 tons)', 'Sugar(10000 tons)', 'Salt(10000 tons)', 'Edible Vegetable Oil(10000 tons)', 'Beer(10000 kl(year:10000 tons))', 'Cigarettes(100 million unit)', 'Household Refrigerators(10000 sets)', 'Electric Fan(10000 sets)', 'Household Washing Machines(10000 sets)', 'Color TV Sets(10000 sets)', 'Cameras(10000 sets)', 'Coal(10000 tons)', 'Crude Oil(10000 tons)', 'Natural Gas(100000000 cu.m)', 'Electricity(100 million kwh)', 'Electricity - Hydro-power(100 million kwh)', 'Pig Iron(10000 tons)', 'Steel(10000 tons)', 'Steel Products(10000 tons)', 'Cement(10000 tons)', 'Plate Glass(10000 weight cases)', 'Sulfuric Acid(10000 tons)', 'Chemical Fertilizer(10000 tons)', 'Chemical Pesticide(10000 tons)', 'Metal- Cutting Machine Tools(10000 sets)', 'Motor Vehicles(10000 units)', 'Number of Construction Enterprises(unit)', 'Number of Construction Enterprises - State-owned(unit)', 'Number of Construction Enterprises - Urban Collective-owned(unit)', 'Number of Construction Enterprises - Rural Construction Teams(unit)', 'Number of Persons Engaged in Construction(10000 persons)', 'Number of Persons Engaged in Construction - State-owned(10000 persons)', 'Number of Persons Engaged in Construction - Urban Collective-owned(10000 persons)', 'Number of Persons Engaged in Construction - Rural Construction Teams(10000 persons)', 'Gross Output Value of Construction(100 million yuan)', 'Gross Output Value of Construction - State-owned(100 million yuan)', 'Gross Output Value of Construction - Urban Collective-owned(100 million yuan)', 'Gross Output Value of Construction - Rural Construction Teams(100 million yuan)', 'Floor Space Under Construction(10000 sq.m)', 'Floor Space Completed(10000 sq.m)', 'Length of Railways in Operation(10000 km)', 'National Electrical Railways(10000 km)', 'Length of Highways(10000 km)', 'Length of Navigable Inland Waterways(10000 km)', 'Length of Civil Avaition Routes(10000 km)', 'Length of Civil Avaition Routes - International(10000 km)', 'Length of Pipelines(10000 km)', 'Total Passenger Traffic(10000 persons)', 'Railways(10000 persons)', 'Railways - National Railways(10000 persons)', 'Railways - Local Railways(10000 persons)', 'Highways(10000 persons)', 'Waterways(10000 persons)', 'Civil Avaition(10000 persons)', 'Total Turnover Value of Passenger Traffic(100 million passenger-km)', 'Railways(100 million passenger-km)', 'Railways - National Railways(100 million passenger-km)', 'Railways - Local Railways(100 million passenger-km)', 'Highways(100 million passenger-km)', 'Waterways(100 million passenger-km)', 'Civil Avaition(100 million passenger-km)', 'Total Freight Traffic(10000 tons)', 'Railways(10000 tons)', 'Railways - National Railways(10000 tons)', 'Railways - Local Railways(10000 tons)', 'Highways(10000 tons)', 'Waterways(10000 tons)', 'Civil Aviation(10000 tons)', 'Petroleum and Gas(10000 tons)', 'Total Turnover Volume of Freight Traffic(100 million ton-km)', 'Railways(100 million ton-km)', 'Railways - National Railways(100 million ton-km)', 'Railways - Local Railways(100 million ton-km)', 'Highways(100 million ton-km)', 'Waterways(100 million ton-km)', 'Civil Aviation(100 million ton-km)', 'Petroleum and Gas(100 million ton-km)', 'Total Average Transport Distance of Passengers(km)', 'Railways(km)', 'Highways(km)', 'Waterways(km)', 'Civil Avaition(km)', 'Total Average Transport Distance of Freight(km)', 'Average Freight Distance - Railways(km)', 'Average Freight Distance - Highways(km)', 'Average Freight Distance - Waterways(km)', 'Average Freight Distance - Pipelines(km)', 'Average Freight Distance - Civil Aviation(km)', 'Total Daily Average Number of Freight Car Loadings(car)', 'Total Daily Average Number of Freight Car Loadings - Coal(car)', 'Total Daily Average Number of Freight Car Loadings - Petroleum(car)', 'Total Daily Average Number of Freight Car Loadings - Steel and Iron(car)', 'Total Daily Average Number of Freight Car Loadings - Mineral Builing Materials(car)', 'Total Daily Average Number of Freight Car Loadings - Grain(car)', 'Railway Traffic - Coal(10000 tons)', 'Railway Traffic - Petroleum(10000 tons)', 'Railway Traffic - Steel and Iron(10000 tons)', 'Railway Traffic - Mineral Building Materials(10000 tons)', 'Railway Traffic - Cement(10000 tons)', 'Railway Traffic - Timber(10000 tons)', 'Railway Traffic - Chemical Fertilizers and Pesticides(10000 tons)', 'Railway Traffic - Grain(10000 tons)', 'Total Number of Civil Motor Vehicles Owned(10000 units)', 'Total Number of Civil Motor Vehicles Owned - Buses and Cars(10000 units)', 'Total Number of Civil Motor Vehicles Owned - Trucks(10000 units)', 'Vehicles Owned by Departmentof Highway Transportation(10000 units)', 'Vehicles Owned by Departmentof Highway Transportation - Buses and Cars(10000 units)', 'Vehicles Owned by Departmentof Highway Transportation - Trucks(10000 units)', 'Private Vehicles(10000 units)', 'Private Vehicles - Buses and Cars(10000 units)', 'Private Vehicles - Trucks(10000 units)', 'Number of Post and Telecommunications Offices(unit)', 'Length of Postal Routes and Rural Delivery Routes(10000 km)', 'Length of Postal Routes and Rural Delivery Routes - Highway Routes(km)', 'Length of Postal Routes and Rural Delivery Routes - Railway Routes(km)', 'Long Distance Telephone Circuits(line)', 'Telegram Circuits(line)', 'Business Volume of Post and Telecommunication(100 million yuan)', 'Number of Letter(100 million pcs)', 'Number of Parcels(10000 pcs)', 'Newspapers and Magazines Circulation(10000 copies)', 'Number of Long Distance Telephone Calls(100 million times)', 'Number of Local Urban Telephone Subscribers(year-end)(subscribers)(10000 subscribers)', 'Number of Local Urban Telephone Subscribers - Residential Telephone Subscribers(10000 subscribers)', 'Capacity of Local Office Telephone Exchanges(10000 line)', 'Capacity of Local Office Telephone Exchanges - Central State-owned(10000 line)', 'Capacity of Local Office Telephone Exchanges - Local State-owned(10000 line)', 'Number of Telephone Sets(10000 units)', 'Number of Telephone Sets - Central State-owned(10000 units)', 'Number of Telephone Sets - Local State-owned(10000 units)', 'Total Retail Sales of Consumer Goods(100 million yuan)', 'Total Retail Sales of Consumer Goods - State-owned(100 million yuan)', 'Total Retail Sales of Consumer Goods - Collective Owned(100 million yuan)', 'Total Retail Sales of Consumer Goods - Joint Owned(100 million yuan)', 'Total Retail Sales of Consumer Goods - Individual(100 million yuan)', 'Total Retail Sales of Consumer Goods - Others(100 million yuan)', 'Total Retail Sales of Consumer Goods - by Sector(100 million yuan)', 'Total Retail Sales of Consumer Goods - Wholesale and Retail Sale Trades(100 million yuan)', 'Total Retail Sales of Consumer Goods - Catering Trade(100 million yuan)', 'Total Retail Sales of Consumer Goods - Others(100 million yuan)', 'Number of Contracts With Foreign Countries or Territories(unit)', 'Contracted Value With Foreign Countries or Territories(USD 100 million)', 'Value of Business Fulfilled With Foreign Countries or Territories(USD 10000)', 'Number of Contracts of Contracted Projects(unit)', 'Contracted Value of Contracted Projects(USD 100 million)', 'Value of Businness Fulfilled of Contracted Projects(USD 10000)', 'Number of Contracts of Contracted Projects - unknown type?(unit)', 'Contracted Value of Contracted Projects - unknown type?(USD 100 million)', 'Value of Businness Fulfilled of Contracted Projects - unknown type2?(USD 10000)', 'Number of Contracts of Contracted Projects - unknown type?(unit)', 'Contracted Value of Contracted Projects - unknown type2?(USD 100 million)', 'Value of Businness Fulfilled of Contracted Projects - unknown type2?(USD 10000)', 'Total Imports & Exports(100 million yuan)', 'Total Exports(RMB 100 million yuan)', 'Total Imports(RMB 100 million yuan)', 'Balance(RMB 100 million yuan)', 'Total Imports & Exports(1000 US dollars)', 'Total Exports(1000 US dollars)', 'Total Imports(1000 US dollars)', 'Balance(1000 US dollars)', 'Exports - Total(1000 US dollars)', 'Exports - Primary Goods(1000 US dollars)', 'Exports - Primary Goods - Food and Live Animals Used Chiefly for Food(1000 US dollars)', 'Exports - Primary Goods - Beverages and Tobacco(1000 US dollars)', 'Exports - Primary Goods - Non-Edible Raw Materials(1000 US dollars)', 'Exports - Primary Goods - Mineral Fuels Lubricants and Related Materials(1000 US dollars)', 'Exports - Primary Goods - Animal and Vegetable Oils Fats and Wax(1000 US dollars)', 'Exports - Manufactured Goods(1000 US dollars)', 'Exports - Manufactured Goods - Chemicals and Related Products(1000 US dollars)', 'Exports - Manufactured Goods - Light and Textile Industrial Products Rubber Products Minerals Metallurgical Products(1000 US dollars)', 'Exports - Manufactured Goods - Machinery and Transport Equipment(1000 US dollars)', 'Exports - Manufactured Goods - Miscellaneous Products(1000 US dollars)', 'Exports - Manufactured Goods - Products Not Otherwise Classified(1000 US dollars)', 'Imports - Total(1000 US dollars)', 'Imports - Primary Goods(1000 US dollars)', 'Imports - Primary Goods - Food and Live Animals Used Chiefly for Food(1000 US dollars)', 'Imports - Primary Goods - Beverages and Tobacco(1000 US dollars)', 'Imports - Primary Goods - Non-Edible Raw Materials(1000 US dollars)', 'Imports - Primary Goods - Mineral Fuels Lubricants and Related Materials(1000 US dollars)', 'Imports - Primary Goods - Animal and Vegetable Oils Fats and Wax(1000 US dollars)', 'Imports - Manufactured Goods(1000 US dollars)', 'Imports - Manufactured Goods - Chemicals and Related Products(1000 US dollars)', 'Imports - Manufactured Goods - Light and Textile Industrial Products Rubber Products Minerals Metallurgical Products(1000 US dollars)', 'Imports - Manufactured Goods - Machinery and Transport Equipment(1000 US dollars)', 'Imports - Manufactured Goods - Miscellaneous Products(1000 US dollars)', 'Imports - Manufactured Goods - Products Not Otherwise Classified(1000 US dollars)', 'Total Utilization of Foreign Capital - Number of Projects(unit)', 'Total Utilization of Foreign Capital - Value(USD 10000)', 'Foreign Loans - Number of Projects(unit)', 'Foreign Loans - Value(USD 10000)', 'Direct Foreign Investments - Number of Projects(unit)', 'Direct Foreign Investments - Value(USD 10000)', 'Total Utilization of Foreign Capital - Number of Projects(unit) - unknown type?', 'Total Utilization of Foreign Capital - Value(USD 10000) - unknown type?', 'Foreign Loans - Number of Projects - unknown type?(unit)', 'Foreign Loans - Value - unknown type?(USD 10000)', 'Direct Foreign Investments - Number of Projects - unknown type?(unit)', 'Direct Foreign Investments - Value - unknown type?(USD 10000)', 'Total Number of Schools(unit)', 'Number of Schools - Regular Institutions of Higher Education(unit)', 'Number of Schools - Secondary Schools(unit)', 'Number of Schools - Secondary Schools - Specialized Secondary Sechools(unit)', 'Number of Schools - Secondary Schools - Specialized Secondary Schools - Technical Schools(unit)', 'Number of Schools - Secondary Schools - Specialized Secondary Sechools - Teacher Training Schools(unit)', 'Number of Schools - Secondary Schools - Regular Secondary Schools(unit)', 'Number of Schools - Secondary Schools - Regular Secondary Schools - Senior(unit)', 'Number of Schools - Secondary Schools - Regular Secondary Schools - Junior(unit)', 'Number of Schools - Secondary Schools - Vocational Schools(unit)', 'Number of Schools - Primary Schools(unit)', 'Number of Schools - Kindergartens(unit)', 'Number of Schools - Special Schools(unit)', 'Total School Staff(10000 persons)', 'School Staff - Regular Institutions of Higher Education(10000 persons)', 'School Staff - Secondary Schools(10000 persons)', 'School Staff - Secondary Schools - Specialized Secondary Schools(10000 persons)', 'School Staff - Secondary Schools - Specialized Secondary Schools - Technical Schools(10000 persons)', 'School Staff - Secondary Schools - Specialized Secondary Sechools - Teacher Training Schools(10000 persons)', 'School Staff - Secondary Schools - Regular Secondary Schools(10000 persons)', 'School Staff - Secondary Schools - Vocational Schools(10000 persons)', 'School Staff - Primary Schools(10000 persons)', 'School Staff - Kindergartens(10000 persons)', 'School Staff - Special Schools(10000 persons)', 'Total Number of Teachers(10000 persons)', 'Number of Teachers - Regular Institutions of Higher Education(10000 persons)', 'Number of Teachers - Secondary Schools(10000 persons)', 'Number of Teachers - Secondary Schools - Specialized Secondary Schools(10000 persons)', 'Number of Teachers - Secondary Schools - Specialized Secondary Schools - Technical Schools(10000 persons)', 'Number of Teachers - Secondary Schools - Specialized Secondary Sechools - Teacher Training Schools(10000 persons)', 'Number of Teachers - Secondary Schools - Regular Secondary Schools(10000 persons)', 'Number of Teachers - Secondary Schools - Regular Secondary Schools - Senior(10000 persons)', 'Number of Teachers - Secondary Schools - Regular Secondary Schools - Junior(10000 persons)', 'Number of Teachers - Secondary Schools - Vocational Schools(10000 persons)', 'Number of Teachers - Primary Schools(10000 persons)', 'Number of Teachers - Kindergartens(10000 persons)', 'Number of Teachers - Special Schools(10000 persons)', 'Total Number of Enrolled Students(10000 persons)', 'Enrolled Students - Regular Institutions of Higher Education(10000 persons)', 'Enrolled Students - Secondary Schools(10000 persons)', 'Enrolled Students - Secondary Schools - Specialized Secondary Schools(10000 persons)', 'Enrolled Students - Secondary Schools - Specialized Secondary Schools - Technical Schools(10000 persons)', 'Enrolled Students - Secondary Schools - Specialized Secondary Sechools - Teacher Training Schools(10000 persons)', 'Enrolled Students - Secondary Schools - Regular Secondary Schools(10000 persons)', 'Enrolled Students - Secondary Schools - Regular Secondary Schools - Senior(10000 persons)', 'Enrolled Students - Secondary Schools - Regular Secondary Schools - Junior(10000 persons)', 'Enrolled Students - Secondary Schools - Vocational Schools(10000 persons)', 'Enrolled Students - Primary Schools(10000 persons)', 'Enrolled Students - Kindergartens(10000 persons)', 'Enrolled Students - Special Schools(10000 persons)', 'Total New Student Enrollment(10000 persons)', 'New Student Enrollment - Regular Institutions of Higher Education(10000 persons)', 'New Student Enrollment - Secondary Schools(10000 persons)', 'New Student Enrollment - Secondary Schools - Specialized Secondary Schools(10000 persons)', 'New Student Enrollment - Secondary Schools - Specialized Secondary Schools - Technical Schools(10000 persons)', 'New Student Enrollment - Secondary Schools - Specialized Secondary Sechools - Teacher Training Schools(10000 persons)', 'New Student Enrollment - Secondary Schools - Regular Secondary Schools(10000 persons)', 'New Student Enrollment - Secondary Schools - Regular Secondary Schools - Senior(10000 persons)', 'New Student Enrollment - Secondary Schools - Regular Secondary Schools - Junior(10000 persons)', 'New Student Enrollment - Secondary Schools - Vocational Schools(10000 persons)', 'New Student Enrollment - Primary Schools(10000 persons)', 'New Student Enrollment - Special Schools(10000 persons)', 'Total Number of Graduates(10000 persons)', 'Number of Graduates - Regular Institutions of Higher Education(10000 persons)', 'Number of Graduates - Secondary Schools(10000 persons)', 'Number of Graduates - Secondary Schools - Specialized Secondary Schools(10000 persons)', 'Number of Graduates - Secondary Schools - Specialized Secondary Schools - Technical Schools(10000 persons)', 'Number of Graduates - Secondary Schools - Specialized Secondary Sechools - Teacher Training Schools(10000 persons)', 'Number of Graduates - Secondary Schools - Regular Secondary Schools(10000 persons)', 'Number of Graduates - Secondary Schools - Regular Secondary Schools - Senior(10000 persons)', 'Number of Graduates - Secondary Schools - Regular Secondary Schools - Junior(10000 persons)', 'Number of Graduates - Secondary Schools - Vocational Schools(10000 persons)', 'Number of Graduates - Primary Schools(10000 persons)', 'Number of Graduates - Special Schools(10000 persons)', 'Higher Education Enrollment - Philosophy(10000 persons)', 'Higher Education Enrollment - Economics(10000 persons)', 'Higher Education Enrollment - Law(10000 persons)', 'Higher Education Enrollment - Education(10000 persons)', 'Higher Education Enrollment - Literature(10000 persons)', 'Higher Education Enrollment - History(10000 persons)', 'Higher Education Enrollment - Science(10000 persons)', 'Higher Education Enrollment - Engineering(10000 persons)', 'Higher Education Enrollment - Agriculture(10000 persons)', 'Higher Education Enrollment - Medicine(10000 persons)', 'New Student Enrollment - Philosophy(10000 persons)', 'New Student Enrollment - Economics(10000 persons)', 'New Student Enrollment - Law(10000 persons)', 'New Student Enrollment - Education(10000 persons)', 'New Student Enrollment - Literature(10000 persons)', 'New Student Enrollment - History(10000 persons)', 'New Student Enrollment - Science(10000 persons)', 'New Student Enrollment - Engineering(10000 persons)', 'New Student Enrollment - Agriculture(10000 persons)', 'New Student Enrollment - Medicine(10000 persons)', 'Graduates of Philosophy(10000 persons)', 'Graduates of Economics(10000 persons)', 'Graduates of Law(10000 persons)', 'Graduates of Education(10000 persons)', 'Graduates of Literature(10000 persons)', 'Graduates of History(10000 persons)', 'Graduates of Science(10000 persons)', 'Graduates of Engineering(10000 persons)', 'Graduates of Agriculture(10000 persons)', 'Graduates of Medicine(10000 persons)', 'Student Enrollment in Technical Schools - Engineering(10000 persons)', 'Student Enrollment in Technical Schools - Agriculture(10000 persons)', 'Student Enrollment in Technical Schools - Forestry(10000 persons)', 'Student Enrollment in Technical Schools - Medicine(10000 persons)', 'Student Enrollment in Technical Schools - Economics and Finance(10000 persons)', 'School Enrollment in Secondary Technical Schools - Politics and Law(10000 persons)', 'School Enrollment in Secondary Technical Schools - Physical(10000 persons)', 'School Enrollment in Secondary Technical Schools - Art(10000 persons)', 'School Enrollment in Secondary Technical Schools - Management(10000 persons)', 'School Enrollment - Teacher Training(10000 persons)', 'New Student Enrollment in Technical Schools - Engineering(10000 persons)', 'New Student Enrollment in Technical Schools - Agriculture(10000 persons)', 'New Student Enrollment in Technical Schools - Forestry(10000 persons)', 'New Student Enrollment in Technical Schools - Medicine(10000 persons)', 'New Student Enrollment in Technical Schools - Economics and Finance(10000 persons)', 'New School Enrollment in Secondary Technical Schools - Politics and Law(10000 persons)', 'New School Enrollment in Secondary Technical Schools - Physical(10000 persons)', 'New School Enrollment in Secondary Technical Schools - Art(10000 persons)', 'New School Enrollment in Secondary Technical Schools - Management(10000 persons)', 'New School Enrollment - Teacher Training(10000 persons)', 'Graduates of Technical Schools - Engineering(10000 persons)', 'Graduates of Technical Schools - Agriculture(10000 persons)', 'Graduates of Technical Schools - Forestry(10000 persons)', 'Graduates of Technical Schools - Medicine(10000 persons)', 'Graduates of Technical Schools - Economics and Finance(10000 persons)', 'Graduates of Secondary Technical Schools - Politics and Law(10000 persons)', 'Graduates of Secondary Technical Schools - Physical(10000 persons)', 'Graduates of Secondary Technical Schools - Art(10000 persons)', 'Graduates of Secondary Technical Schools - Management(10000 persons)', 'Graduates of Teacher Training(10000 persons)', 'Number of Postgraduates - Student Enrollment(10000 persons)', 'Number of Postgraduates - New Student Enrollment(10000 persons)', 'Number of Postgraduates - Graduates(10000 persons)', 'Number of Students Studying Abroad(10000 persons)', 'Number of Returned Students(10000 persons)', 'Percentage of Graduates of Junior Secondary Schools Entering Senior Secondary Schools(%)', 'Percentage of Graduates of Primary Secondary Schools Entering Junior Secondary Schools(%)', 'School-Age Children(10000 persons)', 'School-Age Children Enrolled in Schools(10000 persons)', 'Enrollment Rate(%)', 'Students as Percentage of Total Population(%)', 'Number of Students per 10000 Population - University and College Students(person)', 'Number of Students per 10000 Population - Secondary School Students(person)', 'Number of Students per 10000 Population - Primary School Students(person)', 'Student-Teacher Ratio - Regular Institutions of Higher Education(person)', 'Student-Teacher Ratio - Secondary Schools(person)', 'Student-Teacher Ratio - Secondary Schools - Specialized Secondary Schools(person)', 'Student-Teacher Ratio - Secondary Schools - Specialized Secondary Schools - Technical Schools(person)', 'Student-Teacher Ratio - Secondary Schools - Specialized Secondary Schools -Teacher Training Schools(person)', 'Student-Teacher Ratio - Secondary Schools - Regular Secondary Schools(person)', 'Student-Teacher Ratio - Secondary Schools - Regular Secondary Schools(person) - Senior(person)', 'Student-Teacher Ratio - Secondary Schools - Regular Secondary Schools(person) - Junior(person)', 'Student-Teacher Ratio - Secondary Schools - Vocational Schools(person)', 'Student-Teacher Ratio - Primary Schools(person)', 'Student-Teacher Ratio - Kindergartens(person)', 'Student-Teacher Ratio - Schools for the Blind Deaf and Deafmute(person)', 'Art Performance Troupes(unit)', 'Art Performance Plances(unit)', 'Cultural Centers(unit)', 'Public Libraries(unit)', 'Museums(unit)', 'Book Published - Number of Publications(kind)', 'Book Published - Number of Publications - New Publications(kind)', 'Book Published - Printed Copies(100 million copies)', 'Book Published - Printed Sheets(100 million sheets)', 'Magazines Published - Number of Publications(kind)', 'Magazines Published - Average Printed Copies per Issue(10000 copies)', 'Magazines Published - Total Printed Copies(100 million copies)', 'Magazines Published - Printed Sheets(100 million sheets)', 'Newspapers Published - Number of Newspapers Published(kind)', 'Newspapers Published - Average Printed Copies per Issue(10000 copies)', 'Newspapers Published - Total Printed Copies(100 million copies)', 'Newspapers Published - Printed Sheets(100 million sheets)', 'Number of Health Institutions - Total(unit)', 'Hospitals(unit)', 'Hospitals At and Above County Level(unit)', 'Sanatoriums(unit)', 'Clinics(unit)', 'Specialized Prevention & Treatment Centers & Stations(unit)', 'Sanitation and Antiepidemic Institutions(unit)', 'Maternity and Child Care Centers(unit)', 'Medicines and Chemical Reagent Test Labs(unit)', 'Research Institutes of Medical Science(unit)', 'Other Health Institutions(unit)', 'Number of Persons Engaged in Health Institutions - Total', 'Medical Technical Personnel(10000 persons)', 'Medical Technical Personnel - Doctors(10000 persons)', 'Medical Technical Personnel - Doctors - Doctors of Traditional Chinese Medicine(10000 persons)', 'Medical Technical Personnel - Doctors - Doctors of Western Medicine(10000 persons)', 'Medical Technical Personnel - Doctors - Paramedics of Western Medicine(10000 persons)', 'Medical Technical Personnel - Senior and Junior Nurses(10000 persons)', 'Number of Beds in Health Institutions - Total(10000 units)', 'Number of Beds in Health Institutions - Hospitals(10000 units)', 'Number of Beds in Health Institutions - Hospitals - At and Above County Level(10000 units)', 'Number of Beds in Health Institutions - Sanatoriums(10000 units)', 'Number of Beds in Health Institutions - Other Health Institutions(10000 units)', 'Hospital Beds - City(10000 units)', 'Hospital Beds - County(10000 units)', 'Medical Technical Personnel - City(10000 persons)', 'Medical Technical Personnel - City - Doctors(10000 persons)', 'Medical Technical Personnel - City - Senior and Junior Nurses(10000 persons)', 'Medical Technical Personnel - County(10000 persons)', 'Medical Technical Personnel - County - Doctors(10000 persons)', 'Medical Technical Personnel - County - Senior and Junior Nurses(10000 persons)', 'Area of Cultivated Land(10000 hectares)', 'Area of Undeveloped Land(10000 hectares)', 'Area of Afforestated Land(10000 hectares)', 'Grassland(10000 hectares)', 'Forest Area(10000 hectares)', 'Forest Coverage Rate(%)', 'Surface Water Volume(100 million cu.m)', 'Hydropower Resources(100 million kw)', 'Inland Water Area(10000 hectares)', 'Coastal Area(10000sq.km)', 'Cultivatable Area in Marine Areas(1000 hectares)']
NATIONAL_BASE_URL = 'macroy/macroytshow.asp'
NATIONAL_NUM_HEADER_VARIABLES = 1

#
# PREFECTURE VARIABLES
#

PREFECTURE_DATASET = "prefecture"

# array of prefecture page codes
PREFECTURE_PAGES = ['A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10', 'A12', 'A13', 'A14', 'A15', 'A16', 'A17', 'A18', 'A19', 'A20', 'A21', 'A22', 'A23', 'A24', 'A25', 'A26', 'A27']
PREFECTURE_HEADERS = ['Year', 'ProvinceID', 'Province', 'IsPrefectureTotal', 'IsProvinceTotal', 'Prefecture', 'PrefectureID', 'Total Population at year-end(10000 persons)', 'Non-agricultural Population(10000 persons)', 'Natural Growth Rate(e)', 'Number of Employees(10000 persons)', 'Number of Urban Registered Unemployees at Year-end(10000 persons)', 'Number of Employed Persons in Urban Private Enpterprises and Self-employed Individuals at the Year-end(10000 persons)', 'Proportion of Employees in Primary Industry(10000 persons)', 'Proportion of Employees in Secondary Industry(10000 persons)', 'Proportion of Employees in Tertiary Industry(10000 persons)', 'Number of Labors in Farming Forestry Animal Husbandry Fishery(10000 persons)', 'Mining and Quarrying(10000 persons)', 'Manufacturing(10000 persons)', 'Electric Power Gas and Water Production and Supply(10000 persons)', 'Construction(10000 persons)', 'Transportation Storage Post and Telecommunications(10000 persons)', 'Wholesale & Retail Trade(10000 persons)', 'Banking and Insurance(10000 persons)', 'Real Estate(10000 persons)', 'Social Services(10000 persons)', 'Public Management and Social Organization(10000 persons)', 'Scientific Research Technical Service and Geologic Prospecting(10000 persons)', 'Management of Water Conservancy Environment and Public Facilities(10000 persons)', 'Health Social Security and Social Welfare(10000 persons)', 'Land Area(10000 sq.km)', 'Land Area(Completed Construction Area)(sq.km)', 'Cultivated Land by Year-end(1000 hectares)', 'Park Garden and Green Area(10000 hectare)', 'Population Density(person per sq.km)', 'Per Capita Cultivated Land(hectare)', 'Coverage Rate of Green Area in Completed Construction Area(%)', 'Gross Domestic Product(100 million yuan)', 'Primary Industry Percentage(100 million yuan)', 'Secondary Industry Percentage(100 million yuan)', 'Tertiary Industry Percentage(100 million yuan)', 'GDP Index(%)', 'Per Capital of Gross Domestic Product(yuan person)', 'Yield of Major Farm Crops Vegetables(10000 tons)', 'Yield of Major Farm Crops Fruits(10000 tons)', 'Yield of Major Farm Products Total Aquatic Products(10000 tons)', 'Yield of Major Farm Crops Meat(10000 tons)', 'Yield of Major Farm Crops Milk(10000 tons)', 'Per Capita Yield of Aquatic(kg)', 'Per Capita Yield of Vegetables(kg)', 'Per Capita Yield of Milk(kg)', 'Per Capita Yield of Meat(kg)', 'Per Capita Yield of fruits(kg)', 'Gross Industrial Output Value of Enterprises above Designated Size(100 million yuan)', 'Number of Enterprises above Designated Size(unit)', 'Gross Industrial Output Value of Domestic-funded Enterprises(100 million yuan)', 'Gross Industrial Output Value of Enterprises Funded by Hongkong Macao and Taiwan Investors(100 million yuan)', 'Gross Industrial Output Value of Foreign-funded Enterprises(100 million yuan)', 'Average Annual Number of Employees(10000 persons)', 'Sales Revenue of Product(100 million yuan)', 'Total Pre-tex Profits(100 million yuan)', 'Value-added Tax Payable in This Year(100 million yuan)', 'Annual Average Balance of Net Value of Fixed Assets(100 million yuan)', 'Annual Average Balance of Flowing Assets(100 million yuan)', 'Investment in Fixed Assets(100 million yuan)', 'Investment in Residential Buildings(100 million yuan)', 'Investment in Real Estate Development(100 million yuan)', 'Sales Value in Wholesale and Retail Sale Trade(100 million yuan)', 'Total Retail Sales of Consumer Goods(100 million yuan)', 'Number of Corporation above Designated Size in Wholesale and Retail Trade(unit)', 'Number of Newly Signed Contracts(unit)', 'Total Foreign Capital from Signed Contracts(USD 10000)', 'Actually Utilized Foreign Capital(USD 10000)', 'Budgetary Revenue of Local Government(100 million yuan)', 'Budgetary Expenditure of Local Government(100 million yuan)', 'Expenditure for Science Administration(100 million yuan)', 'Expenditure for Education Administration(100 million yuan)', 'Deposit(100 million yuan)', 'Loan(100 million yuan)', 'Outstanding Amount of Savings Deposit of Urban and Rural Residents at Year-end(100 million yuan)', 'Average Wage of Staff and Workers(yuan)', 'Average Number of Employees(10000 persons)', 'Total Wage of Employees(100 million yuan)', 'Number of Institutions of Higher Education(unit)', 'Number of Regular Secondary Schools(unit)', 'Number of Primary Schools(unit)', 'Number of Full-time Teachers in Institutions of Higher Education(10000 persons)', 'Number of Full-time Teachers in Regular Secondary Schools(10000 persons)', 'Number of Full-time Teachers in Primary Schools(10000 persons)', 'Student Enrollment in Institutions of Higher Education(10000 persons)', 'Student Enrollment in Regular Secondary Schools(10000 persons)', 'Student Enrollment in Primary Schools(10000 persons)', 'Theaters and Music Halls(unit)', 'Public Library Collections(10000 volumes)', 'Number of Books in Public Libraries Per Capita(volume-person)', 'Number of Hospitals(unit)', 'Number of Beds in Hospitals(10000 units)', 'Number of Doctors(10000 persons)', 'Total Passenger Traffic(10000 persons)', 'Passenger Traffic by Railway(10000 persons)', 'Passenger Traffic by Highway(10000 persons)', 'Total Freight Traffic(100 million passenger-km)', 'Freight Traffic by Railway(100 million passenger-km)', 'Freight Traffic by Highway(100 million passenger-km)', 'Number of Post & Telecommunication Offices at Year-end(unit)', 'Postal Service Income(100 million yuan)', 'Telecommunication Service Income(100 million yuan)', 'Number of Local Telephone Users(10000 subscribers)', 'Annual Supply of Tap Water(100 million tons)', 'Per Capita Water Consumption for Living(ton)', 'Total Yearly Electricity Consumption(10000 kwh)', 'Per Capita Electricity Consumption for Living(kwh)', 'Household Consumption of Coal Gas(100 million cu.m)', 'Household Consumption of Liquefied Petrol Gas(10000 tons)', 'Area of Paved Roads by Year-end(10000 sq.m)', 'Area of paved Rodas Per Capita(sq.m)', 'Number of Public Transportation Vehicles by Year-end (Buses and Trolley Buses etc.)(unit)', 'Number of Public Transportation Vehicles Per 10,000 Persons(unit)', 'Number of Passengers Carried by Public Transportation Vehicles(10000 person-times)', 'Number of Cabs by Year-end(unit)', 'Industry Solid Waste Comprehensive Use Factor(%)', 'Volume of Sulphur Dioxide Exhausted(ton)', 'Proportion of Industrial Waste Water Discharge Qualifying Standard(%)']
PREFECTURE_BASE_URL = 'city/citytshow.asp'
# number of left-hand side array variables that will be spliced on a the end
PREFECTURE_NUM_HEADER_VARIABLES = 5


#
# PROVINCE VARIABLES
#

PROVINCE_DATASET = "province"

# The location of the province dropdown on the province page
PROVINCE_DATASET_DD = 0

# array of provincial page codes
PROVINCE_PAGES = ['A0101', 'A0103', 'A0104', 'A0201', 'A0202', 'A0301', 'A0302', 'A0402', 'A0501', 'A0601', 'A0602', 'A0801', 'A0802', 'A0803', 'A0804', 'A0901', 'A0904', 'A1001', 'A1002', 'A1101', 'A1102', 'A1103', 'A1201', 'A1202', 'A1401', 'A1402', 'A1501', 'A1601']
PROVINCE_HEADERS = ['Year', 'Province ID', 'Province', 'Gross Domestic Product(100 million yuan)', 'Primary Industry(100 million yuan)', 'Secondary Industry(100 million yuan)', 'Industry(100 million yuan)', 'Construction(100 million yuan)', 'Tertiary Industry(100 million yuan)', 'Transportation Post and Telecommunications(100 million yuan)', 'Wholesale Retail & Catering Trade(100 million yuan)', 'Per-Capita GDP(yuan/person)', 'Gross Domestic Product(%)', 'Primary Industry(%)', 'Secondary Industry(%)', 'Secondary Industry-Industry(%)', 'Secondary Industry-Construction(%)', 'Tertiary Industry(%)', 'Tertiary Industry(%)-Transportation Post and Telecommunications(%)', 'Tertiary Industry(%)-Wholesale Retail& Catering Trade(%)', 'Per-Capitas GDP(%)', 'Gross Domestic Product by Expenditure Approach(100 million yuan)', 'Final Consumption Expenditure(100 million yuan)', 'Household Expenditure(100 million yuan)', 'Government Expenditure(100 million yuan)', 'Gross Capital Formation(100 million yuan)', 'Fixed Capital(100 million yuan)', 'Changes in Inventories(100 million yuan)', 'Net Exportof Goods and Services(100 million yuan)', 'Total Permanent Population(year-end)(10000 persons)', 'Total Permanent Population-Male(10000 Persons)', 'Total Permanent Population-Female(10000 Persons)', 'Total Household registed Population(year-end)(10000 persons)', 'Total Household registed Population(year-end) Grouped by Sex-Male(10000 Persons)', 'Total Household registed Population(year-end) Grouped by Sex-Female(10000 Persons)', 'Birth Rate(e)', 'Death Rate(e)', 'Natural Growth Rate(e)', 'Total Number of Employed Persons(10000 persons)', 'Employed Persons by UrbanAreas(10000 persons)', 'Employed Persons by RuralAreas(10000 persons)', 'Employed Persons by Industry-Primary Industry(10000 persons)', 'Employed Persons by Industry-Secondary Industry(10000 persons)', 'Employed Persons by Industry-Tertiary Industry(10000 persons)', 'Staff and Workers(10000 persons)', 'Staff and Workers-State Owned Units(10000 persons)', 'Staff and Workers-Urban Collective Owned Units(10000 persons)', 'Staff and Workers-Other Ownership Units(10000 persons)', 'Total Investment in Fixed Assets(100 million yuan)', 'Domestic(100 million yuan)', 'DomesticState-owned(100 million yuan)', 'DomesticCollective-owned(100 million yuan)', 'DomesticCooperative(100 million yuan)', 'DomesticJoint(100 million yuan)', 'DomesticLimited Liability(100 million yuan)', 'DomesticShare-holding(100 million yuan)', 'DomesticPrivate(100 million yuan)', 'DomesticSelf-employed Individual(100 million yuan)', 'DomesticOthers(100 million yuan)', 'Funds from Hong Kong,Macao and Taiwan(100 million yuan)', 'Foreign Funded(100 million yuan)', 'Floor Space of Buildings-Under Construction(10000 sq m)', 'Floor Space of Buildings-Completed(10000 sq m)', 'Floor Space of Commercial House Actually Sold(10000 sq m)', 'Floor Space of Commercial House Actually Sold-Residential Buildings(10000 sq m)', 'Commercial House Purchased by Individuals(10000 sq m)', 'Total Sales of Commercial House(100 million yuan)', 'Total Sales of Commercial House-Residential Buildings(100 million yuan)', 'General Retail Price Index(%)', 'General Consumer Price Index(%)', 'General Consumer Price Index-#Rural Area(%)', 'General Consumer Price Index-#Urban Area(%)', 'General Purchasing Price Index of Farm Products(%)', 'General Rural Retail Price Index of Industrial Products(%)', 'Urban Households Per Capital Annual-Disposable Income-Total(yuan)', 'Urban Households Per Capital Annual-Disposable Income-Index(1978=100)%', 'Urban Households Per Capital Annual-Living Expenditure(yuan)', 'Urban Households Per Capital Annual-Living Expenditure-Food(yuan)', 'Rural Households Per Capital Annual-Net Income-Total(yuan)', 'Rural Households Per Capital Annual-Index(1978=100)(%)', 'Rural Households Per Capital Annual-Living Expenditure(yuan)', 'Rural Households Per Capital Annual-Living Expenditure-Food(yuan)', 'Per Capita Living Space Urban(sq.m)', 'Per Capita Living Space Rural(sq.m)', 'Average Wage of Staff and Workers Total(yuan)', 'Average Wage of Staff and Workers Total Index(1978=100)(%)', 'Savings Depositin Urban and Rural Areas(year-end)(100 million yuan)', 'Per Captia Savings Deposit(yuan)', 'Local Revenue(100 million yuan', 'Local Taxes(100 million yuan)', 'Local Taxes-Industrial and Commercial(100 million yuan)', 'Local Expenditure(100 million yuan)', 'Local Expenditure-Capital Construction(100 million yuan)', 'Local Expenditure-Innovation Funds(100 million yuan)', 'Local Expenditure-Supporting Agricultural Production(100 million yuan)', 'Local Expenditure-Culture Education Science & Health Care(100 million yuan)', 'Local Expenditure-Government Administration(100 million yuan)', 'Total Deposits in Financial Institutions(100 million yuan)', 'Deposits in Financial Institutions - Enterprise Deposits (100 million yuan)', 'Total Loans in Financial Institutions(100 million yuan)', 'Loans in Financial Institutions - To Industrial Enterprises (100 million yuan)', 'Loans in Financial Institutions - To Commercial Enterprises (100 million yuan)', 'Loans in Financial Institutions - To Agriculture (100 million yuan)', 'Loans in Financial Institutions - Fixed Assets (100 million yuan)', 'Number of Township and Town Governments(unit)', 'Number of Villagers Committees(unit)', 'Number of Rural Households(household)', 'Number of Rural Populations(10000 persons)', 'Number of Rural Laborers(10000 persons)', 'Number of Rural Laborers - Farming Forestry Animal Husbandry & Fishery(10000 persons)', 'Number of Rural Laborers - Industry(10000 persons)', 'Number of Rural Laborers - Construction(10000 persons)', 'Number of Rural Laborers - Transportation(10000 persons)', 'Number of Rural Laborers - Wholesale Retail Sale and Catering Trades(10000 persons)', 'Number of Rural Laborers - Others(10000 persons)', 'Cultivated Areas(1000 hectares)', 'Cultivated Areas - Paddy Fields(1000 hectares)', 'Cultivated Areas - Dry Fields(1000 hectares)', 'Cpacity of Reservoirs(100 million cu.m)', 'Number of large and Medium Agricultural Tractors(unit)', 'Capacity of Large and Medium Agricultural Tractors(10000 kw)', 'Number of Mini-tractors(unit)', 'Capacity of Mini-tractors(10000 kw)', 'Number of Diesel Engines(unit)', 'Capacity of Diesel Engines(10000 kw)', 'Number of Trucks for Agricultrural Use(unit)', 'Capacity of Trucks for Agricultrural Use(10000 kw)', 'Number of Motorized Fishing Boats(unit)', 'Capacity of Motorized Fishing Boats(10000 kw)', 'Grain Crops(kg-hectare)', 'Cotton(kg-hectare)', 'Oilbearing Crops(kg-hectare)', 'Sugar Crops(kg-hectare)', 'Grain Crops(kg)', 'Cotton(kg)', 'Output of Pork Beef and Mutton(kg)', 'Aquatic Products(kg)', 'Output Value of Farming and Forestry(yuan)', 'Gross Output Value of Farming Forestry and Animal Husbandry - Total(100 million yuan)', 'Gross Output Value of Farming Forestry and Animal Husbandry - Farming(100 million yuan)', 'Gross Output Value of Farming Forestry and Animal Husbandry - Forestry(100 million yuan)', 'Gross Output Value of Farming Forestry and Animal Husbandry - Animal Husbandry(100 million yuan)', 'Gross Output Value of Farming Forestry and Animal Husbandry - Fishing(100 million yuan)', 'Indices of Gross Output Value of Farming and Animal Husbandry - Total(%)', 'Indices of Gross Output Value of Farming and Animal Husbandry - Farming(%)', 'Indices of Gross Output Value of Farming and Animal Husbandry - Forestry(%)', 'Indices of Gross Output Value of Farming and Animal Husbandry - Animal Husbandry(%)', 'Indices of Gross Output Value of Farming and Animal Husbandry - Fishery(%)', 'Total Power of Agricultural Machinery(10000 kw)', 'Irrigated Area(1000 hectares)', 'Consumption of Chemical Fertilizers(10000 tons)', 'Electricity Consumed in Rural Area(100 million kwh)', 'Total Sown Area(1000 hectares)', 'Sown Area - Grain Crops(1000 hectares)', 'Grain(10000 tons)', 'Cotton(10000 tons)', 'Oil-Bearing Crops(10000 tons)', 'Fruits(10000 tons)', 'Fruits(10000 tons)', 'Large Animals(year-end)(10000 heads)', 'Output of Pork Beef & Mutton(10000 tons)', 'Aquatic Products(10000 tons)', 'Number of Industrial Enterprises(unit)', 'Number of Industrial Enterprises - State Owned(unit)', 'Number of Industrial Enterprises - Collective Owned(unit)', 'Gross Industrial Output Value(100 million yuan)', 'Gross Industrial Output Value - State Owned(100 million yuan)', 'Gross Industrial Output Value - Collective Owned(100 million yuan)', 'Indices of Gross Industrial Output Value(%)', 'Indices of Gross Industrial Output Value - State Owned(%)', 'Indices of Gross Industrial Output Value - Collective Owned(%)', 'Cloth(100 million m)', 'Machine-made Paper and Paperboard(10000 tons)', 'Cigarettes(100 million unit)', 'Coal(10000 tons)', 'Oil(10000 tons)', 'Electricity(100 million kwh)', 'Steel(10000 tons)', 'Steel Products(10000 tons)', 'Cement(10000 tons)', 'Plate Glass(10000 weight cases)', 'Chemical Fertilizer(10000 tons)', 'Number of Construction Enterprises(unit)', 'Number of Construction Enterprises - State Owned(unit)', 'Number of Construction Enterprises - Urban Collective Owned(unit)', 'Number of Persons Engaged(10000 persons)', 'Number of Persons Engaged - State Owned(10000 persons)', 'Number of Persons Engaged - Urban Collective Owned(10000 persons)', 'Gross OutputValue of Construction Enterprises(100 million yuan)', 'Gross OutputValue of Construction Enterprises - State Owned(100 million yuan)', 'Gross OutputValue of Construction Enterprises - Urban Collective Owned(100 million yuan)', 'Floor Space of Building Construction - Under Construction(10000 sq m)', 'Floor Space of Building Construction - Completed(10000 sq m)', 'Length of Railways(10000 km)', 'Length of Highways(10000 km)', 'Passenger Traffic(10000 persons)', 'Passenger Traffic - Railway(10000 persons)', 'Passenger Traffic - Highway(10000 persons)', 'Passenger Traffic - Waterways(10000 persons)', 'Freight Traffic(10000 tons)', 'Freight Traffic - Railway(10000 tons)', 'Freight Traffic - Highway(10000 tons)', 'Freight Traffic - Waterways(10000 tons)', 'Turnover Volume of Passenger Traffic(100 million passenger-km)', 'Turnover Volume of Passenger Traffic - Railway(100 million passenger-km)', 'Turnover Volume of Passenger Traffic - Highway(100 million passenger-km)', 'Turnover Volume of Passenger Traffic - Waterways(100 million passenger-km)', 'Turnover Volume of Freight Traffic(100 million ton-km)', 'Turnover Volume of Freight Traffic - Railway(100 million ton-km)', 'Turnover Volume of Freight Traffic - Highway(100 million ton-km)', 'Turnover Volume of Freight Traffic - Waterways(100 million ton-km)', 'Number of Civil Motor Vehicles Owned(10000 units)', 'Business Volume of Post and Telecommunications(100 million yuan)', 'Number of Letters(100 million pcs)', 'Number of Loans Urban Telephone Subscribers(10000 subscribers)', 'Number of Telephone Sets(10000 units)', 'Total Retail Sales of Consumer Goods(100 million yuan)', 'Retail Sales of Consumer Goods - State Owned(100 million yuan)', 'Retail Sales of Consumer Goods - Collective Owned(100 million yuan)', 'Retail Sales of Consumer Goods - Urban Areas(100 million yuan)', 'Retail Sales of Consumer Goods - Rural Areas(100 million yuan)', 'Transaction Value(100 million yuan)', 'Total Imports and Exports(1000 US dollars)', 'Imports and Exports - Exports(1000 US dollars)', 'Foreign Capital Actually Utilized(USD 10000)', 'Foreign Capital Actually Utilized - Foreign Loans(USD 10000)', 'Foreign Capital Actually Utilized - Direct Foreign Investment(USD 10000)', 'Foreign Capital Actually Utilized - Other Foreign Investments(USD 10000)', 'Foreign Exchange Income from Tourism(USD million)', 'Student Enrollment - Institutions of Higher Education(10000 Persons)', 'Student Enrollment - Secondary Schools(10000 Persons)', 'Student Enrollment - Secondary Schools (Regular Secondary Schools)(10000 Persons)', 'Student Enrollment - Primary Schools(10000 Persons)', 'Percentage of Graduates of Primary Schools Entering Secondary(%)', 'Percentage of School-Aged Children Enrolled(%)', 'Number of Full-time Teachers - Institutions of Higher Education(10000 persons)', 'Number of Full-time Teachers - Secondary Schools(10000 persons)', 'Number of Full-time Teachers - Secondary Schools (Regular Secondary Schools)(10000 persons)', 'Number of Full-time Teachers - Primary Schools(10000 persons)', 'Art Performance Troupes(unit)', 'Cultural Centers(unit)', 'Public Libraries(unit)', 'Number of Books Published(100 million copies)', 'Number of Magazines Published(100 million copies)', 'Number of Newspapers Published(100 million copies)', 'Listener Rating(%)', 'Viewer Rating(%)', 'Number of Health Institutions(unit)', 'Number of Health Institutions - Hospitals(unit)', 'Number of Beds in Health Institution(10000 units)', 'Number of Beds in Health Institution - Hospitals(10000 units)', 'Medical Technical Personnel(10000 persons)', 'Medical Technical Personnel - Doctors(10000 persons)', 'Per 10000 persons - Number of Beds(unit)', 'Per 10000 persons - Number of Doctors(person)', 'Area of Cultivated Land(10000 hectares)', 'Area of Undeveloped Land(10000 hectares)', 'Area of Afforestated Land(10000 hectares)', 'Grassland(10000 hectares)', 'Forest Area(10000 hectares)', 'Forest-coverage Rate(%)', 'Surface Water Volume(100 million cu.m)', 'Hydropower Resources(100 million kw)', 'Inland Water Area(10000 hectares)', 'Coatal Area(10000sq.km)', 'Cultivable Area in Shallow Sea and Sea-beaches(1000 hectares)']
PROVINCE_BASE_URL = 'macroyr/macroyrtshow.asp'
PROVINCE_NUM_HEADER_VARIABLES = 3

#
# URBAN VARIABLES
#

URBAN_DATASET = "urban"

# array of urban page codes
URBAN_PAGES = ['A01', 'A02', 'A05', 'A06', 'A07', 'A12', 'A13', 'A14', 'A18', 'A19', 'A20']
# headers of the data columns
URBAN_HEADERS = ['Year', 'Province ID', 'Province', 'IsProvinceTotal', 'District', 'DistrictID', 'Total Population at year-end(10000 persons)',	'Natural Growth Rate(e)', 'Number of Employees(10000 persons)',	'Number of Urban Registered Unemployees at Year-end(10000 persons)', 'Land Area(10000 sq.km)', 'Cultivated Land by Year-end(1000 hectares)', 'Gross Domestic Product(100 million yuan)', 'GDP of Primary Industry(100 million yuan)', 'GDP of Secondary Industry(100 million yuan)', 'GDP of Tertiary Industry(100 million yuan)', 'Yield of Major Farm Crops Fruits(10000 tons)', 'Yield of Major Farm Products Total Aquatic Products(10000 tons)', 'Investment in Fixed Assets(100 million yuan)', 'Investment in Real Estate Development(100 million yuan)', 'Total Retail Sales of Consumer Goods(100 million yuan)', 'Total Foreign Capital from Signed Contracts(USD 10000)', 'Actually Utilized Foreign Capital in This Year(USD 10000)', 'Value of Export(1,000 US dollars)', 'Number of Regular Secondary Schools(unit)', 'Number of Primary Schools(unit)', 'Number of Full-time Teachers in Regular Secondary Schools(10000 persons)', 'Number of Full-time Teachers in Primary Schools(10000 persons)', 'Student Enrollment in Regular Secondary Schools(10000 persons)', 'Student Enrollment in Primary Schools(10000 persons)']
# url specifying the urban pages
URBAN_BASE_URL = 'city/citytshow.asp'
# number of left-hand side array variables that will be spliced on a the end
URBAN_NUM_HEADER_VARIABLES = 4


##
## DEFAULT VARIABLES
##

# This is the code to make sure that an option has to be picked
NO_DEFAULT = 0

# This is the starting and ending years of the dataset online
URBAN_DATASET_START = 1996
URBAN_DATASET_END = 2012

COUNTY_DATASET_START = 1947
COUNTY_DATASET_END = 2012

PROVINCE_DATASET_START = 1947
PROVINCE_DATASET_END = 2012

NATIONAL_DATASET_START = 1947
NATIONAL_DATASET_END = 2012

PREFECTURE_DATASET_START = 1996
PREFECTURE_DATASET_END = 2012

# array of years we are interested in
DEFAULT_YEARS_COUNTY = [1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
DEFAULT_YEARS_URBAN = [1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
DEFAULT_YEARS_PROVINCE = [1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
DEFAULT_YEARS_NATIONAL = [1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
DEFAULT_YEARS_PREFECTURE = [1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]

DEFAULT_DATASET = NO_DEFAULT

DEFAULT_VERBOSE = True

DEFAULT_MULTIFILE = False

####
#### FUNCTIONS
####

# Properly sets up the CSV file according to the program options
def initCSV(dataset, years, multifiles):

	csvfiles = []
	headers = ""

	# Sets the headers correctly
	if(dataset == COUNTY_DATASET):
		headers = COUNTY_HEADERS
			
	elif(dataset == NATIONAL_DATASET):
		headers = NATIONAL_HEADERS
		
	elif(dataset == PROVINCE_DATASET):
		headers = PROVINCE_HEADERS
	
	elif(dataset == PREFECTURE_DATASET):
		headers = PREFECTURE_HEADERS

	elif(dataset == URBAN_DATASET):
		headers = URBAN_HEADERS
	
	else:
		print "No headers chosen"
		sys.exit()
		
	# Switches up depending on whether the option to specify multiple files has been selected
	if(multifiles == False or dataset==NATIONAL_DATASET):
		filename = dataset + str(years[0]) + "-" + str(years[len(years)-1]) + ".csv"

		csvfiles.append(csv.writer(open(filename,"w")))
		csvfiles[0].writerow(headers)
	else:
		for i in years:
			filename = dataset + str(i) + ".csv"
	
			csvfiles.append(csv.writer(open(filename,"w")))
			csvfiles[years.index(i)].writerow(headers)

	return csvfiles

# Sends a request; the error-handling code will keep trying to hit the server unless we get an unrecoverable
# error or hit the defined NUM_SERVER_TRIES
def sendRequest(baseurl, postvalues, txheader):
	output = ""
	notDone = True
	# To comport with the standard definition of "times"
	serverFailTimes = 1
	txdata = ''
	
	# encodes the postvalues into a format python understands
	txdata = urllib.urlencode(postvalues)
	
	while(notDone):
		try:
			# sends the POST request
			bodyreq = request(baseurl, txdata, txheader)
			bodyhandle = urlopen(bodyreq)

			# gets the text
			output = bodyhandle.read()
			
			# We finished okay, so no need to loop
			notDone = False
			
		# Need a bunch of error handling in case the system gives us trouble
		except IOError, e:
			print "\nThe server failed to respond for some reason."
			
			# We have failed too many times, and must exit
			if(serverFailTimes == NUM_SERVER_TRIES):
				print "\nThe server has failed to respond %s times."
				print "This is past the limit specified in the code NUM_SERVER_TRIES"
				print "Thus, we are exiting"
				sys.exit()
				
			# This error is probably server busy	
			elif hasattr(e, 'code'):
				# Often, the server will just get a bit pissy and give a 500 error, but we can deal with this
				# note that we loop after the wait time, as notDone still equals True
				print "In particular, the server gave us an HTML error code - %s." % e.code
				print "This is probably recoverable. Waiting %s seconds before trying again\n" % WAIT_TIME
				
				# Wait a bit for the server to get 'unstuck', and note the failure
				time.sleep(WAIT_TIME)
				serverFailTimes = serverFailTimes + 1
				
			# These other types of errors may not be recoverable, so we have to exit
			elif hasattr(e, 'reason'):
				print "In particular, the error has the following 'reason' attribute :"
				print e.reason
				print "This usually means the server doesn't exist,"
				print "is down, or we don't have an internet connection."
				print "Since this error could mean many things (some of which are unrecoverable), the program is exiting now."
				sys.exit()
			# Not sure what falls into this, but it is probably bad
			else:
				print "Encountered an unknown error. Exiting."
				sys.exit()
		
	return output

def parseRows(output):

	rows = []
	numcolumns = 0
	numcolumnsdone = False

	soup = BeautifulSoup(output)
	
	for row in soup.findAll('table', id="texttable1")[0].findAll('tr'):

		rowParent = row.parent

		# Skipping the headers
		if rowParent.name == 'thead':
			pass
		# Nn case the header is malformed, need to check to see if we are still in header 
		elif rowParent.parent.name == 'thead':
			pass
		# Skipping the tails
		elif row.td['class'][0] == u'tdtail':
			pass
			#print "found tail"
			
			#print "row contents: " + str(row.contents)
		
			#data = row.findAll('td')
		
			#print "data contents: " + str(data)
		
			#for contents in enumerate(row.contents):
			#for contents in data:
			#	print("numcolumns in tail: " + str(numcolumns))
			#	numcolumns = numcolumns + 1

		else:
			datarow = []
						
			# Iterating through the data in the row entry
			for i, contents in enumerate(row.contents):

				# Have to record the number of columns for later use on the first data row
				if(numcolumnsdone == False):
					numcolumns = numcolumns + 1
			
				# Checking for missing values
				if(contents.string.isspace()):
					datarow.append(MISSING_VALUE)
				# Adds the name; no need to strip commas from the name
				elif(i == 0):
					datarow.append(contents.string)
				# Appends the data to our county array
				else:
					# Strip out the superfluous commas
					datum = contents.string.replace(",", "")
					datarow.append(datum)
			
			rows.append(datarow)
			numcolumnsdone = True
	
	return rows, numcolumns

# This takes in a specific year's results to discover the list of provinces that year
def parseDropdown(output, dropdown):
	soup = BeautifulSoup(output)
	dropdownlist = []

	for row in soup.findAll('select')[dropdown].findAll('option'):
		
		if row['value'] == '':
			# skips the 'all' option
			pass
		else:
			# Adds to the list the unit and the row
			dropdownlist.append((row['value'], row.string))

	return dropdownlist

# A little helper function to find the appropriate row index in the database
# returns -1 if not found, so that the code will throw an error
# name offset is what column in the data the name is
def findRowIndex(database, name, nameoffset):
	
	index = -1
	found = 0 
	cleanedname = ""
	test = []
	
	for i, row in enumerate(database):
	
		# This strips off the tailing spaces; some of the dropdowns have extra spaces at the end
		# which causes some obvious problems
		cleanedname = name.rstrip()
	
		test = [cleanedname, row[nameoffset]]
	
		# checking for a hit; row[0] stores the subunit name
		if(row[nameoffset] == cleanedname):
			index = i
			found = found + 1
		
	if(found > 1):
		print "Somehow there is more than one unit in the database with the same name. This is a serious problem."
		print "Exiting now"
		raise self.e
	
	return index

# Creates an entry in the csv file, taking in one year/province set and writing a line
# note: provincetuple specifies province ID and name.
# note: hassum indicates whether the first row is a summation row. If so, the 4th column will be a 
# flag that indicates this, otherwise will just be a zero.
def enterData(database, csvfile, provincetuple, year, dataset):
	
	for i, row in enumerate(database):
	
		## note that to add the additional control data, we have to put them
		## on in reverse, as insert works like a 'push'
	
		# this is for if the first row is a summation row
		if(dataset == URBAN_DATASET):
			if(i == 0):
				row.insert(0, 1)
			else:
				row.insert(0, 0)
		elif(dataset==PREFECTURE_DATASET):
			# This marks if it is a province subtotal; there is also a possibility of a district subtotal
			if(i == 0):
				row.insert(0, 1)
				row.insert(0, 0)
			elif(i == 1 and row[0].startswith("Districts")):
				row.insert(0, 1)
				row.insert(0, 1)
			else:
				row.insert(0, 0)
				
				# This marks the district subtotals
				if(row[1].startswith("Districts")):
					row.insert(0, 1)
				else:
					row.insert(0, 0)					
				
		elif(dataset==COUNTY_DATASET):
			# we don't have any special columns for county data
			pass

		if(dataset != PROVINCE_DATASET and dataset != NATIONAL_DATASET):
			# provinces don't need anything added
			row.insert(0, provincetuple[1])
			row.insert(0, provincetuple[0])
			row.insert(0, year)

		# once we have a well-formed entry, we can write the row
		csvfile.writerow(row)

# Gets a list of all of the provinces available based on the drop-down menus
# will iterate through all the years passed
def initProvinceList(years, dataset, verbose):
	
	provincelist = []
	url = ""

	# initializing the internal database based on year/county retrieval
	for i in years:
		if(dataset==PROVINCE_DATASET and verbose==True):
			print "Initializing province list"
		elif(verbose==True):
			print "Initializing province list for year: %s" % i

		# values for the POST url
		if(dataset==COUNTY_DATASET):
			values = {'code':'A01', 'province':'', 'city':'', 'ayear':i}
			url = BASE_URL + COUNTY_BASE_URL
		elif(dataset==PROVINCE_DATASET):
			values = {'code':'A0101', 'dq':'', 'ayear':i}
			url = BASE_URL + PROVINCE_BASE_URL
		elif(dataset==URBAN_DATASET):
			values = {'code':'A01', 'province':'', 'city':'', 'ayear':i, 'sid':'0'}
			url = BASE_URL + URBAN_BASE_URL
		elif(dataset==PREFECTURE_DATASET):
			values = {'code':'A01', 'province':'', 'city':'', 'ayear':i, 'sid':'0'}
			url = BASE_URL + PREFECTURE_BASE_URL
	
		# sends the request
		output = sendRequest(url, values, TX_HEADERS)
			
		if(dataset==PROVINCE_DATASET):
			provincelist = parseDropdown(output, PROVINCE_DATASET_DD)
		else:
			provincelist.append(parseDropdown(output, PROVINCE_DD))
	
	if(verbose==True):
		print "\n\n***Inititalization complete. Starting on data gathering***\n\n"
	
	return provincelist

# This processes a page-type that is below the province level - essentially, counties and cities
def processSubProvinceData(years, csvfiles, verbose, dataset, multifile):
	
	pages = []
	provincelist = []
	url = ""
	columncursor = 0
	
	if(dataset==COUNTY_DATASET):
		pages = COUNTY_PAGES
		url = BASE_URL + COUNTY_BASE_URL
	elif(dataset==URBAN_DATASET):
		pages = URBAN_PAGES
		url = BASE_URL + URBAN_BASE_URL
	elif(dataset==PREFECTURE_DATASET):
		pages = PREFECTURE_PAGES
		url = BASE_URL + PREFECTURE_BASE_URL
			
	provincelist = initProvinceList(years, dataset, verbose)
	
	# now that we've initialized, we need to loop through all of the years
	for year in years:
	
		if(verbose==True):
			print "Now doing year: %s" % year
	
		# within each year, we have to loop through all of the provinces
		for provincetuple in provincelist[years.index(year)]:
			columncursor = 0
			subunitDB = []
			
			if(verbose==True):
				print "\tNow doing province: %s" % provincetuple[1]
		
			# goes across all the pages within the province/year to get the data we need
			for numpages in pages:
			
				if(verbose==True):
					print "\t\tNow doing page: %s" % numpages
				
				if(dataset==COUNTY_DATASET):
					values = {'code':numpages, 'province':provincetuple[0], 'city':'', 'ayear':year}
				elif(dataset==URBAN_DATASET):
					values = {'code':numpages, 'province':provincetuple[0], 'city':'', 'ayear':year, 'sid':'1'}
				elif(dataset==PREFECTURE_DATASET):
					values = {'code':numpages, 'province':provincetuple[0], 'city':'', 'ayear':year, 'sid':'0'}
				
				# sends the request
				output = sendRequest(url, values, TX_HEADERS)
				
				# keeps track of which column we are on, after parsing data into the database
				if(dataset==COUNTY_DATASET):
					columncursor = parseSubunitData(output, subunitDB, columncursor, COUNTY_DATASET)
				elif(dataset==URBAN_DATASET):
					columncursor = parseSubunitData(output, subunitDB, columncursor, URBAN_DATASET)
				elif(dataset==PREFECTURE_DATASET):
					columncursor = parseSubunitData(output, subunitDB, columncursor, PREFECTURE_DATASET)
			
			# now that we've got all of the pages' data concat'ed, we can process it
			if(multifile==True):
				if(dataset==COUNTY_DATASET):
					enterData(subunitDB, csvfiles[years.index(year)], provincetuple, year, COUNTY_DATASET)
				elif(dataset==URBAN_DATASET):
					enterData(subunitDB, csvfiles[years.index(year)], provincetuple, year, URBAN_DATASET)
				elif(dataset==PREFECTURE_DATASET):
					enterData(subunitDB, csvfiles[years.index(year)], provincetuple, year, PREFECTURE_DATASET)
			else:
				if(dataset==COUNTY_DATASET):
					enterData(subunitDB, csvfiles[0], provincetuple, year, COUNTY_DATASET)
				elif(dataset==URBAN_DATASET):
					enterData(subunitDB, csvfiles[0], provincetuple, year, URBAN_DATASET)
				elif(dataset==PREFECTURE_DATASET):
					enterData(subunitDB, csvfiles[0], provincetuple, year, PREFECTURE_DATASET)

# Parses a generic subunit data page
def parseSubunitData(output, database, columncursor, dataset):

	data = []
	rowIndex = 0
	numColumns = 0
	pageColumns = 0
	subunitTuple = []
	subunits = []

	n = columncursor
	startColumncursor = columncursor

	# Need to set numColumns based on the dataset
	if(dataset == COUNTY_DATASET):
		numColumns = len(COUNTY_HEADERS) - (COUNTY_NUM_HEADER_VARIABLES)
	elif(dataset == URBAN_DATASET):
		numColumns = len(URBAN_HEADERS) - (URBAN_NUM_HEADER_VARIABLES)
	elif(dataset == PREFECTURE_DATASET):
		numColumns = len(PREFECTURE_HEADERS) - (PREFECTURE_NUM_HEADER_VARIABLES)
	else:
		print "Dataset type not supported in this parsing mode"
		raise self.e

	# initing the db based on the dropdown menu
	if(columncursor == 0):
		subunits = parseDropdown(output, SUBUNIT_DD)

		for n, subunit in enumerate(subunits):
			initSubunit(database, subunit[1].rstrip(), subunit[0], numColumns)
		
		# need to update columncursor variables
		columncursor = columncursor + 2
		n = columncursor
		startColumncursor = columncursor
	
	# gets all the data rows and the number of columns
	datapage, pageColumns = parseRows(output)
	
	# updates column cursor; we have to reduce by 1 because the name of the unit doesn't count as a column
	columncursor = startColumncursor + (pageColumns-1)
	
	# Iterates down the list of rows
	for datarow in datapage:

		# checks to see if the named unit is already in the database; if not, rowIndex is == -1
		rowIndex = findRowIndex(database, datarow[0], 0)

		# now we have to find if this subunit already has an entry;
		# if it doesn't exist yet, we have to creat a new row
		# if it does, then we add on the new data parts
		# note: this only occurs when the county shows up on subsequent 
		# pages but is not on the first page's subunit dropdown list
		# not sure if this ever happens, but probably better to account for it
		if(rowIndex == -1):
			print "doing post-init not found code"
			subunits = []
			subunitTuple = []

			subunits = parseDropdown(output, SUBUNIT_DD)
			
			# Finds the necessary subunit
			for subunit in subunits:
				if(subunit[1] == datarow[0]):
					subunitTuple = subunit
				
			# If the subunit does not have a drop-down entry, we are in trouble	
			if(subunitTuple == []):
				print "Subunit has shown up that does not have a corresponding ID given"
				print "This is a serious error"
				sys.exit()
				
			initSubunit(database, subunitTuple[1], subunitTuple[0], numColumns)		
									
			# resets the row index to the proper value
			rowIndex = findRowIndex(database, datarow[0], 0) 
		
		# need to reset n each time for each row
		n = startColumncursor
		
		# actually adds on the new data into the database structure
		for p, newdata in enumerate(datarow):
			if(p == 0):
				# name is already entered; this datarow has the name
				pass
			else:										
				# adds in the new data, advances the column variable
				database[rowIndex][n] = newdata
				n = n + 1
	
	# lets us know where we left off
	return columncursor

# Another helper function that initializes the subunit data in the subunit database
# note: only called from parseSubunitData
def initSubunit(database, name, id, numColumns):
	
	newentry = []
	
	for i in range(numColumns):
		if(i == 0):
			newentry.append(name)
		elif(i == 1):
			newentry.append(id)
		else:
			newentry.append(MISSING_VALUE)
	
	database.append(newentry)
	
# Lets people know how to use the program from the command line
def usage(error):
	
	print ""
	
	if(error != ""):
		print "\x1B[1merror: " + error + "\x1B[0m\n"
	
	print "USAGE: chinesedata [-c | -n | -p | -u] [-h | --help] [-y] [-s] [-m]"
	print ""
	print "NAME\n\tchinesedata -- downloads data from the All China Online Database\n"
	print "DESCRIPTION\n\tThis program allows one to download one of several different datasets"
	print "\tavailable from the University of Michigan depository, provided one has a"
	print "\tsubscription. The script must be run from a machine that has an"
	print "\tacceptable IP address to their service. The data is written out" 
	print "\tin csv format to the directory from which the script is run. Note that"
	print "\ta dataset option must be specified."
	print "\t"
	print "\tThe following options are available:\n"
	print "\t-c\tSpecifies downloading the counties dataset; available years\n\t\tare " + str(COUNTY_DATASET_START) + " to " + str(COUNTY_DATASET_END) + "\n"
	print "\t-f\tSpecifies downloading the prefecture-level dataset; available\n\t\tyears are " + str(PREFECTURE_DATASET_START) + " to " + str(PREFECTURE_DATASET_END) + "\n"
	print "\t-n\tSpecifies downloading the national-level dataset; available\n\t\tyears are " + str(NATIONAL_DATASET_START) + " to " + str(NATIONAL_DATASET_END) + "\n"
	print "\t-p\tSpecifies downloading the provincial-level dataset; available\n\t\tyears are " + str(PROVINCE_DATASET_START) + " to " + str(PROVINCE_DATASET_END) + "\n"
	print "\t-u\tSpecifies downloading the urban-area dataset (at the level of a\n\t\tcounty); available years are " + str(URBAN_DATASET_START) + " to " + str(URBAN_DATASET_END) + "\n"
	print "\t-h\tShows this message.\n"
	print "\t--help\tSame as -h.\n"
	print "\t-y\tSpecifies the years requested. Takes a required argument of the\n\t\tyears that are desired. Default if -y is not selected is either\n\t\t" + str(DEFAULT_YEARS_COUNTY[0]) + " or the first year data is available, whichever is farther\n\t\tback in time, to " + str(DEFAULT_YEARS_COUNTY[len(DEFAULT_YEARS_COUNTY)-1]) + ", but this can take a long time on the\n\t\tcounty, prefecture, and urban datasets.\n\n\t\tNecessary format is: 1982+2000\n\t\t"
	print "\t-s\tIf -s is selected, then only error messages will be printed; \n\t\totherwise, verbose status updates will be printed.\n"
	print "\t-m\tIf -m is selected, then each year's data will be recorded in\n\t\tits own file. Default is to write all data to one file. Good if\n\t\tyour connection is unreliable. Note: option has no effect if \n\t\t-n flag is chosen."
	print ""
	print "\tSample usage: \"python chinesedata.py -c -m -y 1999+2002\""
	print "\tThis gets the county data and writes each year from 1999-2002 to a\n\tseparate file."
	print ""
	print "This script is (c) 2008, 2009, 2010, 2013 Andrew MacDonald (andrewm@stanfordalumni.org)"
	print "All rights reserved. Version 1.1\n"
	
	sys.exit(0)

# Parses the command line arguments and sets up the default variables
def parseArguments(argv):

	# setting up our defaults here
	dataset = DEFAULT_DATASET
	years = []
	multifile = DEFAULT_MULTIFILE
	verbose = DEFAULT_VERBOSE
	
	# indicates whether years are within the bounds allowed, and if the -y flag was used
	validYears = True
	yearsSpecified = False
	startYear = 0
	endYear = 0
	
	# used to check to make sure at least one is picked
	numDatasetPicked = 0

	try: 
		opts, args = getopt.getopt(argv, "cpunfhy:sm", ["help", "year="])

		if(opts == []):
			usage("no arguments specified; at least a dataset flag must be set.")
		# arguments aren't used in this script
		elif(args != []):
			usage("extraneous argument(s): " + str(args) + " not allowed.")
	
	except getopt.GetoptError, err:           
		usage(str(err))
		sys.exit(0)                         

	for opt, arg, in opts:
	
		# doing help
		if opt in ("-h", "--help"):      
			usage("")                     
			sys.exit() 
	
		# noting up the dataset
		elif(opt == "-c"):
			dataset = COUNTY_DATASET
			numDatasetPicked = numDatasetPicked + 1
			if(yearsSpecified == False):
				years = DEFAULT_YEARS_COUNTY
				startYear = COUNTY_DATASET_START
				endYear = COUNTY_DATASET_END

		elif(opt == "-n"):
			dataset = NATIONAL_DATASET
			numDatasetPicked = numDatasetPicked + 1
			if(yearsSpecified == False):
				years = DEFAULT_YEARS_NATIONAL
				startYear = NATIONAL_DATASET_START
				endYear = NATIONAL_DATASET_END
			
		elif(opt == "-p"):
			dataset = PROVINCE_DATASET
			numDatasetPicked = numDatasetPicked + 1
			if(yearsSpecified == False):
				years = DEFAULT_YEARS_PROVINCE
				startYear = PROVINCE_DATASET_START
				endYear = PROVINCE_DATASET_END
			
		elif(opt == "-u"):
			dataset = URBAN_DATASET
			numDatasetPicked = numDatasetPicked + 1
			if(yearsSpecified == False):
				years = DEFAULT_YEARS_URBAN
				startYear = URBAN_DATASET_START
				endYear = URBAN_DATASET_END
				
		elif(opt == "-f"):
			dataset = PREFECTURE_DATASET
			numDatasetPicked = numDatasetPicked + 1
			if(yearsSpecified == False):
				years = DEFAULT_YEARS_PREFECTURE
				startYear = PREFECTURE_DATASET_START
				endYear = PREFECTURE_DATASET_END
	
		# checking for multifile
		elif(opt == "-m"):
			multifile = True
		
		# checking for silent mode
		elif(opt == "-s"):
			verbose = False	
		
		# checking for year
		elif(opt == "-y"):
			i = 0
			n = 0
			years = []
			# reset these now that we know we have to do years
			startYear = 0
			endYear = 0
			
			# text processing can throw a lot of exceptions if the text is malformed
			try:
				for digit in arg:
					# getting the start year; note that we are progressing digit by digit
					if(i <= 3):
						startYear = startYear + int(digit) * pow(10, 3-i)
						
					# checking sure we have the right seperator
					elif(i == 4):
						if(digit != "+"):
							raise self.e
					
					# getting the end year
					elif(i >= 5):
						endYear = endYear + int(digit) * pow(10, 8-i)
					
					# incremeting the counter
					i = i + 1
				
				# this means in some way or other the year-digits were too long or too short
				if(i < 9):
					raise self.e
				elif(i > 9):
					raise self.e
				
				# makes sure -y option isn't overwritten with the defaults when processing the dataset flag
				yearsSpecified = True
				
				# inits the years vector
				while(n <= endYear - startYear):
					years.append(startYear + n)
					n = n + 1
					
			except:
				usage("the formatting of the -y argument was incorrect; see the entry below for correct usage")
			
	# making sure that only one dataset is pickecd
	if(numDatasetPicked > 1):
		usage("too many dataset option flags picked")
	
	# making sure that they actually picked a dataset
	if(numDatasetPicked == 0):
		usage("no dataset specified")

	# checking the years now at the end, since we don't know in what order the flags were.
	validYears = checkYearValidity(startYear, endYear, dataset)
	
	if(validYears == False):
		usage("the years selected were outside the bounds of what is available for your chosen dataset")
		
	return dataset, years, multifile, verbose

# A small helper function that checks to see whether one has inputted a valid set of years
# in reference to the type of datset that they have selected.
# note: assumes that startYear and endYear are ints
def checkYearValidity(startYear, endYear, dataset):
	
	valid = True
	validStartYear = 0
	validEndYear = 0
	
	# Sets up the valid start and end years based on the datset
	if(dataset==COUNTY_DATASET):
		validStartYear = COUNTY_DATASET_START
		validEndYear = COUNTY_DATASET_END
		
	if(dataset==NATIONAL_DATASET):
		validStartYear = NATIONAL_DATASET_START
		validEndYear = NATIONAL_DATASET_END
	
	if(dataset==PROVINCE_DATASET):
		validStartYear = PROVINCE_DATASET_START
		validEndYear = PROVINCE_DATASET_END
	
	if(dataset==URBAN_DATASET):
		validStartYear = URBAN_DATASET_START
		validEndYear = URBAN_DATASET_END
		
	if(dataset==PREFECTURE_DATASET):
		validStartYear = PREFECTURE_DATASET_START
		validEndYear = PREFECTURE_DATASET_END
	
	# The sanity checks
	if(startYear < validStartYear):
		valid = False
	
	if(endYear > validEndYear):
		valid = False
		
	# obviously also a problem
	if(startYear > endYear):
		valid = False
	
	return valid

# Gets county data - this function and urban do essentially the same thing
def getCountyData(years, csvfiles, verbose, multifile):

	processSubProvinceData(years, csvfiles, verbose, COUNTY_DATASET, multifile)


def getNationalData(years, csvfiles, verbose, multifile):
	
	pages = NATIONAL_PAGES
	url = BASE_URL + NATIONAL_BASE_URL
	columncursor, startcolumncursor, numcolumns, index = [0, 0, 0, 0]
	database, newyear, rows = [[], [], []]
	
	# inits the database
	for i, year in enumerate(years):
	
		newyear = []
		
		for t in range(len(NATIONAL_HEADERS)):
			if(t == 0):
				newyear.append(str(year))
			else:
				newyear.append(MISSING_VALUE)
		
		database.append(newyear)
	
	for page in pages:
		if(verbose==True):
			print "Now doing page: %s" % page		

		startcolumncursor = columncursor
		
		# sends the request
		values = {'code':page}
		output = sendRequest(url, values, TX_HEADERS)
		
		# gets the rows and updates the column cursors
		rows, numcolumns = parseRows(output)
		columncursor = startcolumncursor + (numcolumns-1)

		# goes through the rows and copies the data to our year-database
		for row in rows:
			index = findRowIndex(database, row[0].lstrip('&nbsp;'), NATIONAL_NUM_HEADER_VARIABLES-1)
		
			if(index != -1):				
				for t in range(columncursor - startcolumncursor + 1):
					if(t == 0):
						# this is the year - we've already got that
						pass
					else:
						database[index][t+NATIONAL_NUM_HEADER_VARIABLES+startcolumncursor-1] = row[t]
			else:
				# got a year here that is not in the range of years we are asked to deal with
				# so, pass
				pass
	
	enterData(database, csvfiles[0], [], year, NATIONAL_DATASET)


def getProvinceData(years, csvfiles, verbose, multifile):

	pages = PROVINCE_PAGES
	url = BASE_URL + PROVINCE_BASE_URL
	provinces, lastyear, newrow, rows, currentyear = [[], [], [], [], []]
	columncursor, startcolumncursor, numcolumns, index = [0, 0, 0, 0]
	
	# Sends the last year of the dataset into the init function; 
	# this function requires an array of years, but we only need to 
	# init once
	lastyear.append(years[len(years)-1])
	provinces = initProvinceList(lastyear, PROVINCE_DATASET, verbose)
	
	print("Province headers: " + str(len(PROVINCE_HEADERS)))
	
	# In this, we loop through each year; each year has a separate datastructure
	# At the end of processing the data for that year, it is written out to the file
	for i, year in enumerate(years):
		currentyear = []
		columncursor = 0
		
		if(verbose==True):
			print "Now doing year: %s" % year
	
		# inits the currentyear database
		for province in provinces:
			newrow = []
		
			for s in range(len(PROVINCE_HEADERS)): 
				# appends the year
				if(s == 0):
					newrow.append(year)
				# appends the id
				elif(s == 1):
					newrow.append(province[0])
				# appends the name
				elif(s == 2):
					newrow.append(province[1])
				else:
					newrow.append(MISSING_VALUE)
			
			currentyear.append(newrow)
			
		for page in pages:
			if(verbose==True):
				print "\tNow doing page: %s" % page
			
			startcolumncursor = columncursor
			
			# sends the request
			values = {'code':page, 'dq':'', 'ayear':year}
			output = sendRequest(url, values, TX_HEADERS)
			
			# gets the rows and updates the column cursors
			rows, numcolumns = parseRows(output)
			columncursor = startcolumncursor + (numcolumns-1)
			
			# goes through the rows and copies the data to our year-database
			for row in rows:
			
				index = findRowIndex(currentyear, row[0], PROVINCE_NUM_HEADER_VARIABLES-1)
			
				if(index != -1):				
					for t in range(columncursor - startcolumncursor + 1):
						if(t == 0):
							# this is the name - we've already got that
							pass
						else:
							currentyear[index][t+PROVINCE_NUM_HEADER_VARIABLES+startcolumncursor-1] = row[t]
				else:
					print "Province not found in province database!"
					print "This is a serious error."
					print "Exiting."
					raise self.e
		

		if(multifile==True):
			enterData(currentyear, csvfiles[years.index(year)], [], year, PROVINCE_DATASET)
		else:
			enterData(currentyear, csvfiles[0], [], year, PROVINCE_DATASET)
	
# Gets urban data - this function and county do essentially the same thing
def getUrbanData(years, csvfiles, verbose, multifile):

	processSubProvinceData(years, csvfiles, verbose, URBAN_DATASET, multifile)

# Gets prefecture-level data - this function is similar to county and urban pages; hence, this function	
def getPrefectureData(years, csvfiles, verbose, multifile):

	processSubProvinceData(years, csvfiles, verbose, PREFECTURE_DATASET, multifile)
		
##########################################################
################### START OF MAIN CODE ###################
##########################################################

####
#### INITIALIZATION CODE - 1. get command line flags 2. initialize the cookie system to allow logging into the All China Data Center 3. Initialize the .csv file(s)
####

# The variables that describe how the program should operate
dataset = ""
years = ""
multifile = ""
verbose = ""

# Reading command line arguments
dataset, years, multifile, verbose = parseArguments(sys.argv[1:])

if(verbose==True):
	print "\nStarting program by initializing cookies and files"


## COOKIE INITIALIZATION
# initializes cookiejar and opener
urlopen = urllib2.urlopen
request = urllib2.Request
cj = cookielib.LWPCookieJar()

# loads old cookies
if os.path.isfile(COOKIEFILE):
     	# if we have a cookie file already saved
        # then load the cookies into the Cookie Jar
        cj.load(COOKIEFILE)

# installs cookiejar
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

# opens the CSV file
csvfiles = []
csvfiles = initCSV(dataset, years, multifile)

###
### RUNTIME CODE - the main goal here is to log in, then dispatch the actual handling of getting the data to dataset-specific functions
###

try:
	txdata = ''	
	
	if(verbose==True):
		print "Logging in..."
		
	output = sendRequest(LOGIN_URL, '', TX_HEADERS)

	# Checking to see if the login worked
	if re.search(LOGIN_FAIL, output):
		print "Login failed!\nMake sure you are a licensed user or connected to your university's network\n"
		sys.exit()
	elif(verbose==True):
		print "Login successful!"
	
	# This is necessary because sometimes the server doesn't seem to like quickly repeated connection attempts
	if(verbose==True):
		print "Waiting for server to free up connection (this will take %s seconds)\n" % WAIT_TIME
	time.sleep(WAIT_TIME)

	# Actually switches between the functions that do all of the data gathering work
	if(dataset==COUNTY_DATASET):
		getCountyData(years, csvfiles, verbose, multifile)
	elif(dataset==NATIONAL_DATASET):
		getNationalData(years, csvfiles, verbose, multifile)
	elif(dataset==PROVINCE_DATASET):
		getProvinceData(years, csvfiles, verbose, multifile)
	elif(dataset==URBAN_DATASET):
		getUrbanData(years, csvfiles, verbose, multifile)
	elif(dataset==PREFECTURE_DATASET):
		getPrefectureData(years, csvfiles, verbose, multifile)

except IOError, e:
	print "We failed to open a page."
	if hasattr(e, 'code'):
		print "We failed with error code - %s." % e.code
	elif hasattr(e, 'reason'):
		print "The error object has the following 'reason' attribute :"
		print e.reason
		print "This usually means the server doesn't exist,"
		print "is down, or we don't have an internet connection."
	sys.exit()
		

	
else:
		print "Success! Data saved." 
		if(verbose==True):
			print "Now cleaning up after ourselves"

####
#### CLEANUP CODE
####
if cj is None:
	print "Number of cookies stored is 0; cleanup probably successful?"
else:
	if(verbose==True):
		print "Cleanup of login successful. Number of cookies stored: %s\n" % len(cj)
    	
	# save the cookies again
	cj.save(COOKIEFILE)           