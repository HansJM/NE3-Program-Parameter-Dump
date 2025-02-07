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
# Version:     1.4
#
# Author:      Hans Juergen Miks
#
# History:     14.03.2017  Version 1.0  Initial Version
#              25.10.2017  Version 1.1  Evaluation of Piano models corrected,
#                                       Clavinet pick-up type removed since it cannot
#                                       be determined from .nepg file
#              17.06.2020  Version 1.2  Evaluation of Organ effect settings corrected,
#                                       check for unsupported .nepg file format added,
#                                       Note: File format changed with unknown Nord
#                                       Sound Manager version above 7.10
#              21.06.2020  Version 1.3  Support for new .nepg file format added
#              23.01.2025  Version 1.4  Migrated to Python 3.x, cosmetic changes
#
# MIT License
#
# Copyright (c) 2025 HansJM
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

version = 1.4

print("\nnepgDump - Nord Electro 3 Program Parameter Dump, Vs {}".format(version))
print("========================================================\n")

# Parse and evaluate command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("SRC", help = "source file (w/o ext) / src folder with option '-f'")
parser.add_argument("-d", "--dst", help = "write results to <DST>.csv / <SRC>.csv with '-d $'")
parser.add_argument("-f", "--folder", help = "process all .nepg files in folder <SRC>", action = "store_true")
args = parser.parse_args()

in_folder = ''
in_files = ''
out_file = ''

if args.folder:
    if os.path.isdir(args.SRC):
        in_folder = str(args.SRC)
        in_files = os.listdir(str(args.SRC))
    else:
        print("Error: Directory '{}' not found".format(args.SRC))
        sys.exit()    
else:
    in_files = [str(args.SRC) + '.nepg']

if args.dst == '$':
    out_file = str(args.SRC) + '.csv'
elif args.dst:
    out_file = str(args.dst) + '.csv'

# Prepare .csv output file, if specified
if out_file != '':
    f_out = open(out_file, 'w', newline='')
    f_out.write('sep=,\n')
    nepgOut.write_csv_header(f_out)

# Process input file(s)
file_count = 0
for in_file in in_files:
    if in_file.endswith('.nepg'):
        file_count += 1
        if in_folder != '':
          in_path = in_folder + '\\' + in_file
        else:
          in_path = in_file

        if os.path.isfile(in_path):
            f_in = open(in_path, 'rb')
            data = f_in.read()

            # Check for valid NE3 program file
            if (data[0x00:0x04] == b'CBIN') and (data[0x08:0x0c] == b'nepg'):
                # Check file format (data[0x04] = 0: initial file format; 1: new file format)
                if data[0x04] == 0x00:
                    offs = 0x00
                elif data[0x04] == 0x01:
                    offs = 0x14
                else:
                    # offs = 0xff indicates unknown file format
                    offs = 0xff

                if offs != 0xff:
                    # Parse NE3 program file
                    nepg_parms = nepgParser.parse(data, offs)
    
                    if out_file == '':
                        # Print results to screen 
                        nepgOut.print_screen(in_file, nepg_parms)
                    else:
                        # Write results to .csv file
                        print("Processing file '{}'".format(in_path))
                        nepg_name, ext = os.path.splitext(os.path.basename(in_path))
                        nepgOut.write_csv_line(f_out, nepg_name, nepg_parms)
                else:
                    print("Error: File '{}' comprises unsupported file format".format(in_path))
            else:
                print("Error: File '{}' is not a valid NE3 program file".format(in_path))

            f_in.close()    
        else:
          print("Error: File '{}' not found".format(in_path))

if file_count == 0:
    print("Error: No NE3 program files found")

if out_file != '':
    print("\n{} files processed and results written to '{}'".format(file_count, out_file))
    f_out.close()