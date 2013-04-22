#!/usr/bin/python
# Name: neopi.py
# Description: Utility to scan a file path for encrypted and obfuscated files
# Authors: Ben Hagen (ben.hagen@neohapsis.com)
#         Scott Behrens (scott.behrens@neohapsis.com)
#
# Date: 11/4/2010
#
# pep-0008 - Is stupid. TABS FO'EVER!

# Try catch regular expressions/bad path/bad filename/bad regex/

# Library imports
import math
import sys
import os
import re
import csv
import zlib
import time
from collections import defaultdict
from optparse import OptionParser

#
# Globals
#
   
# Smallest filesize to checkfor in bytes.  
SMALLEST = 1 # change this back!
# percentage deviation before alarm will sound
DEVIATION_THRESH = 1.2

#base class for all tests
class Test:
   def calculate(self,data,filename):
       print "In parent's calculate, this should have been overridden by child!)"

   def __init__(self):
       # highIsBad means the higher the metric, the more suspicious it is
       self.highIsBad = True

   # chops the file's data into blocks and calculates the metric on each
   # block and only return the highest (or lowest). this achieves finer granularity.
   def blockCalculate(self, blocksize, data, filename):
       noB = int(math.ceil(float(len(data))/blocksize))
       maxEntropy = -9999
       minEntropy = 9999
       j = 0
       pos = 0
       for i in range(noB):
	    Blockdata = data[j:j+blocksize]
	    j=j+blocksize
	    if(self.highIsBad == True):
		    if(maxEntropy <= self.calculate(Blockdata,filename)):
		        maxEntropy = self.calculate(Blockdata,filename)
                        pos = i * blocksize
	    if(self.highIsBad == False):
		    if(minEntropy > self.calculate(Blockdata,filename)):
		         minEntropy = self.calculate(Blockdata,filename)
                         pos = i * blocksize
       if(self.highIsBad == True):
          self.results.append({"filename":filename, "value":maxEntropy, "position":pos})
          return {"value":maxEntropy, "position":pos}
       else:
          self.results.append({"filename":filename, "value":minEntropy, "position":pos})
          return {"value":minEntropy, "position":pos}

   def calcMean(self):
       resTotal = 0
       for res in self.results:
           resTotal += res["value"]
       self.mean = resTotal / len(self.results)

   # this assumes that mean has been calculated
   def calcStdDev(self):
       squareTotal = 0
       for res in self.results:
           squareTotal += math.pow(res["value"] - self.mean, 2)
       self.stddev = math.sqrt(squareTotal / len(self.results))

   # this scans through results to see if any files are alarming
   # it works by comparing their deviation to the standard deviation
   # this method depends on the function isDeviant
   def flagAlarm(self):

       self.calcMean()
       self.calcStdDev()

       flagList = []
       for res in self.results:
           # current value deviates more than a threshold amount of standard deviation
	   if dist(res["value"], self.mean) > (DEVIATION_THRESH)*self.stddev:
               # check that the deviation is in the correct "direction"
               # for example, we don't care when a file has very low entropy, we only care when it's very high
	       if (self.highIsBad and res["value"] > self.mean) or (not self.highIsBad and res["value"] < self.mean):
		   percentage = dist(res["value"], self.mean)/ self.stddev if self.stddev > 0 else float("inf")
		   res["percentage"] = percentage
		   flagList.append(res)

       # sort and print out the flagged results
       flagList.sort(key=lambda item: item["percentage"])
       for res in flagList:
	   print ' {0:>7.4f}       {1}'.format(res["percentage"], res["filename"])


