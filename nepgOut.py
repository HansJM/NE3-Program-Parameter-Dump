# ==============================================================================
# nepgDump - Nord Electro 3 Program Parameter Dump
#
# Module:      nepgOut.py
# Description: Contains functions for screen and file output of
#              NE3 program parameters
#
# Author:      Hans Juergen Miks
#
# Date:        27.06.2024
# ==============================================================================
import csv

# ------------------------------------------------------------------------------
# Function:    printScreen()
#
# Parameters:  inFile     input file name
#              nepgParms  NE3 program parameters
# Returns:     -
#
# Description: prints program parameters stored in dictionary 'nepgParms'
#              to screen
# ------------------------------------------------------------------------------
def printScreen(inFile, nepgParms):

    # Assemble output string
    str = '\n+++++ {} +++++'.format(inFile)
    str += '\n\nProgram location: {}'.format(nepgParms['progLoc'])

    str += '\n\nInstrument:       {}'.format(nepgParms['instr'])
    if nepgParms['instr'] == 'Piano':
        str += '\n  Category:       {}'.format(nepgParms['pianoCategory'])
        str += '\n  Model:          {}'.format(nepgParms['pianoModel'])
        if nepgParms['pianoCategory'] == 'Clav/Hps':
            str += '\n  Clav EQ:        {}'.format(nepgParms['clavEq'])
    elif nepgParms['instr'] == 'Organ':
        str += ', {}'.format(nepgParms['organModel'])
        str += '\n1/Lo:'
        str += '\n  Drawbars:       {}'.format(nepgParms['organDrawbars#1'])
        str += '\n  Vibrato/Chorus: {}'.format(nepgParms['organVib#1'])
        if nepgParms['organModel'] == 'B3':
            str += '\n  Percussion:     {}'.format(nepgParms['organPerc#1'])
        str += '\n2/Up:'
        str += '\n  Drawbars:       {}'.format(nepgParms['organDrawbars#2'])
        str += '\n  Vibrato/Chorus: {}'.format(nepgParms['organVib#2'])
        if nepgParms['organModel'] == 'B3':
            str += '\n  Percussion:     {}'.format(nepgParms['organPerc#2'])
        str += '\nRotary Speed:     {}'.format(nepgParms['organRotarySpeed'])
        str += '\nPreset/Split:     {}'.format(nepgParms['organPresetSplit'])
    elif nepgParms['instr'] == 'Sample Lib':
        str += '\n  Sample No:      {}'.format(nepgParms['sampleNo'])
        str += '\n  Sample Env:     {}'.format(nepgParms['sampleEnv'])
  
    str += '\n'
    if nepgParms['eff1Type'] != 'Off':
        str += '\nEffect 1:         {}'.format(nepgParms['eff1Type'])
        str += '\n  Rate:           {}'.format(nepgParms['eff1Rate'])
    else:
        str += '\nEffect 1:         Off'
      
    if nepgParms['eff2Type'] != 'Off':
        str += '\nEffect 2:         {}'.format(nepgParms['eff2Type'])
        str += '\n  Rate:           {}'.format(nepgParms['eff2Rate'])
    else:
        str += '\nEffect 2:         Off'
      
    if nepgParms['spkCompType'] != 'Off':
        str += '\nSpeaker/Comp:     {}'.format(nepgParms['spkCompType'])
        str += '\n  Rate:           {}'.format(nepgParms['spkCompRate'])
    else:
        str += '\nSpeaker/Comp:     Off'
      
    if nepgParms['revType'] != 'Off':
        str += '\nReverb:           {}'.format(nepgParms['revType'])
        str += '\n  Mix:            {}'.format(nepgParms['revMix'])
    else:
        str += '\nReverb:           Off'
      
    if nepgParms['eqState'] == 'On':
        str += '\nEqualizer:'
        str += '\n  Bass Gain:      {} dB'.format(nepgParms['eqBassGain'])
        str += '\n  Mid Freq:       {} Hz'.format(nepgParms['eqMidFreq'])
        str += '\n  Mid Gain:       {} dB'.format(nepgParms['eqMidGain'])
        str += '\n  Treble Gain:    {} dB'.format(nepgParms['eqTrebleGain'])
    else:
        str += '\nEqualizer:        Off'

    str += '\n\nProgram Gain:     {}\n'.format(nepgParms['progGain'])
  
    print(str)
  
    return


# ------------------------------------------------------------------------------
# Write header line to .csv file
#
# Parameters:  fOut  file handle
# Returns:     -
#
# Description: Writes .csv header line
# ------------------------------------------------------------------------------
def writeCsvHeader(fOut):

    csvHeader = ['Location', 'Program Name', 'Instrument', 'Piano Category', 'Piano Model', 'Clav EQ',\
        'Organ Model', 'Organ Drawbars (1/Lo)', 'Vibrato/Chorus (1/Lo)', 'Percussion (1/Lo)', 'Organ Drawbars (2/Up)',\
        'Vibrato/Chorus (2/Up)', 'Percussion (2/Up)', 'Rotary Speed', 'Preset/Split', 'Sample No', 'Sample Env',\
        'Effect1', 'Rate', 'Effect2', 'Rate', 'Speaker/Comp', 'Rate', 'Reverb', 'Mix',\
        'Equalizer', 'Bass [dB]', 'Mid Freq [Hz]', 'Mid Gain [dB]', 'Treble [dB]', 'Program Gain']

    writer = csv.writer(fOut, delimiter=',')
    writer.writerow(csvHeader)

    return


# ------------------------------------------------------------------------------
# Write single line to .csv file
#
# Parameters:  fOut       file handle
#              nepgName   NE3 program name
#              nepgParms  NE3 program parameters
# Returns:     -
#
# Description: writes program parameters stored in dictionary 'nepgParms'
#              to .csv file
# ------------------------------------------------------------------------------
def writeCsvLine(fOut, nepgName, nepgParms):

    # Add a leading whitespace character to float numbers to force formatting as text in Excel
    for key, value in nepgParms.items():
        if isinstance(value, float):
            nepgParms[key] = ' ' + str(value)

    # Add program name to parameter list
    nepgParms['progName'] = nepgName

    writer = csv.writer(fOut, delimiter=',')
    writer.writerow(nepgParms.values())

    return