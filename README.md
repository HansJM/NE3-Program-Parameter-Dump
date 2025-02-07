# nepgDump - Nord Electro 3 Program Parameter Dump

## Purpose
This Python script extracts the parameter values from Nord Electro 3 program files and either prints them to screen or writes them to a .csv file for import in Excel. Single and multiple program files can be evaluated at once.

Knowledge of the program parameter settings, especially those not visualized on the NE3 panel, helps with modifying existing programs. It can be used for documentation purposes as well.

## Usage
For instructions on how to use the script see the following output created by typing `python nepgDump.py -h`:

```
usage: nepgDump.py [-h] [-d DST] [-f] SRC

positional arguments:
  SRC                source file (w/o ext) / src folder with option '-f'

optional arguments:
  -h, --help         show this help message and exit
  -d DST, --dst DST  write results to <DST>.csv / <SRC>.csv with '-d $'
  -f, --folder       process all .nepg files in folder <SRC>
```

## Contents
Here is a short description of all files contained in this folder:

File | Description
---- | -----------
nepgDump.py | NE3 dump script (main module)
nepgParser.py | Parser module (imported by main module)
nepgOut.py | Output module (imported by main module)
nepgDump.exe | Executable program
NE3 Template.xlsm | Empty Excel template
NE3 Program Parameters.xlsm | Example Excel table

## Requirements and compatibility
This Python script requires Python 3.x being installed on your computer. Previous versions of the script up to version 1.3 are compatible with Python 2.7.

The executable program nepgDump.exe (created from the script by using PyInstaller) can be executed on any Windows PC even without a Python installation.

The script has been tested by using Python 3.13 with NE3 program files created by the Nord Sound Manager v7.10 and v7.44 (new .nepg file format) and with several NE3 program files downloaded from the Nord Homepage.

## History
Date | Version | Release Notes
---- |:-------:| -------------
14.03.2017 | 1.0 | Initial Version  
25.10.2017 | 1.1 | Detection of Piano models corrected, Clavinet pick-up type removed since it cannot be determined from program file
17.06.2020 | 1.2 | Evaluation of Organ effect settings corrected
21.06.2020 | 1.3 | Support for new .nepg file format added
23.01.2025 | 1.4 | Migrated to Python 3.x, cosmetic changes

## Acknowledgement
Some basic ideas have been taken from a similar dump script for Nord Electro 4 program files. It has been written by Christian E. and can be found on GitHub here: https://github.com/10x10sw/NordUser/tree/master/DumpNE4P