class LanguageIC(Test):
   """Class that calculates a file's Index of Coincidence as
   as well as a a subset of files average Index of Coincidence.
   """
   def __init__(self):
       """Initialize results arrays as well as character counters."""
       self.char_count =  defaultdict(int)
       self.total_char_count = 0
       self.results = []
       self.ic_total_results = ""
       self.highIsBad = False


   def calculate_char_count(self,data):
       """Method to calculate character counts for a particular data file."""
       if not data:
           return 0
       for x in range(256):
           char = chr(x)
           charcount = data.count(char)
           self.char_count[char] += charcount
           self.total_char_count += charcount
       return

   def calculate_IC(self):
       """Calculate the Index of Coincidence for the self variables"""
       total = 0
       for val in self.char_count.values():

           if val == 0:
               continue
           total += val * (val-1)

       try:
           ic_total =      float(total)/(self.total_char_count * (self.total_char_count - 1))
       except:
           ic_total = 0
       self.ic_total_results = ic_total
       return

   def calculate(self,data,filename):
       """Calculate the Index of Coincidence for a file and append to self.ic_results array"""
       if not data or (len(data)==1):
           return 0
       char_count = 0
       total_char_count = 0

       for x in range(256):
           char = chr(x)
           charcount = data.count(char)
           char_count += charcount * (charcount - 1)
           total_char_count += charcount
       ic = float(char_count)/(total_char_count * (total_char_count - 1))
       if not options.block_mode:
           self.results.append({"filename":filename, "value":ic})
       # Call method to calculate_char_count and append to total_char_count
       self.calculate_char_count(data)
       return ic

   def sort(self):
       self.results.sort(key=lambda item: item["value"])
       self.results = resultsAddRank(self.results)

   def printer(self, count):
       """Print the top signature count match files for a given search"""
       # Calculate the Total IC for a Search
       self.calculate_IC()
       print "\n[[ Average IC for Search ]]"
       print self.ic_total_results
       print "\n[[ Top %i lowest IC files ]]" % (count)
       if (count > len(self.results)): count = len(self.results)
       if not options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}        {1}'.format(self.results[x]["value"], self.results[x]["filename"])
       if options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}   at byte number:{1}     {2}'.format(self.results[x]["value"], self.results[x]["position"], self.results[x]["filename"])
       return

class Entropy(Test):
   """Class that calculates a file's Entropy."""

   def __init__(self):
       """Instantiate the entropy_results array."""
       self.results = []
       self.highIsBad = True

   def calculate(self,data,filename):
       """Calculate the entropy for 'data' and append result to entropy_results array."""

       self.stripped_data =data.replace(' ', '')
       if not self.stripped_data:
           return 0
       entropy = 0
       for x in range(256):
           p_x = float(self.stripped_data.count(chr(x)))/len(self.stripped_data)
           if p_x > 0:
               entropy += - p_x * math.log(p_x, 2)
       if not options.block_mode:
            self.results.append({"filename":filename, "value":entropy})
       return entropy

   def sort(self):
       self.results.sort(key=lambda item: item["value"])
       self.results.reverse()
       self.results = resultsAddRank(self.results)

   def printer(self, count):
       """Print the top signature count match files for a given search"""
       print "\n[[ Top %i entropic files for a given search ]]" % (count)
       if (count > len(self.results)): count = len(self.results)
       if not options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}        {1}'.format(self.results[x]["value"], self.results[x]["filename"])
       if options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}   at byte number:{1}     {2}'.format(self.results[x]["value"], self.results[x]["position"], self.results[x]["filename"])
       return

class LongestWord(Test):
   """Class that determines the longest word for a particular file."""
   def __init__(self):
       """Instantiate the longestword_results array."""
       self.results = []
       self.highIsBad = True

   def calculate(self,data,filename):
       """Find the longest word in a string and append to longestword_results array"""
       if not data:
           return "", 0
       longest = 0
       longest_word = ""
       words = re.split("[\s,\n,\r]", data)
       if words:
           for word in words:
               length = len(word)
               if length > longest:
                   longest = length
                   longest_word = word
       if not options.block_mode:
           self.results.append({"filename":filename, "value":longest})
       return longest

   def sort(self):
       self.results.sort(key=lambda item: item["value"])
       self.results.reverse()
       self.results = resultsAddRank(self.results)

   def printer(self, count):
       """Print the top signature count match files for a given search"""
       print "\n[[ Top %i longest word files ]]" % (count)
       if (count > len(self.results)): count = len(self.results)
       if not options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}        {1}'.format(self.results[x]["value"], self.results[x]["filename"])
       if options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}   at byte number:{1}     {2}'.format(self.results[x]["value"], self.results[x]["position"], self.results[x]["filename"])
       return

