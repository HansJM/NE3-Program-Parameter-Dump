# ==============================================================================
# nepgDump - Nord Electro 3 Program Parameter Dump
#
# Module:      nepgOut.py
# Description: Contains functions for screen and file output of
#              NE3 program parameters
#
# Author:      Hans Juergen Miks
#
# Date:        22.01.2025
# ==============================================================================
import csv

# ------------------------------------------------------------------------------
# Function:    print_screen()
#
# Parameters:  in_file     input file name
#              nepg_parms  NE3 program parameters
# Returns:     -
#
# Description: prints program parameters stored in dictionary 'nepg_parms'
#              to screen
# ------------------------------------------------------------------------------
def print_screen(in_file, nepg_parms):

    # Assemble output string
    str = '+++++ {} +++++'.format(in_file)
    str += '\n\nProgram location: {}'.format(nepg_parms['progLoc'])

    str += '\n\nInstrument:       {}'.format(nepg_parms['instr'])
    if nepg_parms['instr'] == 'Piano':
        str += '\n  Category:       {}'.format(nepg_parms['pianoCategory'])
        str += '\n  Model:          {}'.format(nepg_parms['pianoModel'])
        if nepg_parms['pianoCategory'] == 'Clav/Hps':
            str += '\n  Clav EQ:        {}'.format(nepg_parms['clavEq'])
    elif nepg_parms['instr'] == 'Organ':
        str += ', {}'.format(nepg_parms['organModel'])
        str += '\n1/Lo:'
        str += '\n  Drawbars:       {}'.format(nepg_parms['organDrawbars#1'])
        str += '\n  Vibrato/Chorus: {}'.format(nepg_parms['organVib#1'])
        if nepg_parms['organModel'] == 'B3':
            str += '\n  Percussion:     {}'.format(nepg_parms['organPerc#1'])
        str += '\n2/Up:'
        str += '\n  Drawbars:       {}'.format(nepg_parms['organDrawbars#2'])
        str += '\n  Vibrato/Chorus: {}'.format(nepg_parms['organVib#2'])
        if nepg_parms['organModel'] == 'B3':
            str += '\n  Percussion:     {}'.format(nepg_parms['organPerc#2'])
        str += '\nRotary Speed:     {}'.format(nepg_parms['organRotarySpeed'])
        str += '\nPreset/Split:     {}'.format(nepg_parms['organPresetSplit'])
    elif nepg_parms['instr'] == 'Sample Lib':
        str += '\n  Sample No:      {}'.format(nepg_parms['sampleNo'])
        str += '\n  Sample Env:     {}'.format(nepg_parms['sampleEnv'])
  
    str += '\n'
    if nepg_parms['eff1Type'] != 'Off':
        str += '\nEffect 1:         {}'.format(nepg_parms['eff1Type'])
        str += '\n  Rate:           {}'.format(nepg_parms['eff1Rate'])
    else:
        str += '\nEffect 1:         Off'
      
    if nepg_parms['eff2Type'] != 'Off':
        str += '\nEffect 2:         {}'.format(nepg_parms['eff2Type'])
        str += '\n  Rate:           {}'.format(nepg_parms['eff2Rate'])
    else:
        str += '\nEffect 2:         Off'
      
    if nepg_parms['spkCompType'] != 'Off':
        str += '\nSpeaker/Comp:     {}'.format(nepg_parms['spkCompType'])
        str += '\n  Rate:           {}'.format(nepg_parms['spkCompRate'])
    else:
        str += '\nSpeaker/Comp:     Off'
      
    if nepg_parms['revType'] != 'Off':
        str += '\nReverb:           {}'.format(nepg_parms['revType'])
        str += '\n  Mix:            {}'.format(nepg_parms['revMix'])
    else:
        str += '\nReverb:           Off'
      
    if nepg_parms['eqState'] == 'On':
        str += '\nEqualizer:'
        str += '\n  Bass Gain:      {} dB'.format(nepg_parms['eqBassGain'])
        str += '\n  Mid Freq:       {} Hz'.format(nepg_parms['eqMidFreq'])
        str += '\n  Mid Gain:       {} dB'.format(nepg_parms['eqMidGain'])
        str += '\n  Treble Gain:    {} dB'.format(nepg_parms['eqTrebleGain'])
    else:
        str += '\nEqualizer:        Off'

    str += '\n\nProgram Gain:     {}\n'.format(nepg_parms['progGain'])
  
    print(str)
  
    return


# ------------------------------------------------------------------------------
# Function:    write_csv_header()
#
# Parameters:  f_out  file handle
# Returns:     -
#
# Description: Writes .csv header line
# ------------------------------------------------------------------------------
def write_csv_header(f_out):

    csv_header = ['Location', 'Program Name', 'Instrument', 'Piano Category', 'Piano Model', 'Clav EQ',\
        'Organ Model', 'Organ Drawbars (1/Lo)', 'Vibrato/Chorus (1/Lo)', 'Percussion (1/Lo)', 'Organ Drawbars (2/Up)',\
        'Vibrato/Chorus (2/Up)', 'Percussion (2/Up)', 'Rotary Speed', 'Preset/Split', 'Sample No', 'Sample Env',\
        'Effect1', 'Rate', 'Effect2', 'Rate', 'Speaker/Comp', 'Rate', 'Reverb', 'Mix',\
        'Equalizer', 'Bass [dB]', 'Mid Freq [Hz]', 'Mid Gain [dB]', 'Treble [dB]', 'Program Gain']

    writer = csv.writer(f_out, delimiter=',')
    writer.writerow(csv_header)

    return


# ------------------------------------------------------------------------------
# Function:    write_csv_line()
#
# Parameters:  f_out       file handle
#              nepg_name   NE3 program name
#              nepg_parms  NE3 program parameters
# Returns:     -
#
# Description: writes program parameters stored in dictionary 'nepg_parms'
#              to a single line in .csv file
# ------------------------------------------------------------------------------
def write_csv_line(f_out, nepg_name, nepg_parms):

    # Add a leading whitespace character to float numbers to force formatting as text in Excel
    for key, value in nepg_parms.items():
        if isinstance(value, float):
            nepg_parms[key] = ' ' + str(value)

    # Add program name to parameter list
    nepg_parms['progName'] = nepg_name

    writer = csv.writer(f_out, delimiter=',')
    writer.writerow(nepg_parms.values())

    return