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
# Function:    get_int()
#
# Parameters:  msb   high byte
#              lsb   low byte
#              offs  number of lowest relevant bit
# Returns:     i     resulting 7 bit as integer value
#
# Description: Get integer value from 7 out of 16 bit with offset
# ------------------------------------------------------------------------------
def get_int(msb, lsb, offs):

    i = ((msb << (8-offs)) | (lsb >> offs)) & 0x7f

    return i

  
# ------------------------------------------------------------------------------
# Function:    parse()
#
# Parameters:  data        string of input data from NE3 program file
#              offs        data offset for different file formats
# Returns:     nepg_parms  NE3 program parameters
#
# Description: parse NE3 program file contents and store parameters
# ------------------------------------------------------------------------------
def parse(data, offs):

    # NE3 program parameters
    nepg_parms = collections.OrderedDict([('progLoc', ''), ('progName', ''), ('instr', ''), ('pianoCategory', ''), ('pianoModel', ''), ('clavEq', ''),\
        ('organModel', ''), ('organDrawbars#1', ''), ('organVib#1', ''), ('organPerc#1', ''), ('organDrawbars#2', ''), ('organVib#2', ''), ('organPerc#2', ''),\
        ('organRotarySpeed', ''), ('organPresetSplit', ''), ('sampleNo', ''), ('sampleEnv', ''), ('eff1Type', ''), ('eff1Rate', ''), ('eff2Type', ''),\
        ('eff2Rate', ''), ('spkCompType', ''), ('spkCompRate', ''), ('revType', ''), ('revMix', ''), ('eqState', ''), ('eqBassGain', ''), ('eqMidFreq', ''),\
        ('eqMidGain', ''), ('eqTrebleGain', ''), ('progGain', '')])

    # Program location (0x0e, mask 0xff)
    b = data[0x0e]
    nepg_parms['progLoc'] = str((b+2)//2)
    if b%2 == 0:
        nepg_parms['progLoc'] += 'A'
    else:
        nepg_parms['progLoc'] += 'B'
  
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
    piano_categories = ['', '', '', '', '', '', '', 'Grand', 'Upright', 'EPiano', 'Wurl', 'Clav/Hps', '', '', '', '', '', '']
    organ_models = ['', '', '', '', 'B3', 'Farf', 'Vox', '', '', '', '', '', '', '', '', '', '', '']
    i = (data[0x10] & 0x1f) - 0x0e
    nepg_parms['instr'] = instruments[i]
    if nepg_parms['instr'] == 'Piano':
        nepg_parms['pianoCategory'] = piano_categories[i]
    elif nepg_parms['instr'] == 'Organ':
        nepg_parms['organModel'] = organ_models[i]
  
    if nepg_parms['instr'] == 'Piano':
        if nepg_parms['pianoCategory'] == 'Grand':
            # Grand Piano model
            #   (data[0x51] & 0x1f) | (data[0x52] & 0xc0)
            nepg_parms['pianoModel'] = str(((data[0x51+offs] & 0x1f) << 2) | ((data[0x52+offs] & 0xc0) >> 6) + 1)
    
        elif nepg_parms['pianoCategory'] == 'Upright':
            # Upright Piano model
            #   (data[0x52] & 0x3f) | (data[0x53] & 0x80)
            nepg_parms['pianoModel'] = str(((data[0x52+offs] & 0x3f) << 1) | ((data[0x53+offs] & 0x80) >> 7) + 1)

        elif nepg_parms['pianoCategory'] == 'EPiano':
            # EPiano model
            #   data[0x53] & 0x7f
            nepg_parms['pianoModel'] = str((data[0x53+offs] & 0x7f) + 1)
    
        elif nepg_parms['pianoCategory'] == 'Wurl':
            # Wurlitzer Piano model
            #   data[0x54] & 0xfe
            nepg_parms['pianoModel'] = str(((data[0x54+offs] & 0xfe) >> 1) + 1)

        elif nepg_parms['pianoCategory'] == 'Clav/Hps':
            # Clavinet/Harpsichord model
            #   (data[0x54] & 0x01) | (data[0x55] & 0xfc)
            nepg_parms['pianoModel'] = str(((data[0x54+offs] & 0x01) << 7) | ((data[0x55+offs] & 0xfc) >> 2) + 1)

            # Clavinet filter settings
            #   data[0x57] & 0xf0:
            #     0x10: Soft
            #     0x20: Medium
            #     0x40: Treble
            #     0x80: Brilliant
            clav_eq_settings = ['Off', 'Soft', 'Med', 'Soft/Med', 'Treb', 'Soft + Treb', 'Med + Treb', 'Soft/Med + Treb',\
                'Brill', 'Soft + Brill', 'Med + Brill', 'Soft/Med + Brill', 'Treb/Brill', 'Soft + Treb/Brill', 'Med + Treb/Brill', 'Soft/Med + Treb/Brill']
            i = (data[0x57+offs] & 0xf0) >> 4
            nepg_parms['clavEq'] = clav_eq_settings[i]
  
    elif nepg_parms['instr'] == 'Organ':
        if nepg_parms['organModel'] == 'B3':
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
            nepg_parms['organDrawbars#1'] = str((data[0x2d+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x2d+offs] & 0x0f)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x2e+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x2e+offs] & 0x0f)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x2f+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x2f+offs] & 0x0f)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x30+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x30+offs] & 0x0f)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x31+offs] & 0xf0) >> 4)
      
            nepg_parms['organDrawbars#2'] = str((data[0x3f+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x3f+offs] & 0x0f)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x40+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x40+offs] & 0x0f)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x41+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x41+offs] & 0x0f)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x42+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x42+offs] & 0x0f)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x43+offs] & 0xf0) >> 4)
      
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
            organ_vib_settings = ['V1', 'C1', 'V2', 'C2', 'V3', 'C3', '', '']
            if data[0x37+offs] & 0x08:
                i = (data[0x37+offs] & 0x70) >> 4
                nepg_parms['organVib#1'] = organ_vib_settings[i]
            else:
                nepg_parms['organVib#1'] = 'Off'

            if data[0x49+offs] & 0x08:
                i = (data[0x49+offs] & 0x70) >> 4
                nepg_parms['organVib#2'] = organ_vib_settings[i]
            else:
                nepg_parms['organVib#2'] = 'Off'

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
            organ_perc_settings = ['Soft', 'Soft + Third', '', 'Third', 'Soft/Fast', 'Soft/Fast + Third', 'Fast', 'Fast + Third']
            if data[0x38+offs] & 0x08:
                i = (data[0x38+offs] & 0x70) >> 4
                nepg_parms['organPerc#1'] = organ_perc_settings[i]
            else:
                nepg_parms['organPerc#1'] = 'Off'

            if data[0x4a+offs] & 0x08:
                i = (data[0x4a+offs] & 0x70) >> 4
                nepg_parms['organPerc#2'] = organ_perc_settings[i]
            else:
                nepg_parms['organPerc#2'] = 'Off'

            # B3 Preset/Split
            #   data[0x23] & 0x20:
            #     0x00: Split off
            #     0x20: Split on
            #   data[0x24] & 0x20:
            #     0x00: 1/Lo
            #     0x20: 2/Up
            organ_preset_split_settings = ['1/Lo', '2/Up', '1/Lo + Split', '2/Up + Split']
            i = ((data[0x23+offs] & 0x20) >> 4) | ((data[0x24+offs] & 0x20) >> 5)
            nepg_parms['organPresetSplit'] = organ_preset_split_settings[i]
      
        elif nepg_parms['organModel'] == 'Farf':
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
            nepg_parms['organDrawbars#1'] = str((data[0x36+offs] & 0x80) >> 7)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x40) >> 6)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x20) >> 5)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x10) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x08) >> 3)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x04) >> 2)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x36+offs] & 0x02) >> 1)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x36+offs] & 0x01)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x37+offs] & 0x80) >> 7)

            nepg_parms['organDrawbars#2'] = str((data[0x48+offs] & 0x80) >> 7)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x40) >> 6)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x20) >> 5)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x10) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x08) >> 3)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x04) >> 2)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x48+offs] & 0x02) >> 1)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x48+offs] & 0x01)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x49+offs] & 0x80) >> 7)

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
            organ_vib_settings = ['Light1', 'Heavy1', 'Light2', 'Heavy2']
            if data[0x38+offs] & 0x80:
                i = data[0x37+offs] & 0x03
                nepg_parms['organVib#1'] = organ_vib_settings[i]
            else:
                nepg_parms['organVib#1'] = 'Off'
      
            if data[0x4a+offs] & 0x80:
                i = data[0x49+offs] & 0x03
                nepg_parms['organVib#2'] = organ_vib_settings[i]
            else:
                nepg_parms['organVib#2'] = 'Off'
      
            # Farfisa Preset/Split
            #   data[0x23] & 0x20:
            #     0x00: Split off
            #     0x20: Split on
            #   data[0x24] & 0x08:
            #     0x00: 1/Lo
            #     0x08: 2/Up
            organ_preset_split_settings = ['1/Lo', '2/Up', '1/Lo + Split', '2/Up + Split']
            i = ((data[0x23+offs] & 0x20) >> 4) | ((data[0x24+offs] & 0x08) >> 3)
            nepg_parms['organPresetSplit'] = organ_preset_split_settings[i]

        elif nepg_parms['organModel'] == 'Vox':
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
            nepg_parms['organDrawbars#1'] = str(data[0x31+offs] & 0x0f)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x32+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x32+offs] & 0x0f)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x33+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x33+offs] & 0x0f)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x34+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x34+offs] & 0x0f)
            nepg_parms['organDrawbars#1'] += ' - ' + str((data[0x35+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#1'] += ' - ' + str(data[0x35+offs] & 0x0f)

            nepg_parms['organDrawbars#2'] = str(data[0x43+offs] & 0x0f)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x44+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x44+offs] & 0x0f)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x45+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x45+offs] & 0x0f)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x46+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x46+offs] & 0x0f)
            nepg_parms['organDrawbars#2'] += ' - ' + str((data[0x47+offs] & 0xf0) >> 4)
            nepg_parms['organDrawbars#2'] += ' - ' + str(data[0x47+offs] & 0x0f)

            # Vox Vibrato/Chorus
            #   1/Lo       / 2/Up
            #   data[0x37] / data[0x49] & 0x04:
            #     0x00: Off
            #     0x04: On
            if data[0x37+offs] & 0x04:
                nepg_parms['organVib#1'] = 'On'
            else:
                nepg_parms['organVib#1'] = 'Off'

            if data[0x49+offs] & 0x04:
                nepg_parms['organVib#2'] = 'On'
            else:
                nepg_parms['organVib#2'] = 'Off'

            # Vox Preset/Split
            #   data[0x23] & 0x20:
            #     0x00: Split off
            #     0x20: Split on
            #   data[0x24] & 0x10:
            #     0x00: 1/Lo
            #     0x10: 2/Up
            organ_preset_split_settings = ['1/Lo', '2/Up', '1/Lo + Split', '2/Up + Split']
            i = ((data[0x23+offs] & 0x20) >> 4) | ((data[0x24+offs] & 0x10) >> 4)
            nepg_parms['organPresetSplit'] = organ_preset_split_settings[i]

    elif nepg_parms['instr'] == 'Sample Lib':
        # Sample Number
        #   data[0x56] & 0xf8
        nepg_parms['sampleNo'] = ((data[0x56+offs] & 0xf8) >> 3) + 1

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
        sample_env_settings = ['Off', 'Rel1', 'Rel2', 'Rel3', 'SlowAt', 'Rel1 + SlowAt', 'Rel2 + SlowAt', 'Rel3 + SlowAT',\
            'VelDyn', 'Rel1 + VelDyn', 'Rel2 + VelDyn', 'Rel3 + VelDyn', 'SlowAt/VelDyn', 'Rel1 + SlowAt/VelDyn', 'Rel2 + SlowAt/VelDyn', 'Rel3 + SlowAt/VelDyn']
        i = ((data[0x57+offs] << 1) | (data[0x58+offs] >> 7)) & 0x0f
        nepg_parms['sampleEnv'] = sample_env_settings[i]

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
    if (nepg_parms['instr'] == 'Organ') and (data[0x70+offs] & 0x40) or\
        (nepg_parms['instr'] == 'Piano') and (data[0x7b+offs] & 0x40) or\
        (nepg_parms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x40):
        eff1_types = ['Trem1', 'Trem2', 'Trem3', 'Pan1', 'Pan2', 'Pan3', 'A-Wa', 'P-Wa', 'RM', '', '', '', '', '', '', '']
        i = (data[0x63+offs] & 0x1e) >> 1
        nepg_parms['eff1Type'] = eff1_types[i]
  
        i = get_int(data[0x62+offs], data[0x63+offs], 5)
        nepg_parms['eff1Rate'] = round(i * 10.0 / 0x7f, 1)
    else:
        nepg_parms['eff1Type'] = 'Off'
  
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
    if (nepg_parms['instr'] == 'Organ') and (data[0x70+offs] & 0x20) or\
        (nepg_parms['instr'] == 'Piano') and (data[0x7b+offs] & 0x20) or\
        (nepg_parms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x20):
        eff2_types = ['Phas1', 'Phas2', 'Phas3', 'Flang1', 'Flang2', 'Flang3', 'Chor1', 'Chor2', 'Chor3', '', '', '', '', '', '', '']
        i = ((data[0x64+offs] << 2) | (data[0x65+offs] >> 6)) & 0x0f
        nepg_parms['eff2Type'] = eff2_types[i]

        i = get_int(data[0x63+offs], data[0x64+offs], 2)
        nepg_parms['eff2Rate'] = round(i * 10.0 / 0x7f, 1)
    else:
        nepg_parms['eff2Type'] = 'Off'

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
    if (nepg_parms['instr'] == 'Organ') and (data[0x70+offs] & 0x10) or\
        (nepg_parms['instr'] == 'Piano') and (data[0x7b+offs] & 0x10) or\
        (nepg_parms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x10):
        spk_comp_types = ['Small', 'JC', 'Twin', 'Comp', 'Rotary', '', '', '']
        i = (data[0x66+offs] & 0x70) >> 4
        nepg_parms['spkCompType'] = spk_comp_types[i]
  
        i = get_int(data[0x65+offs], data[0x66+offs], 7)
        nepg_parms['spkCompRate'] = round(i * 10.0 / 0x7f, 1)
    else:
        nepg_parms['spkCompType'] = 'Off'

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
    if (nepg_parms['instr'] == 'Organ') and (data[0x70+offs] & 0x08) or\
        (nepg_parms['instr'] == 'Piano') and (data[0x7b+offs] & 0x08) or\
        (nepg_parms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x08):
        rev_types = ['Room', 'Stage', 'Hall', 'Stage Soft', 'Hall Soft', '', '', '']
        i = (data[0x67+offs] & 0x1c) >> 2
        nepg_parms['revType'] = rev_types[i]
   
        i = get_int(data[0x66+offs], data[0x67+offs], 5)
        nepg_parms['revMix'] = round(i * 10.0 / 0x7f, 1)
    else:
        nepg_parms['revType'] = 'Off'

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
    if (nepg_parms['instr'] == 'Organ') and (data[0x70+offs] & 0x80) or\
        (nepg_parms['instr'] == 'Piano') and (data[0x7b+offs] & 0x80) or\
        (nepg_parms['instr'] == 'Sample Lib') and (data[0x7b+offs] & 0x80):
        nepg_parms['eqState'] = 'On'

        i = (data[0x5f+offs] >> 1) & 0x7f
        nepg_parms['eqBassGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
  
        i = get_int(data[0x5f+offs], data[0x60+offs], 2)
        if i < 64:
            freq = pow(10, i * 0.699/63 + 2.301)
        else:
            freq = pow(10, (i-64) * 0.903/63 + 3.0)
        nepg_parms['eqMidFreq'] = int(round(freq/10) * 10)
  
        i = get_int(data[0x60+offs], data[0x61+offs], 3)
        nepg_parms['eqMidGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
  
        i = get_int(data[0x61+offs], data[0x62+offs], 4)
        nepg_parms['eqTrebleGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
    else:
        nepg_parms['eqState'] = 'Off'
  
    if nepg_parms['instr'] == 'Organ':
        # Organ Rotary Speed
        #   active only if Speaker/Comp is on and type = Rotary
        #   data[0x68] & 0x06:
        #     0x00: Slow/Stop
        #     0x02: Fast
        #     0x04: Stop Mode + Slow/Stop
        #     0x06: Stop Mode + Fast
        if nepg_parms['spkCompType'] == 'Rotary':
            organ_rotary_settings = ['Slow/Stop', 'Fast', 'Stop Mode + Slow/Stop', 'Stop Mode + Fast']
            i = (data[0x68+offs] & 0x06) >> 1
            nepg_parms['organRotarySpeed'] = organ_rotary_settings[i]
        else:
            nepg_parms['organRotarySpeed'] = 'Off'

    # Program Gain
    #   data[0x67..0x68] & 0x03f8: Gain
    i = get_int(data[0x67+offs], data[0x68+offs], 3)
    nepg_parms['progGain'] = round(i * 10.0 / 0x7f, 1)

    return nepg_parms