class SignatureNasty(Test):
   """Generator that searches a given file for nasty expressions"""

   def __init__(self):
       """Instantiate the results array."""
       self.results = []
       self.highIsBad = True

   def calculate(self, data, filename):
       if not data:
           return "", 0
       # Lots taken from the wonderful post at http://stackoverflow.com/questions/3115559/exploitable-php-functions
       valid_regex = re.compile('(eval\(|file_put_contents|base64_decode|python_eval|exec\(|passthru|popen|proc_open|pcntl|assert\(|system\(|shell)', re.I)
       matches = re.findall(valid_regex, data)
       if not options.block_mode:       
           self.results.append({"filename":filename, "value":len(matches)})
       return len(matches)

   def sort(self):
       self.results.sort(key=lambda item: item["value"])
       self.results.reverse()
       self.results = resultsAddRank(self.results)

   def printer(self, count):
       """Print the top signature count match files for a given search"""
       print "\n[[ Top %i signature match counts ]]" % (count)
       if (count > len(self.results)): count = len(self.results)
       if not options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}        {1}'.format(self.results[x]["value"], self.results[x]["filename"])
       if options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}   at byte number:{1}     {2}'.format(self.results[x]["value"], self.results[x]["position"], self.results[x]["filename"])
       return

class SignatureSuperNasty(Test):
   """Generator that searches a given file for SUPER-nasty expressions (These are almost always bad!)"""

   def __init__(self):
       """Instantiate the results array."""
       self.results = []
       self.highIsBad = True

   def calculate(self, data, filename):
       if not data:
           return "", 0
       valid_regex = re.compile('(@\$_\[\]=|\$_=@\$_GET|\$_\[\+""\]=)', re.I)
       matches = re.findall(valid_regex, data)
       if not options.block_mode:
           self.results.append({"filename":filename, "value":len(matches)})
       return len(matches)

   def sort(self):
       self.results.sort(key=lambda item: item["value"])
       self.results.reverse()
       self.results = resultsAddRank(self.results)

   def printer(self, count):
       """Print the top signature count match files for a given search"""
       print "\n[[ Top %i SUPER-signature match counts (These are usually bad!) ]]" % (count)
       if (count > len(self.results)): count = len(self.results)
       if not options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}        {1}'.format(self.results[x]["value"], self.results[x]["filename"])
       if options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}   at byte number:{1}     {2}'.format(self.results[x]["value"], self.results[x]["position"], self.results[x]["filename"])
       return

class UsesEval(Test):
   """Generator that searches a given file for nasty eval with variable"""

   def __init__(self):
      """Instantiate the eval_results array."""
      self.results = []
      self.highIsBad = True

   def calculate(self, data, filename):
      if not data:
               return "", 0
           # Lots taken from the wonderful post at http://stackoverflow.com/questions/3115559/exploitable-php-functions
      valid_regex = re.compile('(eval\(\$(\w|\d))', re.I)
      matches = re.findall(valid_regex, data)
      if not options.block_mode:
         self.results.append({"filename":filename, "value":len(matches)})
      return len(matches)

   def sort(self):
      self.results.sort(key=lambda item: item["value"])
      self.results.reverse()
      self.results = resultsAddRank(self.results)

   def printer(self, count):
      """Print the files that use eval"""
      print "\n[[ Top %i eval match counts ]]" % (count)
      if (count > len(self.results)): count = len(self.results)
      if not options.block_mode:
          for x in range(count):
              print ' {0:>7.4f}        {1}'.format(self.results[x]["value"], self.results[x]["filename"])
      if options.block_mode:
          for x in range(count):
              print ' {0:>7.4f}   at byte number:{1}     {2}'.format(self.results[x]["value"], self.results[x]["position"], self.results[x]["filename"])
      return


