SD = __import__('sd')
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


class VS():
  def __init__(self, inputID, outputID, debug=False, logParameterChanges=False):
    self.sd = SD.SD(inputID, outputID)
    self.input = self.sd.input
    
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
    
  def establishCommunications(self):
    return self.sd.establishCommunications()
    
  def decouple(self):
    self.sd.decouple()
    
  def couple(self):
    self.sd.couple()
    
  def getParameters(self):
    pass
    
  def changeWaveType(self, voice, t):
    pass
    
  def changeParameter(self, param, v):
    pass
    
  def requestCurrentProgram(self):
    pass
    
  def saveProgramDump(self):
    pass