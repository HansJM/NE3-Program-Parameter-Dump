# ==============================================================================
# nepgDump - Nord Electro 3 Program Parameter Dump
#
# Module:      nepgParser.py
# Description: Contains functions to extract program parameters
#              from NE3 program files 
#
# Author:      Hans Juergen Miks
#
# Date:        26.06.2024
# ==============================================================================
import collections

# ------------------------------------------------------------------------------
# Function:    getInt()
# Parameters:  msb   high byte
#              lsb   low byte
#              offs  number of lowest relevant bit
# Returns:     i     resulting 7 bit as integer value
#
# Description: Get integer value from 7 out of 16 bit with offset
# ------------------------------------------------------------------------------
def getInt(msb, lsb, offs):

    i = ((msb << (8-offs)) | (lsb >> offs)) & 0x7f

    return i

  
# ------------------------------------------------------------------------------
# Function:    parse()
# Parameters:  data       string of input data from NE3 program file
#              offs       data offset for different file formats
# Returns:     nepgParms  NE3 program parameters
#
# Description: parse NE3 program file contents and store parameters
# ------------------------------------------------------------------------------
def parse(data, offs):

    # NE3 program parameters
    nepgParms = collections.OrderedDict([('progLoc', ''), ('progName', ''), ('instr', ''), ('pianoCategory', ''), ('pianoModel', ''), ('clavEq', ''),\
        ('organModel', ''), ('organDrawbars#1', ''), ('organVib#1', ''), ('organPerc#1', ''), ('organDrawbars#2', ''), ('organVib#2', ''), ('organPerc#2', ''),\
        ('organRotarySpeed', ''), ('organPresetSplit', ''), ('sampleNo', ''), ('sampleEnv', ''), ('eff1Type', ''), ('eff1Rate', ''), ('eff2Type', ''),\
        ('eff2Rate', ''), ('spkCompType', ''), ('spkCompRate', ''), ('revType', ''), ('revMix', ''), ('eqState', ''), ('eqBassGain', ''), ('eqMidFreq', ''),\
        ('eqMidGain', ''), ('eqTrebleGain', ''), ('progGain', '')])

    # Program location (0x0e, mask 0xff)
    b = data[0x0e]
    nepgParms['progLoc'] = str((b+2)//2)
    if b%2 == 0:
        nepgParms['progLoc'] += 'A'
    else:
        nepgParms['progLoc'] += 'B'
  
    # Instrument, Piano category and Organ model
    #   data[0x10] & 0x1f:
    #     0x0e: Sample Lib
    #     0x12: Organ, B3
    #     0x13: Organ, Farf
    #     0x14: Organ, Vox
    #     0x15: Piano, Grand
    #     0x16: Piano, Upright
    #     0x17: Piano, EPiano
    #     0x18: Piano, Wurl
    #     0x19: Piano, Clav/Hps
    instruments = ['Sample Lib', '', '', '', 'Organ', 'Organ', 'Organ', 'Piano', 'Piano', 'Piano', 'Piano', 'Piano', '', '', '', '', '', '']
    pianoCategories = ['', '', '', '', '', '', '', 'Grand', 'Upright', 'EPiano', 'Wurl', 'Clav/Hps', '', '', '', '', '', '']
    organModels = ['', '', '', '', 'B3', 'Farf', 'Vox', '', '', '', '', '', '', '', '', '', '', '']
    i = (data[0x10] & 0x1f) - 0x0e
    nepgParms['instr'] = instruments[i]
    if nepgParms['instr'] == 'Piano':
        nepgParms['pianoCategory'] = pianoCategories[i]
    elif nepgParms['instr'] == 'Organ':
        nepgParms['organModel'] = organModels[i]
  
    if nepgParms['instr'] == 'Piano':
        if nepgParms['pianoCategory'] == 'Grand':
            # Grand Piano model
            #   (data[0x51] & 0x1f) | (data[0x52] & 0xc0)
            nepgParms['pianoModel'] = str(((data[0x51+offs] & 0x1f) << 2) | ((data[0x52+offs] & 0xc0) >> 6) + 1)
    
        elif nepgParms['pianoCategory'] == 'Upright':
            # Upright Piano model
            #   (data[0x52] & 0x3f) | (data[0x53] & 0x80)
            nepgParms['pianoModel'] = str(((data[0x52+offs] & 0x3f) << 1) | ((data[0x53+offs] & 0x80) >> 7) + 1)

        elif nepgParms['pianoCategory'] == 'EPiano':
            # EPiano model
            #   data[0x53] & 0x7f
            nepgParms['pianoModel'] = str((data[0x53+offs] & 0x7f) + 1)
    
        elif nepgParms['pianoCategory'] == 'Wurl':
            # Wurlitzer Piano model
            #   data[0x54] & 0xfe
            nepgParms['pianoModel'] = str(((data[0x54+offs] & 0xfe) >> 1) + 1)

        elif nepgParms['pianoCategory'] == 'Clav/Hps':
            # Clavinet/Harpsichord model
            #   (data[0x54] & 0x01) | (data[0x55] & 0xfc)
            nepgParms['pianoModel'] = str(((data[0x54+offs] & 0x01) << 7) | ((data[0x55+offs] & 0xfc) >> 2) + 1)

            # Clavinet filter settings
            #   data[0x57] & 0xf0:
            #     0x10: Soft
            #     0x20: Medium
            #     0x40: Treble
            #     0x80: Brilliant
            clavEqSettings = ['Off', 'Soft', 'Med', 'Soft/Med', 'Treb', 'Soft + Treb', 'Med + Treb', 'Soft/Med + Treb',\
                'Brill', 'Soft + Brill', 'Med + Brill', 'Soft/Med + Brill', 'Treb/Brill', 'Soft + Treb/Brill', 'Med + Treb/Brill', 'Soft/Med + Treb/Brill']
            i = (data[0x57+offs] & 0xf0) >> 4
            nepgParms['clavEq'] = clavEqSettings[i]
  
    elif nepgParms['instr'] == 'Organ':
        if nepgParms['organModel'] == 'B3':
            # B3 Drawbars
            #   1/Lo       / 2/Up
            #   data[0x2d] / data[0x3f] & 0xf0: Sub
            #   data[0x2d] / data[0x3f] & 0x0f: Sub3
            #   data[0x2e] / data[0x40] & 0xf0: Fund
            #   data[0x2e] / data[0x40] & 0x0f: 2nd
            #   data[0x2f] / data[0x41] & 0xf0: 3rd
            #   data[0x2f] / data[0x41] & 0x0f: 4th
            #   data[0x30] / data[0x42] & 0xf0: 5th
            #   data[0x30] / data[0x42] & 0x0f: 6th
            #   data[0x31] / data[0x43] & 0xf0: 8th
            nepgParms['organDrawbars#1'] = str((data[0x2d+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x2d+offs] & 0x0f)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x2e+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x2e+offs] & 0x0f)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x2f+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x2f+offs] & 0x0f)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x30+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x30+offs] & 0x0f)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x31+offs] & 0xf0) >> 4)
      
            nepgParms['organDrawbars#2'] = str((data[0x3f+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x3f+offs] & 0x0f)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x40+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x40+offs] & 0x0f)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x41+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x41+offs] & 0x0f)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x42+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x42+offs] & 0x0f)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x43+offs] & 0xf0) >> 4)
      
            # B3 Vibrato/Chorus
            #   1/Lo       / 2/Up
            #   data[0x37] / data[0x49] & 0x08:
            #     0x00: Off
            #     0x08: On
            #   data[0x37] / data[0x49] & 0x70:
            #     0x00: V1
            #     0x10: C1
            #     0x20: V2
            #     0x30: C2
            #     0x40: V3
            #     0x50: C3
            organVibSettings = ['V1', 'C1', 'V2', 'C2', 'V3', 'C3', '', '']
            if data[0x37+offs] & 0x08:
                i = (data[0x37+offs] & 0x70) >> 4
                nepgParms['organVib#1'] = organVibSettings[i]
            else:
                nepgParms['organVib#1'] = 'Off'

            if data[0x49+offs] & 0x08:
                i = (data[0x49+offs] & 0x70) >> 4
                nepgParms['organVib#2'] = organVibSettings[i]
            else:
                nepgParms['organVib#2'] = 'Off'

            # B3 Percussion
            #   1/Lo       / 2/Up
            #   data[0x38] / data[0x4a] & 0x08:
            #     0x00: Off
            #     0x08: On
            #   data[0x38] / data[0x4a] & 0x10:
            #     0x00: Third off (Second)
            #     0x10: Third on
            #   data[0x38] / data[0x4a] & 0x60:
            #     0x00: Soft
            #     0x20: None
            #     0x40: Soft/Fast
            #     0x60: Fast
            organPercSettings = ['Soft', 'Soft + Third', '', 'Third', 'Soft/Fast', 'Soft/Fast + Third', 'Fast', 'Fast + Third']
            if data[0x38+offs] & 0x08:
                i = (data[0x38+offs] & 0x70) >> 4
                nepgParms['organPerc#1'] = organPercSettings[i]
            else:
                nepgParms['organPerc#1'] = 'Off'

            if data[0x4a+offs] & 0x08:
                i = (data[0x4a+offs] & 0x70) >> 4
                nepgParms['organPerc#2'] = organPercSettings[i]
            else:
                nepgParms['organPerc#2'] = 'Off'

            # B3 Preset/Split
            #   data[0x23] & 0x20:
            #     0x00: Split off
            #     0x20: Split on
            #   data[0x24] & 0x20:
            #     0x00: 1/Lo
            #     0x20: 2/Up
            organPresetSplitSettings = ['1/Lo', '2/Up', '1/Lo + Split', '2/Up + Split']
            i = ((data[0x23+offs] & 0x20) >> 4) | ((data[0x24+offs] & 0x20) >> 5)
            nepgParms['organPresetSplit'] = organPresetSplitSettings[i]
      
        elif nepgParms['organModel'] == 'Farf':
            # Farfisa Drawbars
            #   1/Lo       / 2/Up
            #   data[0x36] / data[0x48] & 0x80: Bass16
            #   data[0x36] / data[0x48] & 0x40: Str16
            #   data[0x36] / data[0x48] & 0x20: Flute8
            #   data[0x36] / data[0x48] & 0x10: Oboe8
            #   data[0x36] / data[0x48] & 0x08: Trmp8
            #   data[0x36] / data[0x48] & 0x04: Str8
            #   data[0x36] / data[0x48] & 0x02: Flute4
            #   data[0x36] / data[0x48] & 0x01: Str4
            #   data[0x37] / data[0x49] & 0x80: 2 2/3
            nepgParms['organDrawbars#1'] = str((data[0x36+offs] & 0x80) >> 7)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x40) >> 6)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x20) >> 5)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x10) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x08) >> 3)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x04) >> 2)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x02) >> 1)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x36+offs] & 0x01)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x37+offs] & 0x80) >> 7)

            nepgParms['organDrawbars#2'] = str((data[0x48+offs] & 0x80) >> 7)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x40) >> 6)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x20) >> 5)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x10) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x08) >> 3)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x04) >> 2)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x02) >> 1)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x48+offs] & 0x01)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x49+offs] & 0x80) >> 7)

            # Farfisa Vibrato
            #   1/Lo       / 2/Up
            #   data[0x38] / data[0x4a] & 0x80:
            #     0x00: Off
            #     0x80: On
            #   data[0x37] / data[0x49] & 0x03:
            #     0x00: Light1
            #     0x01: Heavy1
            #     0x02: Light2
            #     0x03: Heavy2
            organVibSettings = ['Light1', 'Heavy1', 'Light2', 'Heavy2']
            if data[0x38+offs] & 0x80:
                i = data[0x37+offs] & 0x03
                nepgParms['organVib#1'] = organVibSettings[i]
            else:
                nepgParms['organVib#1'] = 'Off'
      
            if data[0x4a+offs] & 0x80:
                i = data[0x49+offs] & 0x03
                nepgParms['organVib#2'] = organVibSettings[i]
            else:
                nepgParms['organVib#2'] = 'Off'
      
            # Farfisa Preset/Split
            #   data[0x23] & 0x20:
            #     0x00: Split off
            #     0x20: Split on
            #   data[0x24] & 0x08:
            #     0x00: 1/Lo
            #     0x08: 2/Up
            organPresetSplitSettings = ['1/Lo', '2/Up', '1/Lo + Split', '2/Up + Split']
            i = ((data[0x23+offs] & 0x20) >> 4) | ((data[0x24+offs] & 0x08) >> 3)
            nepgParms['organPresetSplit'] = organPresetSplitSettings[i]

        elif nepgParms['organModel'] == 'Vox':
            # Vox Drawbars
            #   1/Lo       / 2/Up
            #   data[0x31] / data[0x43] & 0x0f: 16'
            #   data[0x32] / data[0x44] & 0xf0: 8'
            #   data[0x32] / data[0x44] & 0x0f: 4'
            #   data[0x33] / data[0x45] & 0xf0: 2'
            #   data[0x33] / data[0x45] & 0x0f: II
            #   data[0x34] / data[0x46] & 0xf0: III
            #   data[0x34] / data[0x46] & 0x0f: IV
            #   data[0x35] / data[0x47] & 0xf0: Sine
            #   data[0x35] / data[0x47] & 0x0f: Triangle
            nepgParms['organDrawbars#1'] = str(data[0x31+offs] & 0x0f)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x32+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x32+offs] & 0x0f)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x33+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x33+offs] & 0x0f)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x34+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x34+offs] & 0x0f)
            nepgParms['organDrawbars#1'] += ' - ' + str((data[0x35+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#1'] += ' - ' + str(data[0x35+offs] & 0x0f)

            nepgParms['organDrawbars#2'] = str(data[0x43+offs] & 0x0f)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x44+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x44+offs] & 0x0f)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x45+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x45+offs] & 0x0f)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x46+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x46+offs] & 0x0f)
            nepgParms['organDrawbars#2'] += ' - ' + str((data[0x47+offs] & 0xf0) >> 4)
            nepgParms['organDrawbars#2'] += ' - ' + str(data[0x47+offs] & 0x0f)

            # Vox Vibrato/Chorus
            #   1/Lo       / 2/Up
            #   data[0x37] / data[0x49] & 0x04:
            #     0x00: Off
            #     0x04: On
            if data[0x37+offs] & 0x04:
                nepgParms['organVib#1'] = 'On'
            else:
                nepgParms['organVib#1'] = 'Off'

            if data[0x49+offs] & 0x04:
                nepgParms['organVib#2'] = 'On'
            else:
                nepgParms['organVib#2'] = 'Off'

            # Vox Preset/Split
            #   data[0x23] & 0x20:
            #     0x00: Split off
            #     0x20: Split on
            #   data[0x24] & 0x10:
            #     0x00: 1/Lo
            #     0x10: 2/Up
            organPresetSplitSettings = ['1/Lo', '2/Up', '1/Lo + Split', '2/Up + Split']
            i = ((data[0x23+offs] & 0x20) >> 4) | ((data[0x24+offs] & 0x10) >> 4)
            nepgParms['organPresetSplit'] = organPresetSplitSettings[i]

    elif nepgParms['instr'] == 'Sample Lib':
        # Sample Number
        #   data[0x56] & 0xf8
        nepgParms['sampleNo'] = ((data[0x56+offs] & 0xf8) >> 3) + 1

        # Sample Environment settings (Release / Attack/Velocity Dynamic)
        #   data[0x57..0x58] & 0x0180:
        #     0x0000: Off
        #     0x0080: Rel1
        #     0x0100: Rel2
        #     0x0180: Rel3
        #   data[0x57..0x58] & 0x0600:
        #     0x0200: SlowAt
        #     0x0400: VelDyn
        #     0x0600: SlowAt/VelDyn
        sampleEnvSettings = ['Off', 'Rel1', 'Rel2', 'Rel3', 'SlowAt', 'Rel1 + SlowAt', 'Rel2 + SlowAt', 'Rel3 + SlowAT',\
            'VelDyn', 'Rel1 + VelDyn', 'Rel2 + VelDyn', 'Rel3 + VelDyn', 'SlowAt/VelDyn', 'Rel1 + SlowAt/VelDyn', 'Rel2 + SlowAt/VelDyn', 'Rel3 + SlowAt/VelDyn']
        i = ((data[0x57+offs] << 1) | (data[0x58+offs] >> 7)) & 0x0f
        nepgParms['sampleEnv'] = sampleEnvSettings[i]

    # Effect 1
    #   Organ      / Piano, Sample Lib
    #   data[0x70] / data[0x7b] & 0x40:
    #     0x00: Off
    #     0x40: On
    #   data[0x63] & 0x1e:
    #     0x00: Trem1
    #     0x02: Trem2
    #     0x04: Trem3
    #     0x06: Pan1
    #     0x08: Pan2
    #     0x0a: Pan3
    #     0x0c: A-Wa
    #     0x0e: P-Wa 
    #     0x10: RM
    #   data[0x62..0x63] & 0x0fe0: Rate
    if (nepgParms['instr'] == 'Organ') and (data[0x70+offs] & 0x40) or\
        (nepgParms['instr'] == 'Piano') and (data[0x7b+offs] & 0x40) or\
        (nepgParms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x40):
        eff1Types = ['Trem1', 'Trem2', 'Trem3', 'Pan1', 'Pan2', 'Pan3', 'A-Wa', 'P-Wa', 'RM', '', '', '', '', '', '', '']
        i = (data[0x63+offs] & 0x1e) >> 1
        nepgParms['eff1Type'] = eff1Types[i]
  
        i = getInt(data[0x62+offs], data[0x63+offs], 5)
        nepgParms['eff1Rate'] = round(i * 10.0 / 0x7f, 1)
    else:
        nepgParms['eff1Type'] = 'Off'
  
    # Effect 2
    #   Organ      / Piano, Sample Lib
    #   data[0x70] / data[0x7b] & 0x20:
    #     0x00: Off
    #     0x20: On
    #   data[0x64..0x65] & 0x03c0:
    #     0x0000: Phas1
    #     0x0040: Phas2
    #     0x0080: Phas3
    #     0x00c0: Flang1
    #     0x0100: Flang2
    #     0x0140: Flang3
    #     0x0180: Chor1
    #     0x01c0: Chor2
    #     0x0200: Chor3
    #   data[0x63..0x64] & 0x01fc00: Rate
    if (nepgParms['instr'] == 'Organ') and (data[0x70+offs] & 0x20) or\
        (nepgParms['instr'] == 'Piano') and (data[0x7b+offs] & 0x20) or\
        (nepgParms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x20):
        eff2Types = ['Phas1', 'Phas2', 'Phas3', 'Flang1', 'Flang2', 'Flang3', 'Chor1', 'Chor2', 'Chor3', '', '', '', '', '', '', '']
        i = ((data[0x64+offs] << 2) | (data[0x65+offs] >> 6)) & 0x0f
        nepgParms['eff2Type'] = eff2Types[i]

        i = getInt(data[0x63+offs], data[0x64+offs], 2)
        nepgParms['eff2Rate'] = round(i * 10.0 / 0x7f, 1)
    else:
        nepgParms['eff2Type'] = 'Off'

    # Speaker/Comp
    #   Organ      / Piano, Sample Lib
    #   data[0x70] / data[0x7b] & 0x10:
    #     0x00: Off
    #     0x10: On
    #   data[0x66] & 0x0070:
    #     0x00: Small
    #     0x01: JC
    #     0x02: Twin
    #     0x03: Comp
    #     0x04: Rotary
    #   data[0x65..0x66] & 0x3f80: Rate
    if (nepgParms['instr'] == 'Organ') and (data[0x70+offs] & 0x10) or\
        (nepgParms['instr'] == 'Piano') and (data[0x7b+offs] & 0x10) or\
        (nepgParms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x10):
        spkCompTypes = ['Small', 'JC', 'Twin', 'Comp', 'Rotary', '', '', '']
        i = (data[0x66+offs] & 0x70) >> 4
        nepgParms['spkCompType'] = spkCompTypes[i]
  
        i = getInt(data[0x65+offs], data[0x66+offs], 7)
        nepgParms['spkCompRate'] = round(i * 10.0 / 0x7f, 1)
    else:
        nepgParms['spkCompType'] = 'Off'

    # Reverb
    #   Organ      / Piano, Sample Lib
    #   data[0x70] / data[0x7b] & 0x08:
    #     0x00: Off
    #     0x08: On
    #   data[0x67] & 0x001c:
    #     0x00: Room
    #     0x04: Stage
    #     0x08: Hall
    #     0x0c: Stage Soft
    #     0x10: Hall Soft
    #   data[0x66..0x67] & 0x0fe0: Mix
    if (nepgParms['instr'] == 'Organ') and (data[0x70+offs] & 0x08) or\
        (nepgParms['instr'] == 'Piano') and (data[0x7b+offs] & 0x08) or\
        (nepgParms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x08):
        revTypes = ['Room', 'Stage', 'Hall', 'Stage Soft', 'Hall Soft', '', '', '']
        i = (data[0x67+offs] & 0x1c) >> 2
        nepgParms['revType'] = revTypes[i]
   
        i = getInt(data[0x66+offs], data[0x67+offs], 5)
        nepgParms['revMix'] = round(i * 10.0 / 0x7f, 1)
    else:
        nepgParms['revType'] = 'Off'

    # Equalizer
    #   Organ      / Piano, Sample Lib
    #   data[0x70] / data[0x7b] & 0x80:
    #     0x00: Off
    #     0x80: On
    #   data[0x5f..0x62]:
    #     & 0xfe000000: Bass Gain
    #     & 0x01fc0000: Mid Freq
    #     & 0x0003f800: Mid Gain
    #     & 0x000007f0: Treble Gain
    if (nepgParms['instr'] == 'Organ') and (data[0x70+offs] & 0x80) or\
        (nepgParms['instr'] == 'Piano') and (data[0x7b+offs] & 0x80) or\
        (nepgParms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x80):
        nepgParms['eqState'] = 'On'

        i = (data[0x5f+offs] >> 1) & 0x7f
        nepgParms['eqBassGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
  
        i = getInt(data[0x5f+offs], data[0x60+offs], 2)
        if i < 64:
            freq = pow(10, i * 0.699/63 + 2.301)
        else:
            freq = pow(10, (i-64) * 0.903/63 + 3.0)
        nepgParms['eqMidFreq'] = int(round(freq/10) * 10)
  
        i = getInt(data[0x60+offs], data[0x61+offs], 3)
        nepgParms['eqMidGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
  
        i = getInt(data[0x61+offs], data[0x62+offs], 4)
        nepgParms['eqTrebleGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
    else:
        nepgParms['eqState'] = 'Off'
  
    if nepgParms['instr'] == 'Organ':
        # Organ Rotary Speed
        #   active only if Speaker/Comp is on and type = Rotary
        #   data[0x68] & 0x06:
        #     0x00: Slow/Stop
        #     0x02: Fast
        #     0x04: Stop Mode + Slow/Stop
        #     0x06: Stop Mode + Fast
        if nepgParms['spkCompType'] == 'Rotary':
            organRotarySettings = ['Slow/Stop', 'Fast', 'Stop Mode + Slow/Stop', 'Stop Mode + Fast']
            i = (data[0x68+offs] & 0x06) >> 1
            nepgParms['organRotarySpeed'] = organRotarySettings[i]
        else:
            nepgParms['organRotarySpeed'] = 'Off'

    # Program Gain
    #   data[0x67..0x68] & 0x03f8: Gain
    i = getInt(data[0x67+offs], data[0x68+offs], 3)
    nepgParms['progGain'] = round(i * 10.0 / 0x7f, 1)

    return nepgParms