#currently this test is too expensive to be practical
class CharacterFreq(Test):
   """Class that calculates a file's Weighted Average of the Character Frequency."""

   def __init__(self):
       """Instantiate the entropy_results array."""
       self.results = []
       self.highIsBad = True

   def calculate(self,data,filename):
       if False: print "calculating frequecy for file: {}".format(filename)
       self.stripped_data =data.replace(' ', '')
       maxWordSize = min(len(self.stripped_data)/2, 40)
       highestoccurence = [0 for i in range(maxWordSize)]
       for wordsize in range(1, maxWordSize):
	   if False: print "checking wordsize = {}".format(wordsize)
           for y in range (len(self.stripped_data) - (wordsize)):
               word = self.stripped_data [y:y+wordsize]
	       numOccurences = self.stripped_data.count(word) - 1 # -1 so that it doesn't count itself
	       proportion = float(numOccurences) / (len(self.stripped_data) / (wordsize+1))
	       if False: print "checking for word = {}, found {} occurences with proportion = {}".format(word, numOccurences, proportion)
               if ((proportion) > highestoccurence[wordsize]):
                   highestoccurence[wordsize] = proportion
	   if False: print "for wordsize of {}, the highest is {}".format(wordsize, highestoccurence[wordsize])
           
       CharFreq = self.weightaverage(highestoccurence)
       if not options.block_mode:
           self.results.append({"filename":filename, "value":CharFreq})
       return CharFreq

   def weightaverage(self, highoccurence):
       print "highoccurence is {}".format(highoccurence)
       print "highoccurence has length: {}".format(len(highoccurence))
       mySum = 0
       numerator = 0
       for i in range(len(highoccurence)):
            mySum += i+1
            numerator+= (i+1)*highoccurence[i]
       if False: print "numerator / sum = {}/{}".format(numerator, mySum)
       WA = float(numerator)/mySum
       if False: print "weightaverage is: {}".format(WA)
       return WA

   def sort(self):
       self.results.sort(key=lambda item: item["value"])
       self.results.reverse()
       self.results = resultsAddRank(self.results)

   def printer(self, count):
       """Print the top files for a given search"""
       print "\n[[ Top %i Character Frequent files for a given search ]]" % (count)
       if (count > len(self.results)): count = len(self.results)
       if not options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}        {1}'.format(self.results[x]["value"], self.results[x]["filename"])
       if options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}   at byte number:{1}     {2}'.format(self.results[x]["value"], self.results[x]["position"], self.results[x]["filename"])
       return

class Compression(Test):
   """Generator finds compression ratio"""

   def __init__(self):
       """Instantiate the results array."""
       self.results = []
       self.highIsBad = True

   def calculate(self, data, filename):
       if not data:
           return "", 0
       compressed = zlib.compress(data)
       ratio = float(len(compressed)) / float(len(data))
       if not options.block_mode:
          self.results.append({"filename":filename, "value":ratio})
       return ratio

   def sort(self):
       self.results.sort(key=lambda item: item["value"])
       self.results.reverse()
       self.results = resultsAddRank(self.results)

   def printer(self, count):
       """Print the top files for a given search"""
       print "\n[[ Top %i compression match counts ]]" % (count)
       if (count > len(self.results)): count = len(self.results)
       if not options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}        {1}'.format(self.results[x]["value"], self.results[x]["filename"])
       if options.block_mode:
           for x in range(count):
               print ' {0:>7.4f}   at byte number:{1}     {2}'.format(self.results[x]["value"], self.results[x]["position"], self.results[x]["filename"])
       return

#tags each element of array with its ranking under attribute name "rank"
def resultsAddRank(results):
   rank = 1
   offset = 1
   previousValue = False
   newList = []
   for file in results:
       if (previousValue and previousValue != file["value"]):
           rank = offset
       file["rank"] = rank
       newList.append(file)
       previousValue = file["value"]
       offset = offset + 1
   return newList

# returns the distance between 2 numbers
def dist(x,y):
    return math.fabs(x-y)

