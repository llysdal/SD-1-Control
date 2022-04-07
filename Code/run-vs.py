VS = __import__('vs')
GUI = __import__('control-vs')
midi = __import__('midi')
fh = __import__('filehandler')
t = __import__('tools')
                                               
print("""
     _    _ _______ _______ _______  _____   ______      _______ __   __ __   _ _______ _     _
      \  /  |______ |          |    |     | |_____/      |______   \_/   | \  |    |    |_____|
       \/   |______ |_____     |    |_____| |    \_      ______|    |    |  \_|    |    |     |
""")

#Preinit config
configPresent, config = fh.getConfig()

#Handle config
debug = config.get('debug', None) == 'true'
logParameterChanges = config.get('logParameterChanges', None) == 'true'

#Chose MIDI input and Output
devices = midi.getMidiDevices()
mIn, mOut = t.chooseDevices(devices, config)

#Setup Vector Synthesizer
vs = VS.VS(mIn, mOut, debug=debug, logParameterChanges=logParameterChanges)

#Start GUI
root = GUI.tk.Tk()
gui = GUI.VSmain(root, vs, GUI.black)
gui.loadParameters(vs.getParameters())

#Startup sysex handling (handle all of the queue)
connectionEstablished, sysexBuffer = vs.establishCommunications()
if not connectionEstablished:
  vs.decouple()


def updateTask(sysexBuffer):
  gui.updateEnvs()

  #Check for sysex messages
  recv, sysex, sysexBuffer = midi.getSysex(vs.input, sysexBuffer)
  if recv:
    vs.decodeSysex(sysex)
  
  if vs.updateGUI:
    vs.updateGUI = False
    gui.loadParameters(vs.getParameters())

  gui.frame.after(50, updateTask, sysexBuffer)



root.protocol("WM_DELETE_WINDOW", lambda: quit())
updateTask(sysexBuffer)
root.mainloop()
