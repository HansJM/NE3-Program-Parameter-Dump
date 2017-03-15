# ==============================================================================
# nepgDump - Nord Electro 3 Program Parameter Dump
#
# Module:      nepgParser.py
# Description: Contains functions to extract program parameters
#              from NE3 program files 
#
# Author:      Hans Juergen M.
# Date:        14.03.2017
# ==============================================================================
import collections

# ------------------------------------------------------------------------------
# Function:    getInt()
# Parameters:  msb     high byte
#              lsb     low byte
#              offset  number of lowest relevant bit
# Returns:     i       resulting 7 bit as integer value
#
# Description: Get integer value from 7 out of 16 bit with offset
# ------------------------------------------------------------------------------
def getInt(msb, lsb, offset):

  i = ((ord(msb) << (8-offset)) | (ord(lsb) >> offset)) & 0x7f

  return i

  
# ------------------------------------------------------------------------------
# Function:    parse()
# Parameters:  data       string of input data from NE3 program file
# Returns:     nepgParms  NE3 program parameters
#
# Description: parse NE3 program file contents and store parameters
# ------------------------------------------------------------------------------
def parse(data):

  # NE3 program parameters
  nepgParms = collections.OrderedDict([('progLoc', ''), ('progName', ''), ('instr', ''), ('pianoCategory', ''), ('pianoModel', ''), ('clavPickUp', ''),\
    ('clavEq', ''), ('organModel', ''), ('organDrawbars#1', ''), ('organVib#1', ''), ('organPerc#1', ''), ('organDrawbars#2', ''), ('organVib#2', ''),\
    ('organPerc#2', ''), ('organRotarySpeed', ''), ('organPresetSplit', ''), ('sampleNo', ''), ('sampleEnv', ''), ('eff1Type', ''), ('eff1Rate', ''),\
    ('eff2Type', ''), ('eff2Rate', ''), ('spkCompType', ''), ('spkCompRate', ''), ('revType', ''), ('revMix', ''), ('eqState', ''), ('eqBassGain', ''),\
    ('eqMidFreq', ''), ('eqMidGain', ''), ('eqTrebleGain', ''), ('progGain', '')])
  
  # Program location (0x0e, mask 0xff)
  b = ord(data[0x0e])
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
  i = (ord(data[0x10]) & 0x1f) - 0x0e
  nepgParms['instr'] = instruments[i]
  if nepgParms['instr'] == 'Piano':
    nepgParms['pianoCategory'] = pianoCategories[i]
  elif nepgParms['instr'] == 'Organ':
    nepgParms['organModel'] = organModels[i]
  
  if nepgParms['instr'] == 'Piano':
    # Piano model
    #   data[0x52] & 0xc0:
    #     0x00: Model 1
    #     0x40: Model 2
    #     0x80: Model 3
    pianoModels = [1, 2, 3, '']
    i = (ord(data[0x52]) & 0xc0) >> 6
    nepgParms['pianoModel'] = pianoModels[i]
    
    if nepgParms['pianoCategory'] == 'Clav/Hps':
      # Clavinet pick-up/Harpsichord model
      #   data[0x55] & 0x1c:
      #     0x00: CA, Model 1
      #     0x04: CB, Model 1
      #     0x08: DA, Model 1
      #     0x0c: DB, Model 1
      #     0x10: Model 2 (Harpsichord)
      clavPickUps = ['CA', 'CB', 'DA', 'DB']
      i = (ord(data[0x55]) & 0x1c) >> 2
      if i in [0, 1, 2, 3]:
        nepgParms['clavPickUp'] = clavPickUps[i]
        nepgParms['pianoModel'] = 1
      elif i == 4:
        nepgParms['pianoModel'] = 2
      
      # Clavinet filter settings
      #   data[0x57] & 0xf0:
      #     0x10: Soft
      #     0x20: Medium
      #     0x40: Treble
      #     0x80: Brilliant
      clavEqSettings = ['Off', 'Soft', 'Med', 'Soft/Med', 'Treb', 'Soft + Treb', 'Med + Treb', 'Soft/Med + Treb',\
        'Brill', 'Soft + Brill', 'Med + Brill', 'Soft/Med + Brill', 'Treb/Brill', 'Soft + Treb/Brill', 'Med + Treb/Brill', 'Soft/Med + Treb/Brill']
      i = (ord(data[0x57]) & 0xf0) >> 4
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
      nepgParms['organDrawbars#1'] = str((ord(data[0x2d]) & 0xf0) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x2d]) & 0x0f)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x2e]) & 0xf0) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x2e]) & 0x0f)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x2f]) & 0xf0) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x2f]) & 0x0f)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x30]) & 0xf0) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x30]) & 0x0f)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x31]) & 0xf0) >> 4)
      
      nepgParms['organDrawbars#2'] = str((ord(data[0x3f]) & 0xf0) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x3f]) & 0x0f)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x40]) & 0xf0) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x40]) & 0x0f)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x41]) & 0xf0) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x41]) & 0x0f)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x42]) & 0xf0) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x42]) & 0x0f)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x43]) & 0xf0) >> 4)
      
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
      if ord(data[0x37]) & 0x08:
        i = (ord(data[0x37]) & 0x70) >> 4
        nepgParms['organVib#1'] = organVibSettings[i]
      else:
        nepgParms['organVib#1'] = 'Off'

      if ord(data[0x49]) & 0x08:
        i = (ord(data[0x49]) & 0x70) >> 4
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
      if ord(data[0x38]) & 0x08:
        i = (ord(data[0x38]) & 0x70) >> 4
        nepgParms['organPerc#1'] = organPercSettings[i]
      else:
        nepgParms['organPerc#1'] = 'Off'

      if ord(data[0x4a]) & 0x08:
        i = (ord(data[0x4a]) & 0x70) >> 4
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
      organPresetSplitSettings = ['1/Lo', '2/Up', 'Split + 1/Lo', 'Split + 2/Up']
      i = ((ord(data[0x23]) & 0x20) >> 4) | ((ord(data[0x24]) & 0x20) >> 5)
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
      nepgParms['organDrawbars#1'] = str((ord(data[0x36]) & 0x80) >> 7)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x36]) & 0x40) >> 6)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x36]) & 0x20) >> 5)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x36]) & 0x10) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x36]) & 0x08) >> 3)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x36]) & 0x04) >> 2)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x36]) & 0x02) >> 1)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x36]) & 0x01)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x37]) & 0x80) >> 7)

      nepgParms['organDrawbars#2'] = str((ord(data[0x48]) & 0x80) >> 7)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x48]) & 0x40) >> 6)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x48]) & 0x20) >> 5)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x48]) & 0x10) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x48]) & 0x08) >> 3)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x48]) & 0x04) >> 2)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x48]) & 0x02) >> 1)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x48]) & 0x01)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x49]) & 0x80) >> 7)

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
      if ord(data[0x38]) & 0x80:
        i = ord(data[0x37]) & 0x03
        nepgParms['organVib#1'] = organVibSettings[i]
      else:
        nepgParms['organVib#1'] = 'Off'
      
      if ord(data[0x4a]) & 0x80:
        i = ord(data[0x49]) & 0x03
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
      organPresetSplitSettings = ['1/Lo', '2/Up', 'Split + 1/Lo', 'Split + 2/Up']
      i = ((ord(data[0x23]) & 0x20) >> 4) | ((ord(data[0x24]) & 0x08) >> 3)
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
      nepgParms['organDrawbars#1'] = str(ord(data[0x31]) & 0x0f)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x32]) & 0xf0) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x32]) & 0x0f)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x33]) & 0xf0) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x33]) & 0x0f)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x34]) & 0xf0) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x34]) & 0x0f)
      nepgParms['organDrawbars#1'] += ' - ' + str((ord(data[0x35]) & 0xf0) >> 4)
      nepgParms['organDrawbars#1'] += ' - ' + str(ord(data[0x35]) & 0x0f)

      nepgParms['organDrawbars#2'] = str(ord(data[0x43]) & 0x0f)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x44]) & 0xf0) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x44]) & 0x0f)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x45]) & 0xf0) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x45]) & 0x0f)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x46]) & 0xf0) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x46]) & 0x0f)
      nepgParms['organDrawbars#2'] += ' - ' + str((ord(data[0x47]) & 0xf0) >> 4)
      nepgParms['organDrawbars#2'] += ' - ' + str(ord(data[0x47]) & 0x0f)

      # Vox Vibrato/Chorus
      #   1/Lo       / 2/Up
      #   data[0x37] / data[0x49] & 0x04:
      #     0x00: Off
      #     0x04: On
      if ord(data[0x37]) & 0x04:
        nepgParms['organVib#1'] = 'On'
      else:
        nepgParms['organVib#1'] = 'Off'

      if ord(data[0x49]) & 0x04:
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
      organPresetSplitSettings = ['1/Lo', '2/Up', 'Split + 1/Lo', 'Split + 2/Up']
      i = ((ord(data[0x23]) & 0x20) >> 4) | ((ord(data[0x24]) & 0x10) >> 4)
      nepgParms['organPresetSplit'] = organPresetSplitSettings[i]

  elif nepgParms['instr'] == 'Sample Lib':
    # Sample Number
    #   data[0x56] & 0xf8
    nepgParms['sampleNo'] = ((ord(data[0x56]) & 0xf8) >> 3) + 1

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
    i = ((ord(data[0x57]) << 1) | (ord(data[0x58]) >> 7)) & 0x0f
    nepgParms['sampleEnv'] = sampleEnvSettings[i]

  # Effect 1
  #   data[0x7b] & 0x04:
  #     0x00: Off
  #     0x04: On
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
  if ord(data[0x7b]) & 0x40:  
    eff1Types = ['Trem1', 'Trem2', 'Trem3', 'Pan1', 'Pan2', 'Pan3', 'A-Wa', 'P-Wa', 'RM', '', '', '', '', '', '', '']
    i = (ord(data[0x63]) & 0x1e) >> 1
    nepgParms['eff1Type'] = eff1Types[i]
  
    i = getInt(data[0x62], data[0x63], 5)
    nepgParms['eff1Rate'] = round(i * 10.0 / 0x7f, 1)
  else:
    nepgParms['eff1Type'] = 'Off'
  
  # Effect 2
  #   data[0x7b] & 0x20:
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
  if (ord(data[0x7b]) & 0x20) > 0:  
    eff2Types = ['Phas1', 'Phas2', 'Phas3', 'Flang1', 'Flang2', 'Flang3', 'Chor1', 'Chor2', 'Chor3', '', '', '', '', '', '', '']
    i = ((ord(data[0x64]) << 2) | (ord(data[0x65]) >> 6)) & 0x0f
    nepgParms['eff2Type'] = eff2Types[i]

    i = getInt(data[0x63], data[0x64], 2)
    nepgParms['eff2Rate'] = round(i * 10.0 / 0x7f, 1)
  else:
    nepgParms['eff2Type'] = 'Off'

  # Speaker/Comp
  #   data[0x7b] & 0x10:
  #     0x00: Off
  #     0x10: On
  #   data[0x66] & 0x0070:
  #     0x00: Small
  #     0x01: JC
  #     0x02: Twin
  #     0x03: Comp
  #     0x04: Rotary
  #   data[0x65..0x66] & 0x3f80: Rate
  if (ord(data[0x7b]) & 0x10) == 0x10:  
    spkCompTypes = ['Small', 'JC', 'Twin', 'Comp', 'Rotary', '', '', '']
    i = (ord(data[0x66]) & 0x70) >> 4
    nepgParms['spkCompType'] = spkCompTypes[i]
  
    i = getInt(data[0x65], data[0x66], 7)
    nepgParms['spkCompRate'] = round(i * 10.0 / 0x7f, 1)
  else:
    nepgParms['spkCompType'] = 'Off'

  # Reverb
  #   data[0x7b] & 0x08:
  #     0x00: Off
  #     0x08: On
  #   data[0x67] & 0x001c:
  #     0x00: Room
  #     0x04: Stage
  #     0x08: Hall
  #     0x0c: Stage Soft
  #     0x10: Hall Soft
  #   data[0x66..0x67] & 0x0fe0: Mix
  if (ord(data[0x7b]) & 0x08) > 0:  
    revTypes = ['Room', 'Stage', 'Hall', 'Stage Soft', 'Hall Soft', '', '', '']
    i = (ord(data[0x67]) & 0x1c) >> 2
    nepgParms['revType'] = revTypes[i]
   
    i = getInt(data[0x66], data[0x67], 5)
    nepgParms['revMix'] = round(i * 10.0 / 0x7f, 1)
  else:
    nepgParms['revType'] = 'Off'

  # Equalizer
  #   data[0x7b] & 0x80:
  #     0x00: Off
  #     0x80: On
  #   0x5f..0x62 & 0xfe000000: Bass Gain
  #   0x5f..0x62 & 0x01fc0000: Mid Freq
  #   0x5f..0x62 & 0x0003f800: Mid Gain
  #   0x5f..0x62 & 0x000007f0: Treble Gain
  if (ord(data[0x7b]) & 0x80) > 0:  
    nepgParms['eqState'] = 'On'

    i = (ord(data[0x5f]) >> 1) & 0x7f
    nepgParms['eqBassGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
  
    i = getInt(data[0x5f], data[0x60], 2)
    if i < 64:
      freq = pow(10, i * 0.699/63 + 2.301)
    else:
      freq = pow(10, (i-64) * 0.903/63 + 3.0)
    nepgParms['eqMidFreq'] = int(round(freq/10) * 10)
  
    i = getInt(data[0x60], data[0x61], 3)
    nepgParms['eqMidGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
  
    i = getInt(data[0x61], data[0x62], 4)
    nepgParms['eqTrebleGain'] = round((i * 30.0 / 0x7f) - 15.0, 1)
  else:
    nepgParms['eqState'] = 'Off'
  
  # Program Gain
  #   data[0x67..0x68] & 0x03f8: Gain
  i = getInt(data[0x67], data[0x68], 3)
  nepgParms['progGain'] = round(i * 10.0 / 0x7f, 1)

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
      i = (ord(data[0x68]) & 0x06) >> 1
      nepgParms['organRotarySpeed'] = organRotarySettings[i]
    else:
      nepgParms['organRotarySpeed'] = 'Off'

  return nepgParms
