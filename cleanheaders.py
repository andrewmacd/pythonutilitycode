#!/usr/bin/env python2.3
#
#  file: cleanheaders.py
#
#  purpose: strip out some useless header bits from chinadataonline.org scraping file
#
#  Created by Andrew Macdonald on 3/11/09.
#  Copyright (c) 2009 Andrew MacDonald. All rights reserved.


import re

def commaReplace(matchobj):
	return '\', \''

filein = open("prefecturepagecodes.txt")
fileout = open("prefecturepagecodes-reformed.txt", 'w')

filedata = filein.read()

fileout.write(re.sub(', ', commaReplace, filedata))
