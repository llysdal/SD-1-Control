from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import midi
t = __import__('tools')

midi.init()

#Gets all available midi devices, and information about them.
def getMidiDevices():
  midiInputs = {}
  midiOutputs = {}

  for deviceNum in range(midi.get_count()):
    n, name, input, output, n = midi.get_device_info(deviceNum)

    if input:
      #Trim the name, getting rid of the byte prefix
      midiInputs[str(name)[2:-1]] = deviceNum
    if output:
      midiOutputs[str(name)[2:-1]] = deviceNum

  return midiInputs, midiOutputs

def getDeviceInfo(id):
  info = midi.get_device_info(id)
  if type(info) == type(None):
    info = 0,0,0,0,0

  return info

def getMidiInputDevice(id):
  return midi.Input(id, 262144)

def getMidiOutputDevice(id):
  return midi.Output(id)

def clearMidi(device):
  device.read(1000)

def receiveAllMidi(device):
  message = device.read(1000)
  return message

def receiveMidi(device):
  dataPresent = device.poll()

  if dataPresent:
    messages = device.read(1024)
    return messages
  else:
    return False

def sendMidi(device, status, data1, data2):
  device.write_short(status, data1, data2)

def sendSysex(device, message):
  device.write_sys_ex(0, bytes(message))

def checkSysex(device):
  data = receiveMidi(device)

  if not data:
    return False, data

  if 0xF0 in data[0][0]:
    return True, data
  else:
    return False, data

def printSysex(sysex):
  print('├────── '+''.join([hex(d)+' ' for d in sysex]))

present = 0

def getSysex(device, sysexBuffer):
  #strip leading  
  while len(sysexBuffer) > 0 and sysexBuffer[0] != 0xF0:
    sysexBuffer.pop(0)
  
  sysex = sysexBuffer.copy()
  sysexBuffer = []
  

  if 0xF7 in sysex:
    endPntr = sysex.index(0xF7)
    if endPntr+1 < len(sysex):
      sysexBuffer = sysex[endPntr+1:].copy()
    else:
      sysexBuffer = []
        
    return True, sysex[0:endPntr+1], sysexBuffer

  # while True:
  data = receiveMidi(device)

  if data == False:
    return False, [], sysexBuffer

  for i, message in enumerate(data):
    sysex[len(sysex):len(sysex)] = message[0]

    if 0xF7 in message[0]:
      if i+1 < len(data):
        for m in range(i+1, len(data)):
          sysexBuffer[len(sysexBuffer):len(sysexBuffer)] = data[m][0]
      else:
        sysexBuffer = []
      return True, sysex[0:sysex.index(0xF7)+1], sysexBuffer
  
  sysexBuffer[len(sysexBuffer):len(sysexBuffer)] = sysex

  return False, [], sysexBuffer
