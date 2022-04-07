midi = __import__('midi')
t = __import__('tools')
from sdenums import Button, buttonNames
from collections import Mapping, Collection
import copy

EST         = 0xF0
ensoniqID   = 0x0F
vfxFamilyID = 0x05
sdID        = 0x00
EOX         = 0xF7


class SD():
  def __init__(self, inputID, outputID, debug=False, logParameterChanges=False):
    self.input  = midi.getMidiInputDevice(inputID)
    self.output = midi.getMidiOutputDevice(outputID)
    
    self.channel = 0
    self.decoupled = False

    self.updateGUI = False
    self.debug = debug
    self.logParameterChanges = logParameterChanges
    self.transNormal =        '┌─T  '
    self.transNoExpNormal =   '  T  '
    self.transDecoupled =        '┌─I  '
    self.transNoExpDecoupled =   '  I  '
    self.trans = self.transNormal
    self.transNoExp = self.transNoExpNormal
    self.alrt =         '└──//── '
    self.info =         '├────── '
    self.recv =         '└──R '
    self.endNoRecv =    '└────── '
    self.linebreakRecv = True
    
    self.operationQueue = []
    self.runningOperation = False
    self.receivedResponse = False
    
    #Initial SD1 parameters
    voiceParams = {
      'modMixer': {
        'pageOffset': 0,
        'modSource1': [0, 1, 15],
        'modSource2': [0, 2, 15],
        'scaler': [0, 4, 0],
        'shape': [0, 5, 0]
      },
      'wave': {
        'pageOffset': 1,
        'type': 0,
        'sampledWave': {
          'pageOffset': 0,
          'waveName': [0, 0, 0],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
          'waveStartIndex': [0, 3, 0],
          'waveVelocityStartMod': [0, 4, 0],
          'waveDirection': [0, 5, 0]
        },
        'transwave': {
          'pageOffset': 1,
          'waveName': [0, 0, 63],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
          'waveStart': [0, 3, 0],
          'waveModSource': [0, 4, 15],
          'waveModAmount': [0, 5, 0],
        },
        'waveform': {
          'pageOffset': 2,
          'waveName': [0, 0, 84],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
        },
        'multiWave': {
          'pageOffset': 3,
          'waveName': [0, 0, 108],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
          'loopWaveStart': [0, 3, 0],
          'loopLength': [0, 4, 243],
          'loopDirection': [0, 5, 0]
        }
      },
      'pitch': {
        'pageOffset': 5,
        'octave': [0, 0, 0],
        'semitone': [0, 1, 0],
        'fineTune': [0, 2, 0],
        'pitchTable':    [0, 4, 0]
      },
      'pitchMod': {
        'pageOffset': 6,
        'modSource': [0, 1, 15],
        'modAmount': [0, 2, 0],
        'glideMode':      [0, 3, 0],
        'env1ModAmount': [0, 4, 0],
        'lfoModAmount': [0, 5, 0]
      },
      'filters': {
        'pageOffset': 7,
        'filter1': {
          'pageOffset': 0,
          'type': [0, 0, 0],
          'cutoff': [0, 1, 127],
          'keyboardTrack': [0, 2, 0],
          'modSource': [0, 3, 15],
          'modAmount': [0, 4, 0],
          'env2ModAmount': [0, 5, 0]
        },
        'filter2': {
          'pageOffset': 1,
          'type': [0, 0, 0],
          'cutoff': [0, 1, 0],
          'keyboardTrack': [0, 2, 0],
          'modSource': [0, 3, 15],
          'modAmount': [0, 4, 0],
          'env2ModAmount': [0, 5, 0]
        }
      },
      'output': {
        'pageOffset': 9,
        'volume': [0, 0, 127],
        'volumeModSource': [0, 1, 15],
        'volumeModAmount': [0, 2, 0],
        'keyboardScaleAmount': [0, 3, 0],
        'scalingKeyStart': [0, 5, 36],
        'scalingKeyEnd': [0, 5, 96],
        'destination': [1, 2, 0],
        'pan':  [1, 3, 64],
        'panModSource': [1, 4, 15],
        'panModAmount': [1, 5, 0],
        'preGain': [2, 0, 0],
        'priority': [2, 2, 1],
        'velocityThreshold': [2, 5, 0]
      },
      'lfo': {
        'pageOffset': 12,
        'rate': [0, 0, 20],
        'rateModSource': [0, 1, 15],
        'rateModAmount': [0, 2, 0],
        'depth': [0, 3, 30],
        'depthModSource': [0, 4, 15],
        'delay': [0, 5, 0],
        'waveshape': [1, 1, 1],
        'restart': [1, 2, 0],
        'noiseSourceRate': [1, 5, 50]
      },
      'envelopes': {
        'pageOffset': 14,
        'env0': {
          'pageOffset': 0,
          'initialLevel': [0, 1, 0],
          'peakLevel': [0, 2, 127],
          'breakpoint1Level': [0, 3, 127],
          'breakpoint2Level': [0, 4, 127],
          'sustainLevel': [0, 5, 127],
          'attackTime': [1, 1, 0],
          'decay1Time': [1, 2, 0],
          'decay2Time': [1, 3, 0],
          'decay3Time': [1, 4, 0],
          'releaseTime': [1, 5, 0],
          'keyboardTrack': [2, 0, 0],
          'velocityCurve': [2, 2, 0],
          'mode': [2, 3, 0],
          'levelVelocitySens': [2, 4, 0],
          'attackTimeVelocitySens': [2, 5, 0]
        },
        'env1': {
          'pageOffset': 3,
          'initialLevel': [0, 1, 0],
          'peakLevel': [0, 2, 127],
          'breakpoint1Level': [0, 3, 127],
          'breakpoint2Level': [0, 4, 127],
          'sustainLevel': [0, 5, 127],
          'attackTime': [1, 1, 0],
          'decay1Time': [1, 2, 0],
          'decay2Time': [1, 3, 0],
          'decay3Time': [1, 4, 0],
          'releaseTime': [1, 5, 0],
          'keyboardTrack': [2, 0, 0],
          'velocityCurve': [2, 2, 0],
          'mode': [2, 3, 0],
          'levelVelocitySens': [2, 4, 0],
          'attackTimeVelocitySens': [2, 5, 0]
        },
        'env2': {
          'pageOffset': 6,
          'initialLevel': [0, 1, 0],
          'peakLevel': [0, 2, 127],
          'breakpoint1Level': [0, 3, 127],
          'breakpoint2Level': [0, 4, 127],
          'sustainLevel': [0, 5, 127],
          'attackTime': [1, 1, 0],
          'decay1Time': [1, 2, 0],
          'decay2Time': [1, 3, 0],
          'decay3Time': [1, 4, 0],
          'releaseTime': [1, 5, 0],
          'keyboardTrack': [2, 0, 0],
          'velocityCurve': [2, 2, 0],
          'mode': [2, 3, 0],
          'levelVelocitySens': [2, 4, 0],
          'attackTimeVelocitySens': [2, 5, 0]
        }
      }
    }
    
    self.params = {
      'master': {
        'pageOffset': 0,
        'masterTune':  [0, 0, 0],
        'touch':       [0, 1, 11], #should be firm-4
        'bendRange': [0, 2, 2],
        'footSwitch1':     [0, 4, 0],
        'footSwitch2':     [0, 5, 0],
        'sliderMode':      [1, 0, 1],
        'cvPedal':         [1, 2, 0],
        'pitchTable':[1, 5, 1],
        'maxVelocity':     [2, 0, 127],
        'midiTrackNaming': [2, 2, 1],
        'voiceMuting':     [2, 4, 0],
        'keyboardNaming':  [2, 5, 1]
      },
      'midiControl': {
        'pageOffset': 3,
        'baseChannel': [0, 0, 0], #set this when establishing com
        'sendChannel': [0, 2, 0],
        'mode': [0, 3, 1],
        'transpose': [0, 4, 2],
        'externalCC': [0, 5, 95], #todo: set this
        'loopEnable': [1, 0, 0],
        'controllersEnable': [1, 1, 1],
        'songSelectEnable': [1, 2, 0],
        'sendStartStop': [1, 3, 1],
        'systemExclusiveEnable': [1, 4, 1],
        'programChangeEnable': [1, 5, 1]
      },
      'program': {
        'name': 'Init',
      },
      'programControl': {
        'pageOffset': 5,
        'pitchTableEnable': [0, 1, 0],
        'bendRange': [0, 2, 13],
        'delayMultiplier': [0, 3, 0],
        'restrikeDelay': [0, 4, 0],
        'glideTime': [0, 5, 0]
      },
      'selectVoice': {
        'pageOffset': 38,
        'voice0Status':  [0, 0, 1],
        'voice1Status':  [0, 1, 0],
        'voice2Status':  [0, 2, 0],
        'voice3Status':  [0, 3, 0],
        'voice4Status':  [0, 4, 0],
        'voice5Status':  [0, 5, 0]
      },
      'voice0': {
        'pageOffset': 6,
        **copy.deepcopy(voiceParams)
      },
      'voice1': {
        'pageOffset': 6,
        **copy.deepcopy(voiceParams)
      },
      'voice2': {
        'pageOffset': 6,
        **copy.deepcopy(voiceParams)
      },
      'voice3': {
        'pageOffset': 6,
        **copy.deepcopy(voiceParams)
      },
      'voice4': {
        'pageOffset': 6,
        **copy.deepcopy(voiceParams)
      },
      'voice5': {
        'pageOffset': 6,
        **copy.deepcopy(voiceParams)
      },
    }
    
  def establishCommunications(self):
    print(f'{self.trans}Establishing communications')

    midi.sendSysex(self.output, [EST, 0x7E, 0x7F, 0x06, 0x01, EOX])
    
    t.delay(0.1)

    identitySysex = []
    sysexBuffer = []
    received = False
    while True:
      recv, sysex, sysexBuffer = midi.getSysex(self.input, sysexBuffer)
      #todo: make sure this is the identity reply from the sd-1
      if recv and not received: 
        received = True
        identitySysex = sysex
      else: 
        break
    if not received:
      print(f'{self.alrt}Communications failed!\n')
      return False, []
    
    self.channel = identitySysex[2]
    model = ['VFX', 'VFX-SD', 'VFX-SD II', 'SD-1'][identitySysex[8]]
    version = f'{identitySysex[12]}.{identitySysex[13]}'
    
    print(f'{self.info}{model}')
    print(f'{self.info}OS Version {version}')
    print(f'{self.info}Channel {self.channel+1}')
    print(f'{self.recv}Communication established!\n')
     
    return received, sysexBuffer
  
  def decouple(self):
    print('SD-1 Decoupled!')
    if self.linebreakRecv: print()
    self.decoupled = True
    self.trans = self.transDecoupled
    self.transNoExp = self.transNoExpDecoupled
    
  def couple(self):
    print('SD-1 Coupled!')
    if self.linebreakRecv: print()
    self.decoupled = False
    self.trans = self.transNormal
    self.transNoExp = self.transNoExpNormal
  
  def send(self, sysex):
    if not self.decoupled:
      midi.sendSysex(self.output, sysex)

  def getSysexTemplate(self, name):
    if name == 'pressButton':                       return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x00, 'button', EOX]
    elif name == 'parameterChange':                 return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x01, 'voice', 'page', 'slot', 'value', EOX]
    elif name == 'espMicrocodeProgramLoad':         return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x03, EOX]
    elif name == 'pokeByteToRAM':                   return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x04, EOX]
    elif name == 'currentProgramDumpRequest':       return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x05, EOX]
    elif name == 'currentPresetDumpRequest':        return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x06, EOX]
    elif name == 'trackParameterDumpRequest':       return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x07, EOX]
    elif name == 'dumpEverythingRequest':           return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x08, EOX]
    elif name == 'internalProgramBankDumpRequest':  return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x09, EOX]
    elif name == 'internalPresetBankDumpRequest':   return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x0A, EOX]
    elif name == 'sequenceDump':                    return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x0B, 'dataSize', EOX]
    elif name == 'allSequenceMemoryDump':           return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x0C, 'dataSize', EOX]
    elif name == 'currentSequenceDumpRequest':      return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x0D, EOX]
    elif name == 'allSequenceDumpRequest':          return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x00, 0x00, 0x0E, EOX]
    elif name == 'programDump':                     return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x02, 'data', EOX]
    elif name == 'allProgramsDump':                 return [EST, ensoniqID, vfxFamilyID, sdID, self.channel, 0x03, 'data', EOX]

  # def queueSysex(self, sysex):
  #   self.operationQueue.append(lambda sd, sysex=sysex: midi.sendSysex(sd.output, sysex))

  def queueOperation(self, func):
    self.operationQueue.append(func)
      
  def handleQueue(self):
    if self.receivedResponse or not self.runningOperation:
      self.receivedResponse = False
      self.runningOperation = False
      
      if len(self.operationQueue) > 0:
        func = self.operationQueue.pop(0)
        func(self)
        self.runningOperation = True
        
  def replace(self, sysex, index, value):
    i = sysex.index(index)
    if type(value) is int:
      sysex[i] = value
    else:
      sysex[i:i+1] = value
    return sysex, i

  def getWaveClass(self, wave):
    if wave < 15: return 0
    elif wave < 23: return 1
    elif wave < 29: return 2
    elif wave < 34: return 3
    elif wave < 47: return 4
    elif wave < 63: return 5
    elif wave < 80: return 6
    elif wave < 103: return 7
    elif wave < 108: return 8
    elif wave == 108: return 9
    elif wave < 125: return 10
    elif wave < 141: return 11
    elif wave < 150: return 12
    elif wave < 161: return 13
    elif wave < 167: return 14
    elif wave == 167: return 15

  def encode8Bit(self, value):
    return [(value & 0xf0) >> 4, value & 0x0f]
  
  def encode16Bit(self, value):
    return [*self.encode8Bit((value & 0xff00) >> 8), *self.encode8Bit(value & 0x00ff)]
  
  def decode8Bit(self, byte1, byte2):
    return (byte1 << 4) + byte2

  def decodeSysex(self, sysex):
    #Check if the sysex message is for us.
    if sysex[0:5] == [EST, ensoniqID, vfxFamilyID, sdID, self.channel]:
      self.receivedResponse = True
      
      messageType = sysex[5]
      
      if messageType == 0x00 and self.debug:
        commandType = sysex[6] + sysex[7] << 4
        if commandType == 0x02:
          print(f'{self.recv}Edit buffer desync!')
          if self.linebreakRecv: print()
      elif messageType == 0x01 and self.debug:
        if sysex[6] == 0x04:
          print(f'{self.recv}Acknowledge')
          if self.linebreakRecv: print()
        else:
          print(f'{self.alrt}{("No Acknowledgement", "Invalid Parameter Number", "Invalid Parameter Value", "Invalid Button Number")[sysex[7]]}')
          if self.linebreakRecv: print()
      elif messageType == 0x02:
        if self.debug: 
          print(f'{self.recv}Received program dump')
          if self.linebreakRecv: print()
        self.loadProgramDump(sysex[6:-1])
      else:
        print(f'{self.alrt}Unknown message')
        if self.linebreakRecv: print()
      
      if self.debug and self.linebreakRecv: print()

  def requestCurrentProgram(self):
    sysex = self.getSysexTemplate('currentProgramDumpRequest')
    
    if self.debug: 
      print(f'{self.trans}Requesting current program')
      
    self.send(sysex)

  def pressButton(self, buttonId):
    sysexDown = self.getSysexTemplate('pressButton')
    sysexDown, _ = self.replace(sysexDown, 'button', self.encode8Bit(buttonId.value))
    
    sysexUp   = self.getSysexTemplate('pressButton')
    sysexUp, _ = self.replace(sysexUp, 'button', self.encode8Bit(buttonId.value+96))
    
    if self.debug: 
      print(f'{self.trans}Virtual button {buttonNames[buttonId.value]}')
      print(f'{self.info}Down')
    self.send(sysexDown)
    
    t.delay(0.3) #Manual recommends 2-300ms delay
    
    if self.debug:
      print(f'{self.endNoRecv}Up')
      if self.linebreakRecv: print()
    self.send(sysexUp)

    if self.debug and self.linebreakRecv: print()
    
  def changeParameter(self, parameter, value, force=False):
    sysex = self.getSysexTemplate('parameterChange')
    
    paramKeys = parameter.split('.')
    param = self.params
    voice = 0
    pageOffset = 0
    for key in paramKeys:
      if len(key) > 5 and key[0:5] == 'voice': voice = int(key[5])
      param = param[key]
      if type(param) is dict: pageOffset += param['pageOffset']
      
    if type(param) is not list:
      param = value
      return
    
    if value == param[2] and not force: return
    else: param[2] = value
    
    sysex, _ = self.replace(sysex, 'voice', self.encode8Bit(voice))
    sysex, _ = self.replace(sysex, 'page', self.encode8Bit(pageOffset + param[0]))
    sysex, _ = self.replace(sysex, 'slot', self.encode8Bit(param[1]))
    sysex, _ = self.replace(sysex, 'value', self.encode16Bit(value))
    
    if self.debug and self.logParameterChanges: 
      print(f'{self.trans}Parameter change {parameter} to {value}')
      print(f'{self.endNoRecv}Voice {voice}, Page {pageOffset+param[0]}, Slot {param[1]}')
      if self.linebreakRecv: print()
    
    self.send(sysex)
    
  def changeWaveType(self, voice, t, force=False):
    if self.params[f'voice{voice}']['wave']['type'] == t and not force: return
    else: self.params[f'voice{voice}']['wave']['type'] = t
    
    if t == 0:
      self.changeParameter(f'voice{voice}.wave.waveform.waveName', self.params[f'voice{voice}']['wave']['waveform']['waveName'][2], force=True)
    elif t == 1:
      self.changeParameter(f'voice{voice}.wave.transwave.waveName', self.params[f'voice{voice}']['wave']['transwave']['waveName'][2], force=True)
      self.changeParameter(f'voice{voice}.wave.transwave.waveStart', self.params[f'voice{voice}']['wave']['transwave']['waveStart'][2], force=True)
      self.changeParameter(f'voice{voice}.wave.transwave.waveModSource', self.params[f'voice{voice}']['wave']['transwave']['waveModSource'][2], force=True)
      self.changeParameter(f'voice{voice}.wave.transwave.waveModAmount', self.params[f'voice{voice}']['wave']['transwave']['waveModAmount'][2], force=True)
    elif t == 2:
      self.changeParameter(f'voice{voice}.wave.sampledWave.waveName', self.params[f'voice{voice}']['wave']['sampledWave']['waveName'][2], force=True)
      self.changeParameter(f'voice{voice}.wave.sampledWave.waveStartIndex', self.params[f'voice{voice}']['wave']['sampledWave']['waveStartIndex'][2], force=True)
      self.changeParameter(f'voice{voice}.wave.sampledWave.waveVelocityStartMod', self.params[f'voice{voice}']['wave']['sampledWave']['waveVelocityStartMod'][2], force=True)
      self.changeParameter(f'voice{voice}.wave.sampledWave.waveDirection', self.params[f'voice{voice}']['wave']['sampledWave']['waveDirection'][2], force=True)
    elif t == 3:
      self.changeParameter(f'voice{voice}.wave.multiWave.waveClass', 9, force=True)
      self.changeParameter(f'voice{voice}.wave.multiWave.loopWaveStart', self.params[f'voice{voice}']['wave']['multiWave']['loopWaveStart'][2], force=True)
      self.changeParameter(f'voice{voice}.wave.multiWave.loopLength', self.params[f'voice{voice}']['wave']['multiWave']['loopLength'][2], force=True)
      self.changeParameter(f'voice{voice}.wave.multiWave.loopDirection', self.params[f'voice{voice}']['wave']['multiWave']['loopDirection'][2], force=True)

  def getParameters(self):
    def recursive_map(data):
      apply = lambda x: recursive_map(x)
      if isinstance(data, Mapping):
        return ({k: apply(v) for k, v in data.items()})
      elif type(data) is str:
        return data
      elif isinstance(data, Collection):
        return data[2]
      else:
        return data
    
    return recursive_map(self.params)

  def loadProgramDump(self, sysex):
    values = []
    for i in range(0, len(sysex), 2):
      values.append(self.decode8Bit(sysex[i], sysex[i+1]))
    
    def neg(v):
      return v if v < 128 else v - 256
    
    self.params['programControl']['glideTime'][2] = values[514]
    self.params['programControl']['delayMultiplier'][2] = (values[515] & 0xf0) >> 4
    self.params['programControl']['bendRange'][2] = values[515] & 0x0f
    self.params['programControl']['restrikeDelay'][2] = values[516]
    self.params['program']['name'] = ''.join(map(chr, values[498:509]))
    
    for v in range(6):
      self.params['selectVoice'][f'voice{v}Status'][2] = (values[509] & (0b1 << v)) >> v
      
      vO = v * 83
      for e in range(3):
        eO = e * 14
        self.params[f'voice{v}']['envelopes'][f'env{e}']['initialLevel'][2] = values[vO+eO+ 0]-128 if values[vO+eO+ 0] >= 128 else values[vO+eO+ 0]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['attackTime'][2] = values[vO+eO+ 1]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['peakLevel'][2] = values[vO+eO+ 2]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['decay1Time'][2] = values[vO+eO+ 3]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['breakpoint1Level'][2] = values[vO+eO+ 4]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['decay2Time'][2] = values[vO+eO+ 5]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['breakpoint2Level'][2] = values[vO+eO+ 6]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['decay3Time'][2] = values[vO+eO+ 7]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['sustainLevel'][2] = values[vO+eO+ 8]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['releaseTime'][2] = values[vO+eO+ 9]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['levelVelocitySens'][2] = values[vO+eO+ 10]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['attackTimeVelocitySens'][2] = values[vO+eO+ 11]
        self.params[f'voice{v}']['envelopes'][f'env{e}']['keyboardTrack'][2] = neg(values[vO+eO+ 12])
        self.params[f'voice{v}']['envelopes'][f'env{e}']['mode'][2] = (values[vO+eO+ 13] & 0xf0) >> 4
        self.params[f'voice{v}']['envelopes'][f'env{e}']['velocityCurve'][2] = values[vO+eO+ 13] & 0x0f
    
      octave = round(neg(values[vO+ 42]) / 12)
      self.params[f'voice{v}']['pitch']['octave'][2] = octave
      semi = neg(values[vO+ 42]) - octave * 12
      self.params[f'voice{v}']['pitch']['semitone'][2] = semi
      self.params[f'voice{v}']['pitch']['fineTune'][2] = neg(values[vO+ 43])
      self.params[f'voice{v}']['pitch']['pitchTable'][2] = values[vO+ 44]
      self.params[f'voice{v}']['pitchMod']['env1ModAmount'][2] = neg(values[vO+ 45])
      self.params[f'voice{v}']['pitchMod']['lfoModAmount'][2] = neg(values[vO+ 46])
      self.params[f'voice{v}']['pitchMod']['glideMode'][2] = (values[vO+ 47] & 0xf0) >> 4
      self.params[f'voice{v}']['pitchMod']['modSource'][2] = values[vO+ 47] & 0x0f
      self.params[f'voice{v}']['pitchMod']['modAmount'][2] = neg(values[vO+ 48])

      self.params[f'voice{v}']['filters'][f'filter2']['type'][2] = values[vO + 52]>>4
      for f in range(2):
        fO = f * 5
        self.params[f'voice{v}']['filters'][f'filter{f+1}']['cutoff'][2] = values[vO+fO+ 49]
        self.params[f'voice{v}']['filters'][f'filter{f+1}']['keyboardTrack'][2] = neg(values[vO+fO+ 50])
        self.params[f'voice{v}']['filters'][f'filter{f+1}']['env2ModAmount'][2] = neg(values[vO+fO+ 51])
        self.params[f'voice{v}']['filters'][f'filter{f+1}']['modSource'][2] = values[vO+fO+ 52] & 0x0f
        self.params[f'voice{v}']['filters'][f'filter{f+1}']['modAmount'][2] = neg(values[vO+fO+ 53])
        
      self.params[f'voice{v}']['output']['keyboardScaleAmount'][2] = neg(values[vO+ 59])
      self.params[f'voice{v}']['output']['scalingKeyStart'][2] = values[vO+ 60]
      self.params[f'voice{v}']['output']['scalingKeyEnd'][2] = values[vO+ 61]
      self.params[f'voice{v}']['output']['volume'][2] = values[vO+ 62] & 0x7f
      self.params[f'voice{v}']['output']['preGain'][2] = (values[vO+ 62] & 0x80) >> 7
      self.params[f'voice{v}']['output']['panModSource'][2] = (values[vO+ 63] & 0xf0) >> 4
      self.params[f'voice{v}']['output']['volumeModSource'][2] = values[vO+ 63] & 0x0f
      self.params[f'voice{v}']['output']['volumeModAmount'][2] = neg(values[vO+ 64])
      self.params[f'voice{v}']['output']['pan'][2] = values[vO+ 65]
      self.params[f'voice{v}']['output']['panModAmount'][2] = neg(values[vO+ 66])
      self.params[f'voice{v}']['output']['priority'][2] = (values[vO+ 67] & 0xf0) >> 4
      self.params[f'voice{v}']['output']['destination'][2] = values[vO+ 67] & 0x0f
      self.params[f'voice{v}']['output']['velocityThreshold'][2] = neg(values[vO+ 82])
      
      self.params[f'voice{v}']['lfo']['waveshape'][2] = (values[vO+ 68] & 0xf0) >> 4
      self.params[f'voice{v}']['lfo']['depthModSource'][2] = values[vO+ 68] & 0x0f
      self.params[f'voice{v}']['lfo']['depth'][2] = values[vO+ 69]
      self.params[f'voice{v}']['lfo']['restart'][2] = (values[vO+ 70] & 0xf0) >> 4
      self.params[f'voice{v}']['lfo']['rateModSource'][2] = values[vO+ 70] & 0x0f
      self.params[f'voice{v}']['lfo']['rateModAmount'][2] = neg(values[vO+ 71])
      self.params[f'voice{v}']['lfo']['rate'][2] = values[vO+ 72]
      self.params[f'voice{v}']['lfo']['delay'][2] = values[vO+ 73]
      self.params[f'voice{v}']['lfo']['noiseSourceRate'][2] = values[vO+ 78]
      
      self.params[f'voice{v}']['modMixer']['shape'][2] = (values[vO+ 80] & 0xf0) >> 4
      self.params[f'voice{v}']['modMixer']['modSource1'][2] = values[vO+ 80] & 0x0f
      self.params[f'voice{v}']['modMixer']['scaler'][2] = (values[vO+ 81] & 0xf0) >> 4
      self.params[f'voice{v}']['modMixer']['modSource2'][2] = values[vO+ 81] & 0x0f
      
      waveClass = (values[vO+ 75] & 0xf0) >> 4
      if waveClass == 7 or waveClass == 8:
        #waveform
        self.params[f'voice{v}']['wave']['type'] = 0
        self.params[f'voice{v}']['wave']['waveform']['waveName'][2] = values[vO+ 74]
        self.params[f'voice{v}']['wave']['waveform']['delayTime'][2] = values[vO+ 79]
      elif waveClass == 6:
        #transwave
        self.params[f'voice{v}']['wave']['type'] = 1
        self.params[f'voice{v}']['wave']['transwave']['waveName'][2] = values[vO+ 74]
        self.params[f'voice{v}']['wave']['transwave']['waveModSource'][2] = values[vO+ 75] & 0x0f
        self.params[f'voice{v}']['wave']['transwave']['waveModAmount'][2] = neg(values[vO+ 76])
        self.params[f'voice{v}']['wave']['transwave']['waveStart'][2] = values[vO+ 77]
        self.params[f'voice{v}']['wave']['transwave']['delayTime'][2] = values[vO+ 79]
      elif waveClass == 9:
        #multiwave
        self.params[f'voice{v}']['wave']['type'] = 3
        self.params[f'voice{v}']['wave']['multiWave']['waveName'][2] = values[vO+ 74]
        self.params[f'voice{v}']['wave']['multiWave']['loopDirection'][2] = values[vO+ 75] & 0x0f
        self.params[f'voice{v}']['wave']['multiWave']['loopLength'][2] = values[vO+ 76]
        self.params[f'voice{v}']['wave']['multiWave']['loopWaveStart'][2] = values[vO+ 77]
        self.params[f'voice{v}']['wave']['multiWave']['delayTime'][2] = values[vO+ 79]
      else:
        #sampled
        self.params[f'voice{v}']['wave']['type'] = 2
        self.params[f'voice{v}']['wave']['sampledWave']['waveName'][2] = values[vO+ 74]
        self.params[f'voice{v}']['wave']['sampledWave']['waveDirection'][2] = values[vO+ 75] & 0x0f
        self.params[f'voice{v}']['wave']['sampledWave']['waveVelocityStartMod'][2] = neg(values[vO+ 76])
        self.params[f'voice{v}']['wave']['sampledWave']['waveStartIndex'][2] = values[vO+ 77]
        self.params[f'voice{v}']['wave']['sampledWave']['delayTime'][2] = values[vO+ 79]
    
    self.updateGUI = True
    
  def saveProgramDump(self):
    d = []
    
    def combine(high, low):
      return (high << 4) + low
    
    for v in range(6):
      for e in range(3):
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['initialLevel'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['attackTime'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['peakLevel'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['decay1Time'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['breakpoint1Level'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['decay2Time'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['breakpoint2Level'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['decay3Time'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['sustainLevel'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['releaseTime'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['levelVelocitySens'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['attackTimeVelocitySens'][2])
        d.append(self.params[f'voice{v}']['envelopes'][f'env{e}']['keyboardTrack'][2])
        d.append(combine(
          self.params[f'voice{v}']['envelopes'][f'env{e}']['mode'][2],
          self.params[f'voice{v}']['envelopes'][f'env{e}']['velocityCurve'][2]))
        
      d.append(self.params[f'voice{v}']['pitch']['octave'][2] * 12 + self.params[f'voice{v}']['pitch']['semitone'][2])
      d.append(self.params[f'voice{v}']['pitch']['fineTune'][2])
      d.append(self.params[f'voice{v}']['pitch']['pitchTable'][2])
      d.append(self.params[f'voice{v}']['pitchMod']['env1ModAmount'][2])
      d.append(self.params[f'voice{v}']['pitchMod']['lfoModAmount'][2])
      d.append(combine(
        self.params[f'voice{v}']['pitchMod']['glideMode'][2],
        self.params[f'voice{v}']['pitchMod']['modSource'][2]))
      d.append(self.params[f'voice{v}']['pitchMod']['modAmount'][2])
      d.append(self.params[f'voice{v}']['filters']['filter1']['cutoff'][2])
      d.append(self.params[f'voice{v}']['filters']['filter1']['keyboardTrack'][2])
      d.append(self.params[f'voice{v}']['filters']['filter1']['env2ModAmount'][2])
      d.append(combine(
        self.params[f'voice{v}']['filters']['filter2']['type'][2],
        self.params[f'voice{v}']['filters']['filter1']['modSource'][2]))
      d.append(self.params[f'voice{v}']['filters']['filter1']['modAmount'][2])
      d.append(self.params[f'voice{v}']['filters']['filter2']['cutoff'][2])
      d.append(self.params[f'voice{v}']['filters']['filter2']['keyboardTrack'][2])
      d.append(self.params[f'voice{v}']['filters']['filter2']['env2ModAmount'][2])
      d.append(self.params[f'voice{v}']['filters']['filter2']['modSource'][2])
      d.append(self.params[f'voice{v}']['filters']['filter2']['modAmount'][2])
      d.append(self.params[f'voice{v}']['output']['keyboardScaleAmount'][2])
      d.append(self.params[f'voice{v}']['output']['scalingKeyStart'][2])
      d.append(self.params[f'voice{v}']['output']['scalingKeyEnd'][2])
      d.append((self.params[f'voice{v}']['output']['preGain'][2] << 7) + self.params[f'voice{v}']['output']['volume'][2])
      d.append(combine(
        self.params[f'voice{v}']['output']['panModSource'][2],
        self.params[f'voice{v}']['output']['volumeModSource'][2]))
      d.append(self.params[f'voice{v}']['output']['volumeModAmount'][2])
      d.append(self.params[f'voice{v}']['output']['pan'][2])
      d.append(self.params[f'voice{v}']['output']['panModAmount'][2])
      d.append(combine(
        self.params[f'voice{v}']['output']['priority'][2],
        self.params[f'voice{v}']['output']['destination'][2]))
      d.append(combine(
        self.params[f'voice{v}']['lfo']['waveshape'][2],
        self.params[f'voice{v}']['lfo']['depthModSource'][2]))
      d.append(self.params[f'voice{v}']['lfo']['depth'][2])
      d.append(combine(
        self.params[f'voice{v}']['lfo']['restart'][2],
        self.params[f'voice{v}']['lfo']['rateModSource'][2]))
      d.append(self.params[f'voice{v}']['lfo']['rateModAmount'][2])
      d.append(self.params[f'voice{v}']['lfo']['rate'][2])
      d.append(self.params[f'voice{v}']['lfo']['delay'][2])
      
      ty = self.params[f'voice{v}']['wave']['type']
      if ty == 0:
        d.append(self.params[f'voice{v}']['wave']['waveform']['waveName'][2])
        d.append(combine(
          self.getWaveClass(self.params[f'voice{v}']['wave']['waveform']['waveName'][2]),
          0))
        d.append(0)
        d.append(0)
      elif ty == 1:
        d.append(self.params[f'voice{v}']['wave']['transwave']['waveName'][2])
        d.append(combine(
          self.getWaveClass(self.params[f'voice{v}']['wave']['transwave']['waveName'][2]),
          self.params[f'voice{v}']['wave']['transwave']['waveModSource'][2]))
        d.append(self.params[f'voice{v}']['wave']['transwave']['waveModAmount'][2])
        d.append(self.params[f'voice{v}']['wave']['transwave']['waveStart'][2])
      elif ty == 2:
        d.append(self.params[f'voice{v}']['wave']['sampledWave']['waveName'][2])
        d.append(combine(
          self.getWaveClass(self.params[f'voice{v}']['wave']['sampledWave']['waveName'][2]),
          self.params[f'voice{v}']['wave']['sampledWave']['waveDirection'][2]))
        d.append(self.params[f'voice{v}']['wave']['sampledWave']['waveVelocityStartMod'][2])
        d.append(self.params[f'voice{v}']['wave']['sampledWave']['waveStartIndex'][2])
      elif ty == 3:
        d.append(self.params[f'voice{v}']['wave']['multiWave']['waveName'][2])
        d.append(combine(
          9,
          self.params[f'voice{v}']['wave']['multiWave']['loopDirection'][2]))
        d.append(self.params[f'voice{v}']['wave']['multiWave']['loopLength'][2])
        d.append(self.params[f'voice{v}']['wave']['multiWave']['loopWaveStart'][2])
        
      d.append(self.params[f'voice{v}']['lfo']['noiseSourceRate'][2])
      d.append(self.params[f'voice{v}']['wave']['waveform']['delayTime'][2])
    
      d.append(combine(
        self.params[f'voice{v}']['modMixer']['shape'][2],
        self.params[f'voice{v}']['modMixer']['modSource1'][2]))
      d.append(combine(
        self.params[f'voice{v}']['modMixer']['scaler'][2],
        self.params[f'voice{v}']['modMixer']['modSource2'][2]))
      
      d.append(self.params[f'voice{v}']['output']['velocityThreshold'][2])
        
    name = self.params['program']['name']
    while len(name) < 11:
        name += ' '
    nameList = list(map(ord, name[0:11]))
    for c in nameList:
      d.append(c)
      
    d.append(
      (self.params['selectVoice']['voice0Status'][2] > 0) +
      ((self.params['selectVoice']['voice1Status'][2] > 0) << 1) + 
      ((self.params['selectVoice']['voice2Status'][2] > 0) << 2) + 
      ((self.params['selectVoice']['voice3Status'][2] > 0) << 3) + 
      ((self.params['selectVoice']['voice4Status'][2] > 0) << 4) + 
      ((self.params['selectVoice']['voice5Status'][2] > 0) << 5))
    d.append(0)
    d.append(0)
    d.append(0)
    d.append(self.params['programControl']['pitchTableEnable'][2])
    d.append(self.params['programControl']['glideTime'][2])
    d.append(combine(
      self.params['programControl']['delayMultiplier'][2],
      self.params['programControl']['bendRange'][2]))
    d.append(self.params['programControl']['restrikeDelay'][2])
    d.append(0)
    d.append(0)
    for i in range(8):
      d.append(0) #fx
    d.append(0)
    d.append(0)
    d.append(0)
    
    sysex = self.getSysexTemplate('programDump')
    sysex = sysex[0:-2]
    
    for v in d:
      hi, lo = self.encode8Bit(v)
      sysex.append(hi)
      sysex.append(lo)
      
    sysex.append(EOX)
    
    if self.debug: 
      print(f'{self.transNoExp}Uploading program {name}')
    
    self.send(sysex)
    t.delay(1)
    self.pressButton(Button.SOFT3)