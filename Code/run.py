SD = __import__('sd')
GUI = __import__('control')
midi = __import__('midi')
fh = __import__('filehandler')
t = __import__('tools')
                                               
print("""
          ███████╗██████╗        ██╗
          ██╔════╝██╔══██╗      ███║
          ███████╗██║  ██║█████╗╚██║
          ╚════██║██║  ██║╚════╝ ██║
          ███████║██████╔╝       ██║
          ╚══════╝╚═════╝        ╚═╝
""")

#Preinit config
configPresent, config = fh.getConfig()

#Handle config
debug = config.get('debug', None) == 'true'
logParameterChanges = config.get('logParameterChanges', None) == 'true'

#Chose MIDI input and Output
devices = midi.getMidiDevices()
mIn, mOut = t.chooseDevices(devices, config)

#Setup SD-1 communication
sd = SD.SD(mIn, mOut, debug=debug, logParameterChanges=logParameterChanges)

#Start GUI
root = GUI.tk.Tk()
gui = GUI.SD1main(root, sd, GUI.black)
gui.loadParameters(sd.getParameters())

#Startup sysex handling (handle all of the queue)
connectionEstablished, sysexBuffer = sd.establishCommunications()
if not connectionEstablished:
  input('...')
  exit()


def updateTask(sysexBuffer):
  gui.updateEnvs()

  #Check for sysex messages
  recv, sysex, sysexBuffer = midi.getSysex(sd.input, sysexBuffer)
  if recv:
    sd.decodeSysex(sysex)
          
  #sd queue
  sd.handleQueue()
  
  if sd.updateGUI:
    sd.updateGUI = False
    gui.loadParameters(sd.getParameters())

  gui.frame.after(50, updateTask, sysexBuffer)



root.protocol("WM_DELETE_WINDOW", lambda: quit())
updateTask(sysexBuffer)
root.mainloop()