class SearchFile:
   """Generator that searches a given filepath with an optional regular
   expression and returns the filepath and filename"""
   def __init__(self, follow_symlinks):
       self.follow_symlinks = follow_symlinks
   def search_file_path(self, args, valid_regex):
       for root, dirs, files in os.walk(args[0], followlinks=self.follow_symlinks):
           for file in files:
               filename = os.path.join(root, file)
               if (valid_regex.search(file) and os.path.getsize(filename) > SMALLEST):
                   try:
	               if False: print "opening file as {}".format(file)
                       data = open(root + "/" + file, 'rb').read()
	               if False: print "got data as {}".format(data)
                   except:
                       data = False
                       print "Could not read file :: %s/%s" % (root, file)
                   yield data, filename

if __name__ == "__main__":
   """Parse all the options"""

   timeStart = time.clock()

   print """
       )         (   (
    ( /(         )\ ))\ )
    )\())  (    (()/(()/(
   ((_)\  ))\ (  /(_))(_))
    _((_)/((_))\(_))(_))
   | \| (_)) ((_) _ \_ _|
   | .` / -_) _ \  _/| |
   |_|\_\___\___/_| |___| Ver. *.USEGIT
   """

   parser = OptionParser(usage="usage: %prog [options] <start directory> <OPTIONAL: filename regex>",
                         version="%prog 1.0")
   parser.add_option("-c", "--csv",
                     action="store",
                     dest="is_csv",
                     default=False,
                     help="generate CSV outfile",
                     metavar="FILECSV")
   parser.add_option("-a", "--all",
                     action="store_true",
                     dest="is_all",
                     default=False,
                     help="Run all (useful) tests [Entropy, Longest Word, IC, Signature]",)
   parser.add_option("-z", "--zlib",
                     action="store_true",
                     dest="is_zlib",
                     default=False,
                     help="Run compression Test",)
   parser.add_option("-e", "--entropy",
                     action="store_true",
                     dest="is_entropy",
                     default=False,
                     help="Run entropy Test",)
   parser.add_option("-E", "--eval",
                     action="store_true",
                     dest="is_eval",
                     default=False,
                     help="Run signiture test for the eval",)
   parser.add_option("-l", "--longestword",
                     action="store_true",
                     dest="is_longest",
                     default=False,
                     help="Run longest word test",)
   parser.add_option("-i", "--ic",
                     action="store_true",
                     dest="is_ic",
                     default=False,
                     help="Run IC test",)
   parser.add_option("-s", "--signature",
                     action="store_true",
                     dest="is_signature",
                     default=False,
                     help="Run signature test",)
   parser.add_option("-S", "--supersignature",
                     action="store_true",
                     dest="is_supersignature",
                     default=False,
                     help="Run SUPER-signature test",)
   parser.add_option("-A", "--auto",
                     action="store_true",
                     dest="is_auto",
                     default=False,
                     help="Run auto file extension tests",)
   parser.add_option("-u", "--unicode",
                     action="store_true",
                     dest="ignore_unicode",
                     default=False,
                     help="Skip over unicode-y/UTF'y files",)
   parser.add_option("-f", "--follow-links",
                     action="store_true",
                     dest="follow_symlinks",
                     default=False,
                     help="Follow symbolic links",)
   parser.add_option("-m", "--alarm-mode",
                     action="store_true",
                     dest="alarm_mode",
                     default=False,
                     help="Alarm mode outputs flags only files with high deviation",)

   parser.add_option("-b", "--block-mode",
                     action="store",
                     dest="block_mode",
                     default=False,
                     help="Block mode calculates the tests selected for the specified block sizes in each file",
                     metavar="blocksize")
   parser.add_option("-F", "--character-frequency",
                     action="store_true",
                     dest="is_CF",
                     default=False,
                     help="(Experimental) Run Character Frequency Test",)

   (options, args) = parser.parse_args()

   # Error on invalid number of arguements
   if len(args) < 1:
       parser.print_help()
       print ""
       sys.exit()

   # Error on an invalid path
   if os.path.exists(args[0]) == False:
       parser.error("Invalid path")

   valid_regex = ""
   if (len(args) == 2 and options.is_auto is False):
       try:
           valid_regex = re.compile(args[1])
       except:
           parser.error("Invalid regular expression")
   else:
       valid_regex = re.compile('.*')
   tests = []

   if options.is_auto:
       valid_regex = re.compile('(\.php|\.asp|\.aspx|\.scath|\.bash|\.zsh|\.csh|\.tsch|\.pl|\.py|\.txt|\.cgi|\.cfm|\.htaccess)$')

   if options.is_all:
       tests.append(LanguageIC())
       tests.append(Entropy())
       tests.append(LongestWord())
       tests.append(SignatureNasty())
       tests.append(SignatureSuperNasty())
   else:
       if options.is_entropy:
           tests.append(Entropy())
       if options.is_longest:
           tests.append(LongestWord())
       if options.is_ic:
           tests.append(LanguageIC())
       if options.is_signature:
           tests.append(SignatureNasty())
       if options.is_supersignature:
           tests.append(SignatureSuperNasty())
       if options.is_eval:
           tests.append(UsesEval())
       if options.is_zlib:
           tests.append(Compression())
       if options.is_CF:
           tests.append(CharacterFreq())

   # Instantiate the Generator Class used for searching, opening, and reading files
   locator = SearchFile(options.follow_symlinks)

   # CSV file output array
   csv_array = []
   csv_header = ["filename"]

   # Grab the file and calculate each test against file
   fileCount = 0
   fileIgnoreCount = 0
   for test in tests:
       csv_header.append(test.__class__.__name__)
       if options.block_mode:
           csv_header.append("position")

   for data, filename in locator.search_file_path(args, valid_regex):
       if data:
           # a row array for the CSV
           csv_row = []
           csv_row.append(filename)

           if options.ignore_unicode:
               asciiHighCount = 0
               for character in data:
                   if ord(character) > 127:
                       asciiHighCount = asciiHighCount + 1

               fileAsciiHighRatio = float(asciiHighCount) / float(len(data))

           if (options.ignore_unicode == False or fileAsciiHighRatio < .1):
               for test in tests:
                   if options.block_mode:
                      calculated_value = test.blockCalculate(int(options.block_mode),data, filename)
                   else:
                      calculated_value = test.calculate(data, filename)
                   # Make the header row if it hasn't been fully populated, +1 here to account for filename column
                   # possible optimization: move this into its own "for t in tests" loop?
                   if not options.block_mode:
                      csv_row.append(calculated_value)
                   else:
                      csv_row.append(calculated_value["value"])
                      csv_row.append(calculated_value["position"])
                   fileCount = fileCount + 1
               csv_array.append(csv_row)
           else:
               fileIgnoreCount = fileIgnoreCount + 1

   if options.is_csv:
       csv_array.insert(0,csv_header)
       fileOutput = csv.writer(open(options.is_csv, "wb"))
       fileOutput.writerows(csv_array)

   timeFinish = time.clock()

   # Print some stats
   print "\n[[ Total files scanned: %i ]]" % (fileCount)
   print "[[ Total files ignored: %i ]]" % (fileIgnoreCount)
   print "[[ Scan Time: %f seconds ]]" % (timeFinish - timeStart)

   # Print top rank lists
   rank_list = {}
   for test in tests:
       if (options.alarm_mode):
           print "Flagged files for: {}".format(test.__class__.__name__)
           test.flagAlarm()
       test.sort()
       test.printer(10)
       #compute the cumulative running total rank for all tests
       #all tests are given equal weightage
       for file in test.results:
	   rank_list[file["filename"]] = rank_list.setdefault(file["filename"], 0) + file["rank"]

   rank_sorted = sorted(rank_list.items(), key=lambda x: x[1])

   print "\n[[ Top cumulative ranked files ]]"
   #print top 10 (or fewer) files with the lowest cumulative ranks
   count = 10
   if (count > len(rank_sorted)): count = len(rank_sorted)
   for x in range(count):
       print ' {0:>7}        {1}'.format(rank_sorted[x][1], rank_sorted[x][0])
   
