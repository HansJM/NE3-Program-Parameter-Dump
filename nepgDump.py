# ==============================================================================
# nepgDump - Nord Electro 3 Program Parameter Dump
#
# Module:      nepgDump.py (main module)
# Description: Python script to extract the program parameters from NE3 program
#              files and either print them to screen or write them to a .csv file
#              for import in Excel. The script is compatible with Python 2.7.
#
#              Usage: nepgDump.py [-h] [-d DST] [-f] SRC
#
#                SRC                source file (w/o ext) / src folder with option '-f'
#                -h, --help         show this help message and exit
#                -d DST, --dst DST  write results to <DST>.csv / <SRC>.csv with '-d $'
#                -f, --folder       process all .nepg files in folder <SRC>
#
# Version:     1.2
#
# Author:      Hans Juergen Miks
#
# History:     14.03.2017  Version 1.0  Initial Version
#              25.10.2017  Version 1.1  Evaluation of Piano models corrected,
#                                       Clavinet pick-up type removed since it cannot
#                                       be determined from .nepg file
#              17.06.2020  Version 1.2  Evaluation of Organ effect settings corrected,
#                                       Check for unsupported .nepg file format added,
#                                       Note: File format changed with unknown Nord
#                                       Sound Manager version above 7.10
#
# MIT License
#
# Copyright (c) 2020 HansJM
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================
import sys, os, argparse
import nepgParser, nepgOut

version = 1.2

print "\nnepgDump - Nord Electro 3 Program Parameter Dump, Vs {}".format(version)
print "========================================================\n"

# Parse and evaluate command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("SRC", help = "source file (w/o ext) / src folder with option '-f'")
parser.add_argument("-d", "--dst", help = "write results to <DST>.csv / <SRC>.csv with '-d $'")
parser.add_argument("-f", "--folder", help = "process all .nepg files in folder <SRC>", action = "store_true")
args = parser.parse_args()

inFolder = ''
inFiles = ''
outFile = ''

if args.folder:
  if os.path.isdir(args.SRC):
    inFolder = str(args.SRC)
    inFiles = os.listdir(str(args.SRC))
  else:
    print "Error: Directory '{}' not found".format(args.SRC)
    sys.exit()    
else:
  inFiles = [str(args.SRC) + '.nepg']

if args.dst == '$':
  outFile = str(args.SRC) + '.csv'
elif args.dst:
  outFile = str(args.dst) + '.csv'

# Prepare .csv output file, if specified
if outFile != '':
  fOut = open(outFile, 'wb')
  fOut.write('sep=,\n')
  nepgOut.writeCsvHeader(fOut)

# Process input file(s)
fileCount = 0
for inFile in inFiles:
  if inFile.endswith('.nepg'):
    fileCount += 1
    if inFolder != '':
      inPath = inFolder + '\\' + inFile
    else:
      inPath = inFile

    if os.path.isfile(inPath):
      fIn = open(inPath, 'rb')
      data = fIn.read()

      # Check for valid NE3 program file
      if (data[0x00:0x04] == 'CBIN') and (data[0x08:0x0c] == 'nepg'):
        # Check for supported file format
        if ord(data[0x04]) == 0:
          # Parse NE3 program file
          nepgParms = nepgParser.parse(data)
    
          if outFile == '':
            # Print results to screen 
            nepgOut.printScreen(inFile, nepgParms)
          else:
            # Write results to .csv file
            print "Processing file '{}'".format(inPath)
            nepgName, ext = os.path.splitext(os.path.basename(inPath))
            nepgOut.writeCsvLine(fOut, nepgName, nepgParms)
        else:
          print "Error: File '{}' comprises unsupported file format".format(inPath)
          print "(Note: File format changed with unknown Nord Sound Manager version above v7.10)"
      else:
        print "Error: File '{}' is not a valid NE3 program file".format(inPath)

      fIn.close()    
    else:
      print "Error: File '{}' not found".format(inPath)

if fileCount == 0:
  print "Error: No NE3 program files found"

if outFile != '':
  print "\n{} files processed and results written to '{}'".format(fileCount, outFile)
  fOut.close()