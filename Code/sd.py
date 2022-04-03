midi = __import__('midi')
t = __import__('tools')
from sdenums import Button, buttonNames
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

    self.updateGUI = False
    self.debug = debug
    self.logParameterChanges = logParameterChanges
    self.trans =        '┌─T  '
    self.transNoExp =   '  T  '
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
        'modSource1': [0, 1, 0],
        'modSource2': [0, 2, 0],
        'scaler': [0, 4, 0],
        'shape': [0, 5, 0]
      },
      'wave': {
        'pageOffset': 1,
        'sampledWave': {
          'pageOffset': 0,
          'waveform': 'wave.sampledWave',
          'waveName': [0, 0, 0],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
          'waveStartIndex': [0, 3, 0],
          'waveVelocityStartMod': [0, 4, 0],
          'waveDirection': [0, 5, 0]
        },
        'transwave': {
          'pageOffset': 1,
          'waveform': 'wave.transwave',
          'waveName': [0, 0, 0],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
          'waveStart': [0, 3, 0],
          'waveModSource': [0, 4, 0],
          'waveModAmount': [0, 5, 0],
        },
        'waveform': {
          'pageOffset': 2,
          'waveform': 'wave.waveform',
          'waveName': [0, 0, 0],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
        },
        'inharmonic': {
          'pageOffset': 2,
          'waveform': 'wave.inharmonic',
          'waveName': [0, 0, 0],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
        },
        'multiWave': {
          'pageOffset': 3,
          'waveform': 'wave.multiwave',
          'waveName': [0, 0, 0],
          'waveClass':[0, 1, 0],
          'delayTime':[0, 2, 0],
          'loopWaveStart': [0, 3, 249],
          'loopLength': [0, 4, 1],
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
        'modSource': [0, 1, 0],
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
          'cutoff': [0, 1, 0],
          'keyboardTrack': [0, 2, 0],
          'modSource': [0, 3, 0],
          'modAmount': [0, 4, 0],
          'env2ModAmount': [0, 5, 0]
        },
        'filter2': {
          'pageOffset': 1,
          'type': [0, 0, 0],
          'cutoff': [0, 1, 0],
          'keyboardTrack': [0, 2, 0],
          'modSource': [0, 3, 0],
          'modAmount': [0, 4, 0],
          'env2ModAmount': [0, 5, 0]
        }
      },
      'output': {
        'pageOffset': 9,
        'volume': [0, 0, 0],
        'volumeModSource': [0, 1, 0],
        'volumeModAmount': [0, 2, 0],
        'keyboardScaleAmount': [0, 3, 0],
        'scalingKeyRange': [0, 5, 108],
        'destination': [1, 2, 1],
        'pan':  [1, 3, 64],
        'panModSource': [1, 4, 0],
        'panModAmount': [1, 5, 0],
        'preGain': [2, 0, 0],
        'priority': [2, 2, 1],
        'velocityThreshold': [2, 5, 0]
      },
      'lfo': {
        'pageOffset': 12,
        'rate': [0, 0, 20],
        'rateModSource': [0, 1, 0],
        'rateModAmount': [0, 2, 0],
        'depth': [0, 3, 30],
        'depthModSource': [0, 4, 0],
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
      print(f'{self.alrt}Communications failed!')
      return False, []
    
    self.channel = identitySysex[2]
    model = ['VFX', 'VFX-SD', 'VFX-SD II', 'SD-1'][identitySysex[8]]
    version = f'{identitySysex[12]}.{identitySysex[13]}'
    
    print(f'{self.info} {model}')
    print(f'{self.info} OS Version {version}')
    print(f'{self.info} Channel {self.channel+1}')
    print(f'{self.recv}Communication established!\n')    
     
    return received, sysexBuffer

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

  def queueSysex(self, sysex):
    self.operationQueue.append(lambda sd, sysex=sysex: midi.sendSysex(sd.output, sysex))

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

  def encode8Bit(self, value):
    return [(value & 0xf0) >> 4, value & 0x0f]
  
  def encode16Bit(self, value):
    return [*self.encode8Bit((value & 0xff00) >> 8), *self.encode8Bit(value & 0x00ff)]
  
  def decode8Bit(self, byte1, byte2):
    return (byte1 << 4) + byte1

  def decodeSysex(self, sysex):
    #Check if the sysex message is for us.
    if sysex[0:5] == [EST, ensoniqID, vfxFamilyID, sdID, self.channel]:
      self.receivedResponse = True
      
      messageType = sysex[5]
      
      if messageType == 0x00 and self.debug:
        commandType = sysex[6] + sysex[7] << 4
        if commandType == 0x02:
          print(f'{self.recv}Edit buffer desync!')
      elif messageType == 0x01 and self.debug:
        if sysex[6] == 0x04:
          print(f'{self.recv}Acknowledge')
        else:
          print(f'{self.alrt}{("No Acknowledgement", "Invalid Parameter Number", "Invalid Parameter Value", "Invalid Button Number")[sysex[7]]}')
      elif messageType == 0x02:
        if self.debug: print(f'{self.recv}Received program dump')
        self.loadProgramDump(sysex[6:-1])
      else:
        print(f'{self.alrt}Unknown message')
      
      if self.debug and self.linebreakRecv: print()

  def requestCurrentProgram(self):
    sysex = self.getSysexTemplate('currentProgramDumpRequest')
    
    if self.debug: 
      print(f'{self.trans}Requesting current program')
      
    midi.sendSysex(self.output, sysex)

  def pressButton(self, buttonId):
    sysexDown = self.getSysexTemplate('pressButton')
    sysexDown, _ = self.replace(sysexDown, 'button', self.encode8Bit(buttonId))
    
    sysexUp   = self.getSysexTemplate('pressButton')
    sysexUp, _ = self.replace(sysexUp, 'button', self.encode8Bit(buttonId+96))
    
    if self.debug: 
      print(f'{self.trans}Virtual button {buttonNames[buttonId]}')
      print(f'{self.info}Down')
    midi.sendSysex(self.output, sysexDown)
    
    t.delay(0.3) #Manual recommends 2-300ms delay
    
    if self.debug:
      print(f'{self.endNoRecv}Up')
    midi.sendSysex(self.output, sysexUp)

    if self.debug and self.linebreakRecv: print()
    
  def changeParameter(self, parameter, value):
    sysex = self.getSysexTemplate('parameterChange')
    
    paramKeys = parameter.split('.')
    param = self.params
    voice = 0
    pageOffset = 0
    for key in paramKeys:
      if 'voice' in key: voice = int(key[5:])
      param = param[key]
      if type(param) is dict: pageOffset += param['pageOffset']
    
    if 'wave' in param:
      t = param.split('.')[1]
      #self.changeParameter(f'voice{voice}.wave.{t}.waveClass', self.getWaveClass(value))
      self.changeParameter(f'voice{voice}.wave.{t}.waveName', value)
      return
    
    if value == param[2]: return
    else: param[2] = value
    
    if self.debug: 
      print(f'{self.trans}Parameter change {parameter} to {value}')
      
    sysex, _ = self.replace(sysex, 'voice', self.encode8Bit(voice))
    sysex, _ = self.replace(sysex, 'page', self.encode8Bit(pageOffset + param[0]))
    sysex, _ = self.replace(sysex, 'slot', self.encode8Bit(param[1]))
    sysex, _ = self.replace(sysex, 'value', self.encode16Bit(value))
    
    if self.debug: 
      print(f'{self.endNoRecv}Voice {voice}, Page {pageOffset+param[0]}, Slot {param[1]}')
      
    if self.debug and self.linebreakRecv: print()
    
    midi.sendSysex(self.output, sysex)


  def loadProgramDump(self, sysex):    
    values = []
    for i in range(0, len(sysex), 2):
      values.append(self.decode8Bit(sysex[i], sysex[i+1]))
      
    def neg(v):
      return v if v < 128 else v - 256
      
    self.params['voice0']['envelopes']['env0']['initialLevel'][2] = values[0]
    self.params['voice0']['envelopes']['env0']['attackTime'][2] = values[1]
    self.params['voice0']['envelopes']['env0']['peakLevel'][2] = values[2]
    self.params['voice0']['envelopes']['env0']['decay1Time'][2] = values[3]
    self.params['voice0']['envelopes']['env0']['breakpoint1Level'][2] = values[4]
    self.params['voice0']['envelopes']['env0']['decay2Time'][2] = values[5]
    self.params['voice0']['envelopes']['env0']['breakpoint2Level'][2] = values[6]
    self.params['voice0']['envelopes']['env0']['decay3Time'][2] = values[7]
    self.params['voice0']['envelopes']['env0']['sustainLevel'][2] = values[8]
    self.params['voice0']['envelopes']['env0']['releaseTime'][2] = min(values[9] if values[9] < 153 else values[9] - 153, 99)
    self.params['voice0']['envelopes']['env0']['levelVelocitySens'][2] = values[10]
    self.params['voice0']['envelopes']['env0']['attackTimeVelocitySens'][2] = values[11]
    self.params['voice0']['envelopes']['env0']['keyboardTrack'][2] = neg(values[12])
    self.params['voice0']['envelopes']['env0']['mode'][2] = (values[13] & 0xf0) >> 4
    self.params['voice0']['envelopes']['env0']['velocityCurve'][2] = values[13] & 0x0f
    
    self.params['voice0']['envelopes']['env1']['initialLevel'][2] = values[14]
    self.params['voice0']['envelopes']['env1']['attackTime'][2] = values[15]
    self.params['voice0']['envelopes']['env1']['peakLevel'][2] = values[16]
    self.params['voice0']['envelopes']['env1']['decay1Time'][2] = values[17]
    self.params['voice0']['envelopes']['env1']['breakpoint1Level'][2] = values[18]
    self.params['voice0']['envelopes']['env1']['decay2Time'][2] = values[19]
    self.params['voice0']['envelopes']['env1']['breakpoint2Level'][2] = values[20]
    self.params['voice0']['envelopes']['env1']['decay3Time'][2] = values[21]
    self.params['voice0']['envelopes']['env1']['sustainLevel'][2] = values[22]
    self.params['voice0']['envelopes']['env1']['releaseTime'][2] = min(values[23] if values[23] < 153 else values[23] - 153, 99)
    self.params['voice0']['envelopes']['env1']['levelVelocitySens'][2] = values[24]
    self.params['voice0']['envelopes']['env1']['attackTimeVelocitySens'][2] = values[25]
    self.params['voice0']['envelopes']['env1']['keyboardTrack'][2] = neg(values[26])
    self.params['voice0']['envelopes']['env1']['mode'][2] = (values[27] & 0xf0) >> 4
    self.params['voice0']['envelopes']['env1']['velocityCurve'][2] = values[27] & 0x0f
    
    self.params['voice0']['envelopes']['env2']['initialLevel'][2] = values[28]
    self.params['voice0']['envelopes']['env2']['attackTime'][2] = values[29]
    self.params['voice0']['envelopes']['env2']['peakLevel'][2] = values[30]
    self.params['voice0']['envelopes']['env2']['decay1Time'][2] = values[31]
    self.params['voice0']['envelopes']['env2']['breakpoint1Level'][2] = values[32]
    self.params['voice0']['envelopes']['env2']['decay2Time'][2] = values[33]
    self.params['voice0']['envelopes']['env2']['breakpoint2Level'][2] = values[34]
    self.params['voice0']['envelopes']['env2']['decay3Time'][2] = values[35]
    self.params['voice0']['envelopes']['env2']['sustainLevel'][2] = values[36]
    self.params['voice0']['envelopes']['env2']['releaseTime'][2] = min(values[37] if values[37] < 153 else values[37] - 153, 99)
    self.params['voice0']['envelopes']['env2']['levelVelocitySens'][2] = values[38]
    self.params['voice0']['envelopes']['env2']['attackTimeVelocitySens'][2] = values[39]
    self.params['voice0']['envelopes']['env2']['keyboardTrack'][2] = neg(values[40])
    self.params['voice0']['envelopes']['env2']['mode'][2] = (values[41] & 0xf0) >> 4
    self.params['voice0']['envelopes']['env2']['velocityCurve'][2] = values[41] & 0x0f
    
    self.updateGUI = True