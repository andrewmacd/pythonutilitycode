# file: ches-dataedit.py
#
# purpose: recode several household characteristics in the CHES dataset, depending on option selected
#
# created by: Andrew MacDonald on 5/31/16.
#
# copyright: (c) 2016 Andrew MacDonald. All rights reserved.
# email: andrewwm@gmail.com

import pandas as pd
import numpy as np
import math

####
#### GLOBAL VARIABLES
####

RELATIONSHIP = 'a3'
SPOUSE = 1
HOUSEHOLD_HEAD = 16

####
#### FUNCTIONS
####

def findWorkingAged(hhlist):

    print('Find working aged')

def assignSpouseCharacteristics(hhlist):

    #print("Spouse Characteristics")
    experience = np.nan
    exp2 = np.nan
    yearsofschool = np.nan
    mando = np.nan
    partystatus = np.nan

    spouse = hhlist.loc[hhlist[RELATIONSHIP]==SPOUSE]

    # There are some Muslim households with multiple wives. Edge case and we just take first wife
    spouse = spouse.head(1)

    if(spouse.empty==False):

        # There are some outliers in the dataset, we'll set them to NaN
        if (spouse.c12.values[0] < 115):
            # Good values
            if(spouse.c12.values[0] >= 0):
                yearsofschool = spouse.c12.values[0]
            else:
                print('Low')
        if (spouse.c12.values[0]>=115):
            print('High')

        # Make sure yearsofschool is valid
        if(pd.notnull(yearsofschool)):
            # Defined as age-years of school-6
            experience = spouse.a5.values[0] - yearsofschool - 6

        # If experience isn't NaN, calculate exp^2
        if(pd.notnull(experience)):
            exp2 = math.pow(experience, 2)

        # Set Mandarin ability
        if(pd.notnull(spouse.c6.values[0])):

            # Fluent in Mandarin
            if(spouse.c6.values[0]==1):
                mando=1
            # Less than fluent
            elif(spouse.c6.values[0]==2):
                mando = 2
            elif(spouse.c6.values[0]==3):
                mando = 2
            elif(spouse.c6.values[0]==4):
                mando=2
            else:
                print('Out of range mando is: ' + str(spouse.c6.values[0]))

        # Set party status
        if(pd.notnull(spouse.a10.values[0])):

            if(spouse.a10.values[0]==1):
                partystatus = 2
            elif(spouse.a10.values[0]==2):
                partystatus = 2
            elif(spouse.a10.values[0]==3):
                partystatus = 2
            elif(spouse.a10.values[0]==4):
                partystatus = 1
            else:
                print('Out of range party status is: ' + str(spouse.a10.values[0]))

    else:
        # No spouse
        experience = 0
        exp2 = 0
        yearsofschool = 0
        # Default is not a party member
        partystatus = 1

        husband = hhlist.loc[hhlist[RELATIONSHIP]==HOUSEHOLD_HEAD]

        # Set mando equal to husband status if no spouse
        if(husband.c6.values[0]==1):
            mando = 1
        elif(husband.c6.values[0] == 2):
            mando = 2
        elif(husband.c6.values[0] == 3):
            mando = 2
        elif(husband.c6.values[0] == 4):
            mando = 2
        else:
            print('Out of range mando is: ' +  str(husband.c6.values[0]))

    # Assign necessary values
    for i in hhlist.index:
        hhlist['spouseexperience'][i] = experience
        hhlist['spouseexp2'][i] = exp2
        hhlist['spouseeducation'][i] = yearsofschool
        hhlist['spousemando'][i] = mando
        hhlist['spouseparty'][i] = partystatus

    return hhlist

def assignWifeCharateristics(hhlist):

    print('Wife characteristics')

def assignHouseholdCharacteristics(hhlist):

    print("Household Characteristics")

def assignHouseholdOldestMale(hhlist):

    print("Household Oldest Male Assignment")

def assignHousehold():

    print("Household [other]")

##########################################################
################### START OF MAIN CODE ###################
##########################################################

# Open the input file
minorities = pd.io.parsers.read_csv('urbanminorities.csv', sep=',', encoding='utf-8')

# Get the number of unique surveys conducted
uniquecodes = pd.unique(minorities.qumn.ravel())
n = 0
p = 0
q = 0
r = 0
s = 0

for i in uniquecodes:

    hhold = assignSpouseCharacteristics(minorities.loc[minorities['qumn']==i])

    minorities.loc[minorities['qumn'] == i] = hhold

    #print('Spouse experience\n' + str(minorities.loc[minorities['qumn']==i, 'spouseexperience']))

    zerocheck = minorities[minorities['qumn']==i].head(1)

    #print('Final spouse education is: ' + str(zerocheck['spouseeducation'].values[0]))
    #print(zerocheck['spouseexperience'])
    #print(zerocheck['spouseexp2'])

    if(pd.notnull(zerocheck['spouseeducation'].values[0])):
        n = n+1
        #print('N is: ' + str(n))

    if(pd.notnull(zerocheck['spouseexperience'].values[0])):

        p = p+1
        #print('P is: ' + str(p))

        if(pd.notnull(zerocheck['spouseexp2'].values[0])):
             q = q+1
             #print('Q is: ' + str(q))

    if(pd.notnull(zerocheck['spousemando'].values[0])):

        r = r+1
        #print('R is: ' + str(r))

    if(pd.notnull(zerocheck['spouseparty'].values[0])):

        s = s+1
        #print('S is: ' + str(s))


print('N is: ' + str(n))
print('P is: ' + str(p))
print('Q is: ' + str(q))
print('R is: ' + str(r))
print('S is: ' + str(s))

minorities.to_csv('urban-minorities-spouse.csv')
