fh = __import__('filehandler')
import tkinter as tk
from tkinter import N,S,E,W, HORIZONTAL, VERTICAL, BROWSE, filedialog, ttk, CENTER
from math import exp
import wave, struct
import json
from copy import deepcopy

midiKeys = []
for o in range(-1, 10):
  for k in range(0,12):
    midiKeys.append(('C','C#','D','D#','E','F','F#','G','G#','A','A#','B')[k] + str(o))
midiKeys = midiKeys[0:128]

envTimes = [0.00, 0.01, 0.02, 0.03, 0.04, 0.06, 0.07, 0.08, 0.08, 0.09, 0.10, 0.11, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16,
            0.17, 0.19, 0.20, 0.22, 0.23, 0.25, 0.27, 0.29, 0.31, 0.33, 0.35, 0.38, 0.41, 0.44, 0.47, 0.50, 0.54, 0.58,
            0.62, 0.66, 0.71, 0.76, 0.82, 0.88, 0.94, 1.0, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0, 2.1, 2.3,
            2.4, 2.6, 2.8, 3.0, 3.2, 3.5, 3.7, 4.0, 4.3, 4.6, 4.9, 5.3, 5.7, 6.1, 6.5, 7.0, 7.5, 8.1, 8.6, 9.3, 9.9, 10,
            11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 26, 28, 30, 32, 34, 37, 39, 42, 45, 49, 60] #60?

black = "#1f1f1f"
red = "#9D0000"
lightRed = "#f7bebe"
washedRed = "#6e3d3d"
darkRed = "#340000"
grey  = '#3e3e3e'
darkGrey = '#282828'
white = '#e2e2e2'
blue  = '#336ece'

normalEnvColor = '#2b7cff'
finishEnvColor = "#2bff7c"
loopEnvColor = "#ff2b2b"


class spinbox(tk.Spinbox):
  def set(self, value):
    self.delete(0,100)
    self.insert(0,value)

class Application():  
  def init(self, master, background):
    self.master = master
    self.frame = tk.Frame(self.master, background="#9D0000")
    self.frame.grid(column=0, row=0, sticky=N+S+E+W)

    #Resizeability
    self.top = self.frame.winfo_toplevel()
    self.top.rowconfigure(0, weight=1)
    self.top.columnconfigure(0, weight=1)

    self.titlefont = ('Microgramma D Extended', 14)
    self.textfont = ('Lucida Sans', 11)
    self.smalltextfont = ('Lucida Sans', 8)
    self.numberfont = ('Lucida Sans', 10)
    
    self.background = background

    self.frame.configure(background = black)

  def resizableC(self, c):
    self.frame.columnconfigure(c, weight=1)
  def resizableR(self, r):
    self.frame.rowconfigure(r, weight=1)
    
  def padC(self, c, pad):
    self.frame.columnconfigure(c, pad=pad)
  def padR(self, r, pad):
    self.frame.rowconfigure(r, pad=pad)
    
  def createCGap(self, c, size):
    self.frame.columnconfigure(c, minsize=size)
  def createRGap(self, r, size):
    self.frame.rowconfigure(r, minsize=size)
    

  def createCanvas(self, gridpos, columnspan = 1, rowspan = 1, size = (100,100)):
    canvas = tk.Canvas(self.frame, width = size[0], height = size[1], bg = 'black', relief='ridge', borderwidth=2, highlightthickness=0)
    canvas.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, rowspan = rowspan, sticky = N+S+E+W)

    return canvas
  
  def createTabs(self, gridpos, columnspan=1, rowspan=1, command = None):
    tabs = ttk.Notebook(self.frame)
    tabs.grid(column=gridpos[0], row=gridpos[1], columnspan=columnspan, rowspan=rowspan, sticky=N+S+E+W)
    self.frame.columnconfigure(gridpos[0], weight=1)
    self.frame.rowconfigure(gridpos[1], weight=1)
    
    if command:
      tabs.bind("<<NotebookTabChanged>>", 
        lambda event, command=command: command(event.widget.index("current")))
    
    return tabs
  
  def createTab(self, tabFrame, name, background=None):
    tab = ttk.Frame(tabFrame)
    tabFrame.add(tab, text=name)
    
    if background == None: background = self.background
    
    app = Application()
    app.init(tab, background)
    app.frame.grid(column=0, row=0, sticky=N+S+E+W)
    app.frame.configure(background=background)
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(0, weight=1)
    
    return app, tab
  
  def createSlider(self, gridpos, val, res = 1, start = 0, length = 100, width = 15, orient = 0, columnspan = 1, rowspan = 1, showvalue = True, sticky = E+S, command = lambda s: None):
    slider = tk.Scale(self.frame, from_ = val[0], to = val[1], resolution = res,\
                      orient = (HORIZONTAL, VERTICAL)[orient], length = length, showvalue = showvalue, width = width,
                      command = command)
    slider.configure(foreground = white, background = self.background, highlightthickness = 0, troughcolor = grey, activebackground = white, font = self.numberfont)
    slider.grid(column = gridpos[0], row = gridpos[1], rowspan = rowspan, columnspan = columnspan, sticky = sticky)

    slider.set(start)

    return slider

  def createMenuButton(self, gridpos, sticky = E+S, columnspan=1, width=10, value=0, command=None, disabled=False):    
    labelVar = tk.StringVar(value='default')
    var = tk.IntVar(value=value)
    
    menubutton = ttk.Menubutton(self.frame, textvariable=labelVar, width=width)
    if disabled: menubutton.state(["disabled"])
    menu = tk.Menu(menubutton, tearoff=0, borderwidth=0, activeborderwidth=0)
    menubutton['menu'] = menu
    menubutton.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)
    
    if command:
      var.trace_add("write", lambda x, y, z, var=var: command(var.get()))

    return menu, var, labelVar
  
  def createMenuButtonOptions(self, menubutton, labels, variable, labelvariable):
    for v, l in enumerate(labels):
      menubutton.add_radiobutton(label=l, value=v, variable=variable)
      
    variable.trace_add("write", lambda x, y, z, var=variable, t=labels, l=labelvariable: l.set(t[var.get()]))
  
  def createModSourceSelector(self, gridpos, sticky = E+S, command=None, width=17):
    menu, var, label = self.createMenuButton(gridpos, sticky=sticky, width=width)
    
    var.set(15)
    menu.add_radiobutton(label='*OFF*', value=15, variable=var)
    menu.add_radiobutton(label='LFO', value=0, variable=var)
    menu.add_radiobutton(label='Noise', value=3, variable=var)
    menu.add_radiobutton(label='Envelope 1', value=1, variable=var)
    menu.add_radiobutton(label='Envelope 2', value=2, variable=var)
    menu.add_radiobutton(label='Mixer', value=4, variable=var)
    menu.add_radiobutton(label='Pitch', value=9, variable=var)
    keyb = tk.Menu(menu, tearoff=0)
    keyb.add_radiobutton(label='Velocity', value=5, variable=var)
    keyb.add_radiobutton(label='Pressure', value=14, variable=var)
    keyb.add_radiobutton(label='Pressure + Velocity', value=11, variable=var)
    keyb.add_radiobutton(label='Pedal', value=8, variable=var)
    keyb.add_radiobutton(label='Wheel', value=13, variable=var)
    keyb.add_radiobutton(label='Wheel + Pressure', value=12, variable=var)
    keyb.add_radiobutton(label='Timbre', value=7, variable=var)
    keyb.add_radiobutton(label='Keyboard', value=6, variable=var)
    menu.add_cascade(label='Keyboard', menu=keyb)
    menu.add_radiobutton(label='X-Ctrl', value=10, variable=var)
    label.set('*OFF*')
    
    texts = ['LFO', 'Envelope 1', 'Envelope 2', 'Noise', 'Mixer', 'Velocity', 'Keyboard', 'Timbre', 'Pedal', 'Pitch', 'X-Ctrl', 'Pressure + Velocity', 'Wheel + Pressure', 'Wheel', 'Pressure', '*OFF*']
    var.trace_add("write", lambda x, y, z, var=var, t=texts, l=label: l.set(t[var.get()]))
    
    if command:
      var.trace_add("write", lambda x, y, z, var=var: command(var.get()))
    
    return var
  
  def createToggleButton(self, gridpos, text, default=0, sticky=N+S+E+W, columnspan=1, command = None, threeState = False):
    var = tk.IntVar(value=default)
    on, off, three = red, grey, blue
    
    button = tk.Button(self.frame, text = text, command = lambda var=var: var.set(0) if var.get() else var.set(1))
    button.configure(foreground = white, activeforeground = white, activebackground = on if var.get() else off, background = on if var.get() else off)
    button.grid(column = gridpos[0], row = gridpos[1], stick = sticky, columnspan=columnspan)
    
    if not threeState:
      var.trace_add("write", lambda x, y, z, var=var, b=button, off=off, on=on: b.configure(background=on, activebackground=on) if var.get() else b.configure(background=off, activebackground=off))
    else:
      button.bind("<Button-3>", lambda event, var=var: var.set(2) if var.get() < 2 else var.set(1))
      var.trace_add("write", lambda x, y, z, var=var, b=button, off=off, on=on, three=three: (b.configure(background=on, activebackground=on) if var.get() == 1 else b.configure(background=three, activebackground=three)) if var.get() else b.configure(background=off, activebackground=off))
    
    if command:
      var.trace_add("write", lambda x, y, z, var=var: command(var.get()))
      
    return var

  def createDropdown(self, gridpos, values = [1,2,3], start = 1, columnspan = 1, requestparent = False, command = lambda s: None):
    string = tk.StringVar(self.frame)
    string.set(start)

    dropdown = tk.OptionMenu(self.frame, string, *values, command=command)
    dropdown.configure(foreground = white, background = self.background, highlightthickness = 0, borderwidth = 2)
    dropdown.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = E+S)

    if requestparent:
      return string, dropdown

    return string

  def createButton(self, gridpos, text, function):
    button = tk.Button(self.frame, text = text, command = function)
    button.configure(foreground = white, background = self.background)
    button.grid(column = gridpos[0], row = gridpos[1], stick = N+S+E+W)

  def createSmallText(self, gridpos, text, columnspan = 1, sticky = N+W+E, justify='center'):
    label = tk.Label(self.frame, text = text, font = self.smalltextfont, justify = justify)
    label.configure(foreground = white, background = self.background)
    label.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return label

  def createText(self, gridpos, text, columnspan = 1, sticky = W+S):
    label = tk.Label(self.frame, text = text, font = self.textfont, justify = 'left')
    label.configure(foreground = white, background = self.background)
    label.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return label

  def createTitle(self, gridpos, text, columnspan = 1, sticky = E+W):
    label = tk.Label(self.frame, text = text, font = self.titlefont, justify = 'left')
    label.configure(foreground = white, background = self.background)
    label.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return label

  def createDynText(self, gridpos, columnspan = 1, sticky = E+N):
    stringvar = tk.StringVar()

    label = tk.Label(self.frame, textvariable = stringvar, font = self.numberfont, justify = 'left')
    label.configure(foreground = white, background = self.background)
    label.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return stringvar
  
  def createTextEntry(self, gridpos, sticky = E+W+S, width=12, command = None):
    stringvar = tk.StringVar()
    
    entry = tk.Entry(self.frame, textvariable = stringvar, background=grey, foreground=white, insertbackground=white, width=width)
    entry.grid(column = gridpos[0], row = gridpos[1], sticky = sticky)
    
    return stringvar

  def createCheckbutton(self, gridpos, text, columnspan = 1, sticky = E+S):
    intvar = tk.IntVar()

    button = tk.Checkbutton(self.frame, text = text, variable = intvar, onvalue = 1, offvalue = 0)
    button.configure(background = self.background)
    button.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return intvar

  def createSpinbox(self, gridpos, from_ = 0, to = 10, values = [], width = 2, sticky = E+N, command = lambda: None):
    if len(values) > 0:
      spin = spinbox(self.frame, values = values, width = width, command = command)
    else:
      spin = spinbox(self.frame, from_=from_, to=to, width = width, command = command)
    spin.grid(column = gridpos[0], row = gridpos[1], sticky = sticky)

    return spin

  def createMenu(self):
    menubar = tk.Menu(self.frame)
    self.top.config(menu=menubar)

    return menubar

  def minSizeX(self, x, width):
    self.frame.columnconfigure((x,0), minsize = width)

  def minSizeY(self, y, width):
    self.frame.rowconfigure((0,y), minsize = width)


class SD1main(Application):
  def __init__(self, master, sd, background):
    self.sd = sd
    
    s = ttk.Style()
    s.theme_create('sd', settings={
      'TText': {
        'configure': {
          'foreground': white
        }
      },
      'TLabel': {
        'configure': {
          'background': black, 
          'foreground': white
        }
      },
      'TFrame': {
        'configure': {
          'background': black
        }
      },
      'TMenubutton': {
        'configure': {
          'background': grey,
          'foreground': white,
          'borderwidth': 2,
          'relief': 'ridge',
          'anchor': 'center',
        }
      },
      'TNotebook': {
        'configure': {
          'background': black,#darkRed,
          'tabmargins': [0, 0, 0, 0],
          'padding': [0, 0]
        }
      },
      'TNotebook.Tab': {
        'configure': {
          'foreground': white,
          'background': washedRed,
          'padding': [5, 2],
          'focuscolor': 'clear',
        },
        'map': {
          'background': [('selected', red)]
        }
      }
    })
    s.theme_use('sd')
    s.layout('TMenubutton', [('Menubutton.border',
      {'sticky': 'nswe',
      'children': [('Menubutton.focus',
        {'sticky': 'nswe',
          'children': [
          ('Menubutton.padding',
            {'expand': '1',
            'sticky': 'we',
            'children': [('Menubutton.label',
              {'side': 'left', 'sticky': ''})]})]})]})])
    
    self.init(master, background)
    self.setup(sd)
    
  def envDrag(self, event, voice, env, step):
    v = self.voices[voice]
    envVars = v.envVars[env]
    
    rectSize = 4
    w = 500-rectSize
    h = 100
    if step == 0:
      envVars[0][0] = min(127, max(0, 127 - int(event.y/h * 127)))
    elif step == 1:
      envVars[0][1] = min(127, max(0, 127 - int(event.y/h * 127)))
      envVars[1][0] = min(99, max(0, int((event.x-rectSize)/(w/6) * 99)))
    elif step == 2:
      offset = w/6*envVars[1][0]/99
      envVars[0][2] = min(127, max(0, 127 - int(event.y/h * 127)))
      envVars[1][1] = min(99, max(0, int(((event.x-rectSize)-offset)/(w/6) * 99)))
    elif step == 3:
      offset = w/6*envVars[1][0]/99 + w/6*envVars[1][1]/99
      envVars[0][3] = min(127, max(0, 127 - int(event.y/h * 127)))
      envVars[1][2] = min(99, max(0, int(((event.x-rectSize)-offset)/(w/6) * 99)))
    elif step == 4:
      offset = w/6*envVars[1][0]/99 + w/6*envVars[1][1]/99 + w/6*envVars[1][2]/99
      envVars[0][4] = min(127, max(0, 127 - int(event.y/h * 127)))
      envVars[1][3] = min(99, max(0, int(((event.x-rectSize)-offset)/(w/6) * 99)))
    elif step == 5:
      offset = w/6*envVars[1][0]/99 + w/6*envVars[1][1]/99 + w/6*envVars[1][2]/99 + w/6*envVars[1][3]/99 + w/6
      envVars[1][4] = min(99, max(0, int(((event.x-rectSize)-offset)/(w/6) * 99)))
    
  def updateEnvs(self):
    rectSize = 4
    w = 500-rectSize
    h = 100
    
    for voice in self.voices:
      for envIndex, (env, envVars, envMode) in enumerate(zip(voice.envs, voice.envVars, voice.envModes)):
        color = (normalEnvColor, finishEnvColor, loopEnvColor)[envMode.get()]
        
        lastPoint = (rectSize,0)
        for step, (level, duration) in enumerate(zip([*envVars[0], 0], [0, *envVars[1]])):
          newPoint = (lastPoint[0] + w/6*duration/99, (h-rectSize)-(h-rectSize*2)*level/127)
          if step == 5:
            line = env.find_withtag(f'line{step-1}')
            env.itemconfigure(line, fill=color)
            env.coords(line, lastPoint[0], lastPoint[1], lastPoint[0]+w/6, lastPoint[1])
            lastPoint = (lastPoint[0]+w/6, lastPoint[1])
            newPoint = (lastPoint[0] + w/6*duration/99, (h-rectSize)-(h-rectSize*2)*level/127)
            line = env.find_withtag(f'line{step}')
            env.itemconfigure(line, fill=color)
            env.coords(line, lastPoint[0], lastPoint[1], newPoint[0], newPoint[1])
          elif step > 0:
            line = env.find_withtag(f'line{step-1}')
            env.itemconfigure(line, fill=color)
            env.coords(line, lastPoint[0], lastPoint[1], newPoint[0], newPoint[1])
          
          if step > 0: 
            durText = env.find_withtag(f'duration{step-1}')
            env.coords(durText, (newPoint[0]-lastPoint[0])/2+lastPoint[0], (newPoint[1]-lastPoint[1])/2+lastPoint[1])
            try: sDur = f'{envTimes[duration]}s'
            except: sDur = 'err'
            env.itemconfigure(durText, text=sDur)
          
          rect = env.find_withtag(f'step{step}')
          env.itemconfigure(rect, fill=color)
          env.coords(rect, newPoint[0]-rectSize, newPoint[1]-rectSize, newPoint[0]+rectSize, newPoint[1]+rectSize)
          lastPoint = newPoint
          
  def emitEnv(self, event, voice, env, step):
    v = self.voices[voice]
    envVars = v.envVars[env]
    
    if step == 0:
      self.sd.changeParameter(f'voice{voice}.envelopes.env{env}.initialLevel', envVars[0][0])
    elif step == 5:
      self.sd.changeParameter(f'voice{voice}.envelopes.env{env}.releaseTime', envVars[1][4])
    else:
      self.sd.changeParameter(f'voice{voice}.envelopes.env{env}.{["", "peakLevel", "breakpoint1Level", "breakpoint2Level", "sustainLevel"][step]}', envVars[0][step])
      self.sd.changeParameter(f'voice{voice}.envelopes.env{env}.{["attackTime", "decay1Time", "decay2Time", "decay3Time", ""][step-1]}', envVars[1][step-1])

  def copyEnvelope(self, voice, env):
    if not self.envelopeCopy:
      for v in self.voices:
        for e in v.envContexts:
          e.entryconfig("Paste", state=tk.ACTIVE)
    
    v = self.voices[voice]
    self.envelopeCopy = deepcopy(v.envVars[env])
  
  def pasteEnvelope(self, voice, env):
    if not self.envelopeCopy: 
      return
    
    v = self.voices[voice]
    v.envVars[env] = deepcopy(self.envelopeCopy)

  def onVoiceStatusChange(self, voice, status):
    if self.isChangingVoiceStatus: return
    self.isChangingVoiceStatus = True
    if status < 2:
      self.sd.changeParameter(f'selectVoice.voice{voice}Status', status)
      for v in range(6):
        if self.voiceStatus[v].get() == 2:
          self.sd.changeParameter(f'selectVoice.voice{v}Status', 2, force=True)
    else:
      #solo
      self.sd.changeParameter(f'selectVoice.voice{voice}Status', 2)
      shouldDecouple = not self.sd.decoupled
      if shouldDecouple: self.sd.decouple()
      for v in range(6):
        if v == voice: continue
        if self.voiceStatus[v].get() == 2: 
          self.voiceStatus[v].set(1)
          self.sd.changeParameter(f'selectVoice.voice{v}Status', 1)
      if shouldDecouple: self.sd.couple()
    self.isChangingVoiceStatus = False

  def setup(self, sd):
    self.master.title('Ensoniq SD-1 Main Control')
    self.master.iconbitmap(fh.getRessourcePath('sd.ico'))
    
    self.master.minsize(500, 300)

    self.menu = self.createMenu()
    
    systemmenu = tk.Menu(self.menu, tearoff=0)
    systemmenu.add_command(label="Bank 0", command=lambda sd=sd: sd.pressButton(0))
    systemmenu.add_command(label="Master", command=lambda sd=sd: sd.pressButton(22))
    self.menu.add_cascade(label='System', menu=systemmenu)
    
    self.menu.add_command(label="\u22EE", activebackground=self.menu.cget("background"), state=tk.DISABLED)

    programmenu = tk.Menu(self.menu, tearoff=0)
    programmenu.add_command(label='Request current', command=lambda sd=sd: sd.requestCurrentProgram())
    programmenu.add_command(label='Send current', command=lambda sd=sd: sd.saveProgramDump())
    self.menu.add_cascade(label='Programs', menu=programmenu)
    
    self.menu.add_command(label="\u22EE", activebackground=self.menu.cget("background"), state=tk.DISABLED)
    
    optionmenu = tk.Menu(self.menu, tearoff=0)
    self.menu.add_cascade(label='Options', menu=optionmenu)

    self.createRGap(0, 5)
    mainTabs = self.createTabs((0,1))
    masterFrame, masterTab = self.createTab(mainTabs, 'Master')
    midiFrame, midiTab = self.createTab(mainTabs, 'MIDI')
    programFrame, programTabs = self.createTab(mainTabs, 'Voices')
    mainTabs.select(programTabs)

    programFrame.createRGap(0, 5)
    programTabs = programFrame.createTabs((0,1))
    controlFrame, controlTab = programFrame.createTab(programTabs, 'Control')
    voice0Frame, voice0Tab = programFrame.createTab(programTabs, 'Voice 1')
    voice1Frame, voice1Tab = programFrame.createTab(programTabs, 'Voice 2')
    voice2Frame, voice2Tab = programFrame.createTab(programTabs, 'Voice 3')
    voice3Frame, voice3Tab = programFrame.createTab(programTabs, 'Voice 4')
    voice4Frame, voice4Tab = programFrame.createTab(programTabs, 'Voice 5')
    voice5Frame, voice5Tab = programFrame.createTab(programTabs, 'Voice 6')
    #programTabs.select(voice0Tab)
    
    selectorWidth = 25
    sectionGap = 20
    innerGap = 30
    outerGap = 0
    panelInnerGap = 15
    
    c = controlFrame
    c.createCGap(0, 10)
    c.createCGap(100, 10)
    c.createRGap(0, 10)
    c.createRGap(100, 10)
    
    c.program = Application()
    c.program.init(c.frame, darkGrey)
    c.program.frame.grid(column = 1, row = 1, columnspan = 2)
    c.program.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
    c.program.createTitle((1, 0), 'Program', columnspan=7)
    c.program.createCGap(0, panelInnerGap)
    self.programName = c.program.createTextEntry((1,2))
    c.program.createSmallText((1, 3), 'Name')
    self.bendRange = c.program.createSlider((1, 4), (0, 13), start = 0, width=18, length = 150, sticky=S+E+W, command=lambda x, sd=sd:sd.changeParameter(f'programControl.bendRange', int(x)))
    c.program.createSmallText((1, 5), 'Pitch Bend Range')
    c.program.createCGap(2, 10)
    self.glideTime = c.program.createSlider((3, 4), (0, 99), start = 0, width=18, length = 200, sticky=S+E+W, command=lambda x, sd=sd:sd.changeParameter(f'programControl.glideTime', int(x)))
    c.program.createSmallText((3, 5), 'Glide Time')
    c.program.createCGap(4, 10)
    self.restrikeDelay = c.program.createSlider((5, 4), (0, 99), start = 0, width=18, length = 200, sticky=S+E+W, command=lambda x, sd=sd:sd.changeParameter(f'programControl.restrikeDelay', int(x)))
    c.program.createSmallText((5, 5), 'Restrike Delay')
    c.program.createCGap(6, 10)
    delayMultiplier, self.delayMultiplier, delayMultiplierLabel = c.program.createMenuButton((7, 4), sticky=S+E+W, width=18,
                                                                    command=lambda x: sd.changeParameter(f'programControl.delayMultiplier', x))
    c.program.createMenuButtonOptions(delayMultiplier, ['x1', 'x2', 'x4', 'x8'], self.delayMultiplier, delayMultiplierLabel)
    c.program.createSmallText((7, 5), 'Delay Multiplier')
    c.program.createCGap(8, panelInnerGap)
    c.program.createRGap(3, panelInnerGap-5)
    
    c.createRGap(2, 20)
    
    c.voices = Application()
    c.voices.init(c.frame, darkGrey)
    c.voices.frame.grid(column = 1, row = 3)
    c.voices.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
    c.voices.createTitle((1, 0), 'Voices', columnspan=11)
    c.voices.createCGap(0, panelInnerGap)
    c.voices.createRGap(1, 10)
    self.isChangingVoiceStatus = False
    self.voiceStatus = []
    for i in range(6):
      self.voiceStatus.append(c.voices.createToggleButton((i*2+1, 2), f'Voice {i+1}', threeState=True, command=lambda x, i=i, gui=self:gui.onVoiceStatusChange(i, x)))
      c.voices.resizableC(i*2+1)
      if i > 0: c.voices.createCGap(i*2, 10)
    c.voices.createCGap(13, panelInnerGap)
    c.voices.createRGap(3, panelInnerGap)
      
    self.envelopeCopy = None
    
    self.voices = [voice0Frame, voice1Frame, voice2Frame, voice3Frame, voice4Frame, voice5Frame]
    for v in range(6):
      f = self.voices[v]

      f.createCGap(0, 10)
      f.createRGap(0, 10)
      f.createRGap(100, 10)
      
      #f.createTitle((c, r), 'Wave', columnspan=2)
      f.waveTabs = f.createTabs((1,1), rowspan=2, command=lambda x, sd=sd, v=v: sd.changeWaveType(v, x))
      f.waveformFrame, f.waveformTab = f.createTab(f.waveTabs, 'Waveform')
      f.transwaveFrame, f.transwaveTab = f.createTab(f.waveTabs, 'Transwave')
      f.sampledFrame, f.sampledTab = f.createTab(f.waveTabs, 'Sampled')
      f.multiwaveFrame, f.multiwaveTab = f.createTab(f.waveTabs, 'Multiwave')
      
      f.createCGap(2, 15)
      
      
      # WAVEFORM
      f.waveformFrame.createSmallText((1, 2), 'Wave')
      waveformWave, f.waveformWave, waveformWaveLabel = f.waveformFrame.createMenuButton((1, 1), sticky=S+E+W, width=22)
      analog = tk.Menu(waveformWave, tearoff=0)
      waveformWave.add_cascade(label='Analog', menu=analog)
      tk.Menu().add_cascade
      digital = tk.Menu(waveformWave, tearoff=0)
      waveformWave.add_cascade(label='Digital', menu=digital)
      wind = tk.Menu(waveformWave, tearoff=0)
      waveformWave.add_cascade(label='Wind', menu=wind)
      organ = tk.Menu(waveformWave, tearoff=0)
      waveformWave.add_cascade(label='Organ', menu=organ)
      inharm = tk.Menu(waveformWave, tearoff=0)
      waveformWave.add_cascade(label='Inharmonic', menu=inharm)
      waveforms = [
        [analog,
        [
          ('Sawtooth', 84),
          ('Sawtooth (2 harmonics)', 89),
          ('Square', 85),
          ('Square (2 harmonics)', 88),
          ('Triangle', 87),
          ('Sine', 86),
        ]],
        [digital,
        [
          ('Digital Piano Tine', 91),
          ('Bubbawave', 92),
          ('Synth Bell', 100),
          ('Vocal Bell', 99),
          ('Digital Vox', 101),
        ]],
        [wind,
        [
          ('Clavinet', 93),
          ('Clavinet (var.)', 94),
          ('Clarinet', 102),
          ('Woodwind', 95),
          ('Woodwind (var.)', 96),
          ('Brass Organ', 98),
        ]],
        [organ,
        [
          ('Organ (var. 1)', 80),
          ('Organ (var. 2)', 81),
          ('Organ (var. 3)', 82),
          ('Organ (var. 4)', 83),
          ('Pipe Organ', 97),
        ]],
        [inharm,
        [
          ('Triangle', 103),
          ('Anvil', 104),
          ('Cluster', 105),
          ('Tubular', 106),
          ('Noise', 107),
        ]],
        ('Fretless', 90),
      ]
      waveMap = {}
      for elm in waveforms:
        if type(elm) == list:
          cat, waves = elm
          for w, i in waves:
            cat.add_radiobutton(label=w, value=i, variable=f.waveformWave)
            waveMap[i] = w
        else:
          w, i = elm
          waveformWave.add_radiobutton(label=w, value=i, variable=f.waveformWave)
          waveMap[i] = w
          
      f.waveformWave.trace_add("write", lambda x, y, z, var=f.waveformWave, l=waveformWaveLabel, wm=waveMap:
        l.set(wm[var.get()]))
      f.waveformWave.trace_add("write", lambda x, y, z, var=f.waveformWave, v=v, sd=sd:(
        sd.changeParameter(f'voice{v}.wave.waveform.waveName', var.get())))
      f.waveformFrame.createRGap(0, 21)
      f.waveformFrame.createCGap(0, 15)
      f.waveformFrame.createCGap(2, 15)
      
      # TRANSWAVE
      f.transwaveFrame.createSmallText((1, 2), 'Wave')
      transwaveWave, f.transwaveWave, transwaveWaveLabel = f.transwaveFrame.createMenuButton((1, 1), sticky=S+E+W, width=16)
      waveforms = [
        ('Spectral', 63),
        ('Digital', 64),
        ('Vocal', 65),
        ('Doctor', 66),
        ('Inharmonic', 67),
        ('Synchro', 68),
        ('Omega', 69),
        ('ESQ Bell', 70),
        ('Planet', 72),
        ('Electro', 73),
        ('Formant', 71),
        ('Pulse 1', 74),
        ('Pulse 2', 75),
        ('Resonant 1', 76),
        ('Resonant 2', 77),
        ('Resonant 3', 78),
        ('Resonant 4', 79),
      ]
      waveMap = {}
      for w, i in waveforms:
        transwaveWave.add_radiobutton(label=w, value=i, variable=f.transwaveWave)
        waveMap[i] = w
        
      f.transwaveWave.trace_add("write", lambda x, y, z, var=f.transwaveWave, l=transwaveWaveLabel, wm=waveMap:
        l.set(wm[var.get()]))
      f.transwaveWave.trace_add("write", lambda x, y, z, var=f.transwaveWave, v=v, sd=sd:(
        sd.changeParameter(f'voice{v}.wave.transwave.waveName', var.get())))
      f.transwaveStart = f.transwaveFrame.createSlider((3, 1), (0, 99), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.transwave.waveStart', int(x)))
      f.transwaveFrame.createSmallText((3, 2), 'Start')
      f.transwaveModAmount = f.transwaveFrame.createSlider((3, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.transwave.waveModAmount', int(x)))
      f.transwaveModSource = f.transwaveFrame.createModSourceSelector((3, 4), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.wave.transwave.waveModSource', x))
      f.transwaveFrame.createSmallText((3, 5), 'Mod')
      f.transwaveFrame.createRGap(0, 5)
      f.transwaveFrame.createCGap(0, 15)
      f.transwaveFrame.createCGap(2, 10)
      f.transwaveFrame.createCGap(4, 15)
      
      # SAMPLED
      f.sampledFrame.createSmallText((1, 2), 'Wave')
      sampledWave, f.sampledWave, sampledWaveLabel = f.sampledFrame.createMenuButton((1, 1), sticky=S+E+W, width=18)
      piano = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='Piano', menu=piano)
      
      guitar = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='Guitar', menu=guitar)
      bass = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='Bass', menu=bass)
      
      brass = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='Brass', menu=brass)
      string = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='String', menu=string)
      breath = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='Breath', menu=breath)
      
      drum = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='Drum', menu=drum)
      drumKits = tk.Menu(sampledWave, tearoff=0)
      drum.add_cascade(label='Kits', menu=drumKits)
      multiDrum = tk.Menu(sampledWave, tearoff=0)
      drum.add_cascade(label='Multi-Drum', menu=multiDrum)
      hipPerc = tk.Menu(sampledWave, tearoff=0)
      drum.add_cascade(label='TR-808', menu=hipPerc)
      
      perc = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='Percussion', menu=perc)
      
      tunedPerc = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='Misc', menu=tunedPerc)
      
      sfx = tk.Menu(sampledWave, tearoff=0)
      sampledWave.add_cascade(label='SFX', menu=sfx)
      
      waveforms = [
        [piano,
        [
          ('Piano', 141),
          ('Piano (low)', 148),
          ('Piano (high)', 144),
          ('Piano (var. 1)', 142),
          ('Piano (var. 2)', 3),
          ('Electric Piano (soft)', 146),
          ('Electric Piano (hard)', 147),
          ('Grand Piano', 2),
          ('Digital Piano', 4),
          ('Clavinet', 5),
          ('Sympathic', 145),
          ('Piano Thump', 149),
          ('Piano Noise', 143),
          ('Piano Ping', 42),
        ]],
        [string,
        [
          ('Strings', 0),
          ('Pizzicato Strings', 1),
          ('Violin', 163),
          ('Violin (var.)', 164),
        ]],
        [guitar,
        [
          ('Acoustic Guitar', 6),
          ('Guitar', 7),
          ('Guitar (var.)', 8),
          ('Guitar Harmonics', 9),
          ('Electric Guitar', 10),
          ('Pluck Guitar', 11),
          ('Chukka Guitar', 12),
          ('Crunch Guitar', 13),
          ('Crunch Guitar (loop)', 14),
        ]],
        [bass,
        [
          ('Pick Bass', 23),
          ('Slap Bass', 165),
          ('Pop Bass', 24),
          ('Pluck Bass', 25),
          ('Double Bass', 26),
          ('Synth Bass (var. 1)', 27),
          ('Synth Bass (var. 2)', 28),
          ('Synth Bass (var. 3)', 166),
        ]],
        [brass,
        [
          ('Uni Brass', 15),
          ('Trumpet', 16),
          ('Trumpet (var.)', 17),
          ('Frenchhorn', 18),
          ('Frenchhorn (var.)', 19),
          ('Saxophone (var. 1)', 20),
          ('Saxophone (var. 2)', 21),
          ('Saxophone (var. 3)', 22),
        ]],
        [breath,
        [
          ('Wood Flute', 29),
          ('Chiff Flute', 30),
          ('Ocarina', 31),
          ('Vox Ooohs', 32),
          ('Vocal Pad', 33),
        ]],
        [tunedPerc,
        [
          ('Marimba', 34),
          ('Kalimba', 35),
          ('Vibes', 161),
          ('Steeldrum', 36),
          ('Plinkhorn', 40),
          ('Flutedrum', 41),
          ('Rackbell', 45),
          ('Synth Pluck', 39),
          ('Steamdrum', 55),
        ]],
        [sfx,
        [
          ('Orchestral Hit', 43),
          ('Big Blast', 56),
          ('Doorbell', 37),
          ('Duct Tape', 54),
          ('Spray Can', 57),
          ('Slinky Pop', 53),
          ('Potlid Hit', 38),
          ('Anvil Hit', 60),
          ('Metal Dink', 58),
          ('Kagong', 44),
          ('Toy Hammer', 51),
        ]],
        [perc,
        [
          ('Tambourine', 125),
          ('Shaker', 151),
          ('Agogo', 52),
          ('Wood Block', 48),
          ('Temple Block', 49),
          ('Woody Hit', 47),
          ('Dinky Hit', 50),
          ('Vocal Percussion', 59),
        ]],
        [drum,
        [
          ('-',0),
          ('Kick', 61),
          ('Room Kick', 110),
          ('Gated Kick', 109),
          ('-',0),
          ('Snare', 62),
          ('Piccolo Snare', 150),
          ('Gated Snare', 111),
          ('Rim Snare', 112),
          ('-',0),
          ('Hi-hat (closed)', 113),
          ('Hi-hat (open)', 114),
          ('Ride Cymbal', 115),
          ('Crash Cymbal', 46),
          ('-',0),
          ('Dry Toms', 134),
          ('Dry Tom (low', 116),
          ('Dry Tom (high)', 117),
          ('Room Toms', 135),
          ('Gated Toms', 136),
          ('Gated Tom (low)', 118),
          ('Gated Tom (high)', 119),
          ('Rim Tom (low)', 120),
          ('Rim Tom (high)', 121),
          ('Timbale', 122),
          ('Tympani', 162),
          ('Congas', 137),
          ('Congo (low)', 123),
          ('Congo (high)', 124),
        ]],
        [drumKits,
        [
          ('Drum Map', 167),
          ('Standard Kit', 138),
          ('Gated Kit', 139),
          ('Room Kit', 140),
          ('TR-808 Kit', 160),
          ('All Percussion', 126),
          ('All Drums', 127),
        ]],
        [multiDrum,
        [
          ('Kicks', 128),
          ('Snares', 129),
          ('Hi-hats', 130),
          ('Cymbals', 131),
          ('Toms', 132),
          ('Percussion', 133),
        ]],
        [hipPerc,
        [
          ('Kick', 152),
          ('Snare', 153),
          ('Rimshot', 158),
          ('Hi-hat', 154),
          ('Conga', 155),
          ('Cowbell', 156),
          ('Clap', 159),
          ('Shake', 157),
        ]],
      ]
      
      waveMap = {}
      for elm in waveforms:
        if type(elm) == list:
          cat, waves = elm
          for w, i in waves:
            if w == '-':
              cat.add_separator()
              continue
            cat.add_radiobutton(label=w, value=i, variable=f.sampledWave)
            waveMap[i] = w
        else:
          w, i = elm
          sampledWave.add_radiobutton(label=w, value=i, variable=f.sampledWave)
          waveMap[i] = w
          
      f.sampledWave.trace_add("write", lambda x, y, z, var=f.sampledWave, l=sampledWaveLabel, wm=waveMap:
        l.set(wm[var.get()]))
      f.sampledWave.trace_add("write", lambda x, y, z, var=f.sampledWave, v=v, sd=sd:
        sd.changeParameter(f'voice{v}.wave.sampledWave.waveName', var.get()))
      f.sampledWaveStart = f.sampledFrame.createSlider((3, 1), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.sampledWave.waveStartIndex', int(x)))
      f.sampledFrame.createSmallText((3, 2), 'Start')
      f.sampledWaveStartVelocityMod = f.sampledFrame.createSlider((3, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.sampledWave.waveVelocityStartMod', int(x)))
      f.sampledFrame.createSmallText((3, 4), 'Velocity Start Mod')
      sampledWaveLoopDirection, f.sampledWaveLoopDirection, sampledWaveLoopDirectionLabel = f.sampledFrame.createMenuButton((1, 3), sticky=S+E+W, width=18,
                                                                        command=lambda x, v=v: sd.changeParameter(f'voice{v}.wave.sampledWave.waveDirection', x))
      f.sampledFrame.createSmallText((1, 4), 'Wave Direction')
      f.sampledFrame.createMenuButtonOptions(sampledWaveLoopDirection, ['Forward', 'Reverse'], f.sampledWaveLoopDirection, sampledWaveLoopDirectionLabel)
      f.sampledFrame.createRGap(0, 5)
      f.sampledFrame.createCGap(0, 15)
      f.sampledFrame.createCGap(2, 10)
      f.sampledFrame.createCGap(4, 15)
      
      # MULTI-WAVE
      f.multiwaveLoopStart = f.multiwaveFrame.createSlider((3, 1), (0, 249), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.multiWave.loopWaveStart', int(x)))
      f.multiwaveFrame.createSmallText((3, 2), 'Loop Start')
      f.multiwaveLoopLength = f.multiwaveFrame.createSlider((3, 3), (1, 243), start = 243, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.multiWave.loopLength', int(x)))
      f.multiwaveFrame.createSmallText((3, 4), 'Loop Length')
      multiwaveLoopDirection, f.multiwaveLoopDirection, multiwaveLoopDirectionLabel = f.multiwaveFrame.createMenuButton((1, 1), sticky=S+E+W, width=16,
                                                                        command=lambda x, v=v: sd.changeParameter(f'voice{v}.wave.multiWave.loopDirection', x))
      f.multiwaveFrame.createSmallText((1, 2), 'Loop Direction')
      f.multiwaveFrame.createMenuButtonOptions(multiwaveLoopDirection, ['Forward', 'Reverse'], f.multiwaveLoopDirection, multiwaveLoopDirectionLabel)
      f.multiwaveFrame.createRGap(0, 5)
      f.multiwaveFrame.createCGap(0, 15)
      f.multiwaveFrame.createCGap(2, 10)
      f.multiwaveFrame.createCGap(4, 15)

      #GAP
      f.createCGap(2, 15)
    
      f.createRGap(3, 25)
      
      # VOICE
      f.voice = Application()
      f.voice.init(f.frame, darkGrey)
      f.voice.frame.grid(column = 1, row = 4, rowspan = 4)
      f.voice.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.resizableC(1)
      f.voice.resizableC(1)
      f.voice.createCGap(0, panelInnerGap)
      f.voice.createCGap(2, panelInnerGap)
      f.voice.createTitle((1, 0), 'Voice')
      f.voice.createRGap(1, 40)
      voicePreGain, f.voicePreGain, voicePreGainLabel = f.voice.createMenuButton((1, 1), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.preGain', x), width=selectorWidth)
      f.createMenuButtonOptions(voicePreGain, ['Off', 'On'], f.voicePreGain, voicePreGainLabel)
      f.voice.createSmallText((1, 2), 'Pre-Gain')
      f.voice.createRGap(2, 30)
      outputDestination, f.outputDestination, outputDestinationLabel = f.voice.createMenuButton((1, 3), value=1, sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.destination', x), width=selectorWidth)
      f.createMenuButtonOptions(outputDestination, ['Dry', 'FX 1', 'FX 2', 'AUX'], f.outputDestination, outputDestinationLabel)
      f.voice.createSmallText((1, 4), 'Destination')
      f.voice.createRGap(4, 30)
      voicePriority, f.voicePriority, voicePriorityLabel = f.voice.createMenuButton((1, 5), value=1, sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.priority', x), width=selectorWidth)
      f.createMenuButtonOptions(voicePriority, ['Low', 'Medium', 'High'], f.voicePriority, voicePriorityLabel)
      f.voice.createSmallText((1, 6), 'Priority')
      f.voice.createRGap(7, 10)
      glideMode, f.glideMode, glideModeLabel = f.voice.createMenuButton((1, 8), value=1, sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.pitchMod.glideMode', x), width=selectorWidth)
      f.createMenuButtonOptions(glideMode, ['None', 'Pedal', 'Mono', 'Legato', 'Trigger', 'Minimod'], f.glideMode, glideModeLabel)
      f.voice.createSmallText((1, 9), 'Glide Mode')
      f.velocityThreshold = f.voice.createSlider((1, 10), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.velocityThreshold', int(x)))
      f.voice.createSmallText((1, 11), 'Velocity Threshold')
      f.delay = f.voice.createSlider((1, 12), (0, 251), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.waveform.delayTime', int(x)))
      f.voice.createSmallText((1, 13), 'Delay')
      
      # PITCH
      f.createCGap(3, outerGap)
      f.pitch = Application()
      f.pitch.init(f.frame, darkGrey)
      f.pitch.frame.grid(column = 4, row = 4, rowspan=2)
      f.pitch.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.resizableC(4)
      f.pitch.resizableC(1)
      f.pitch.createCGap(0, panelInnerGap)
      f.pitch.createCGap(2, panelInnerGap)
      f.pitch.createTitle((1, 0), 'Pitch')
      f.octave = f.pitch.createSlider((1, 1), (-4, 4), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitch.octave', int(x)))
      f.pitch.createSmallText((1, 2), 'Octave')
      f.semitone = f.pitch.createSlider((1, 3), (-11, 11), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitch.semitone', int(x)))
      f.pitch.createSmallText((1, 4), 'Semitone')
      f.fineTune = f.pitch.createSlider((1, 5), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitch.fineTune', int(x)))
      f.pitch.createSmallText((1, 6), 'Fine')
      f.pitch.createRGap(7, 40)
      pitchTable, f.pitchTable, pitchTableLabel = f.pitch.createMenuButton((1, 7), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.pitch.pitchTable', x), width=selectorWidth)
      f.pitch.createMenuButtonOptions(pitchTable, ['System', 'All C4'], f.pitchTable, pitchTableLabel)
      f.pitch.createSmallText((1, 8), 'Pitch Table')
      
      f.createCGap(5, innerGap)
      
      # PITCH MOD 
      f.pitchMod = Application()
      f.pitchMod.init(f.frame, darkGrey)
      f.pitchMod.frame.grid(column = 6, row = 4, rowspan=2)
      f.pitchMod.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.pitchMod.createCGap(0, panelInnerGap)
      f.pitchMod.createCGap(2, panelInnerGap)
      f.pitchMod.createTitle((1, 0), 'Pitch Mod')
      f.pitchModAmount = f.pitchMod.createSlider((1, 1), (-99, 99), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitchMod.modAmount', int(x)))
      f.pitchModSource = f.pitchMod.createModSourceSelector((1, 2), sticky=N, command=lambda x, v=v: sd.changeParameter(f'voice{v}.pitchMod.modSource', x), width=33)
      f.pitchMod.createSmallText((1, 3), 'Mod')
      f.pitchEnv1ModAmount = f.pitchMod.createSlider((1, 4), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitchMod.env1ModAmount', int(x)))
      f.pitchMod.createSmallText((1, 5), 'Env. 1 Mod Amount')
      f.pitchLfoModAmount = f.pitchMod.createSlider((1, 6), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitchMod.lfoModAmount', int(x)))
      f.pitchMod.createSmallText((1, 7), 'LFO Mod Amount')
      f.createCGap(7, outerGap)
      
      # GAP
      f.createCGap(8, sectionGap)
      
      # FILTER 1
      f.createCGap(9, outerGap)
      f.filter1 = Application()
      f.filter1.init(f.frame, darkGrey)
      f.filter1.frame.grid(column = 10, row = 4, rowspan = 4)
      f.filter1.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.filter1.createCGap(0, panelInnerGap)
      f.filter1.createCGap(2, panelInnerGap)
      f.filter1.createTitle((1, 0), 'Filter 1')
      f.filter1.createRGap(1, 40)
      filter1Type, f.filter1Type, filter1TypeLabel = f.filter1.createMenuButton((1, 1), sticky=S, width=selectorWidth, disabled=True)
      f.filter1.createMenuButtonOptions(filter1Type, ['Low Pass 2', 'Low Pass 3', 'Low Pass 2', 'Low Pass 3'], f.filter1Type, filter1TypeLabel)
      f.filter1.createSmallText((1, 2), 'Type')
      f.filter1Cutoff = f.filter1.createSlider((1, 3), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter1.cutoff', int(x)))
      f.filter1.createSmallText((1, 4), 'Cutoff')
      f.filter1ModAmount = f.filter1.createSlider((1, 5), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter1.modAmount', int(x)))
      f.filter1ModSource = f.filter1.createModSourceSelector((1, 6), sticky=N+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.filters.filter1.modSource', x), width=33)
      f.filter1.createSmallText((1, 7), 'Mod')
      f.filter1Env2ModAmount = f.filter1.createSlider((1, 8), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter1.env2ModAmount', int(x)))
      f.filter1.createSmallText((1, 9), 'Env. 2 Mod Amount')
      f.filter1KeyboardTrack = f.filter1.createSlider((1, 10), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter1.keyboardTrack', int(x)))
      f.filter1.createSmallText((1, 11), 'Keyboard Track')
      f.filter1.createRGap(12, 10)
      
      f.createCGap(11, innerGap)
      
      # FILTER 2
      f.filter2 = Application()
      f.filter2.init(f.frame, darkGrey)
      f.filter2.frame.grid(column = 12, row = 4, rowspan = 4)
      f.filter2.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.filter2.createCGap(0, panelInnerGap)
      f.filter2.createCGap(2, panelInnerGap)
      f.filter2.createTitle((1, 0), 'Filter 2')
      f.filter2.createRGap(1, 40)
      filter2Type, f.filter2Type, filter2TypeLabel = f.filter2.createMenuButton((1, 1), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.filters.filter2.type', x), width=selectorWidth)
      f.filter2Type.trace_add("write", lambda x, y, z, f2=f.filter2Type, f1=f.filter1Type:
        f1.set(f2.get()))
      f.filter2.createMenuButtonOptions(filter2Type, ['High Pass 2', 'High Pass 1', 'Low Pass 2', 'Low Pass 1'], f.filter2Type, filter2TypeLabel)
      f.filter2.createSmallText((1, 2), 'Type')
      f.filter2Cutoff = f.filter2.createSlider((1, 3), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter2.cutoff', int(x)))
      f.filter2.createSmallText((1, 4), 'Cutoff')
      f.filter2ModAmount = f.filter2.createSlider((1, 5), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter2.modAmount', int(x)))
      f.filter2ModSource = f.filter2.createModSourceSelector((1, 6), sticky=N+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.filters.filter2.modSource', x), width=33)
      f.filter2.createSmallText((1, 7), 'Mod')
      f.filter2Env2ModAmount = f.filter2.createSlider((1, 8), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter2.env2ModAmount', int(x)))
      f.filter2.createSmallText((1, 9), 'Env. 2 Mod Amount')
      f.filter2KeyboardTrack = f.filter2.createSlider((1, 10), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter2.keyboardTrack', int(x)))
      f.filter2.createSmallText((1, 11), 'Keyboard Track')
      f.filter2.createRGap(12, 10)
      f.createCGap(13, outerGap)
      
      # GAP
      f.createCGap(14, sectionGap)
      
      # VOLUME
      f.createCGap(15, outerGap)
      f.volume = Application()
      f.volume.init(f.frame, darkGrey)
      f.volume.frame.grid(column = 16, row = 4)
      f.volume.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.volume.createCGap(0, panelInnerGap)
      f.volume.createCGap(2, panelInnerGap)
      f.volume.createTitle((1, 0), 'Volume')
      f.volumeS = f.volume.createSlider((1, 1), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.volume', int(x)))
      f.volume.createSmallText((1, 2), 'Volume')
      f.volumeModAmount = f.volume.createSlider((1, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.volumeModAmount', int(x)))
      f.volumeModSource = f.volume.createModSourceSelector((1, 4), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.volumeModSource', x), width=33)
      f.volume.createSmallText((1, 5), 'Mod')
      f.volumeKeyboardTrack = f.volume.createSlider((1, 6), (-128, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.keyboardScaleAmount', int(x)))
      f.volume.createSmallText((1, 7), 'Keyboard Track')
    
      f.createCGap(17, innerGap)
    
      # PAN
      f.pan = Application()
      f.pan.init(f.frame, darkGrey)
      f.pan.frame.grid(column = 18, row = 4)
      f.pan.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.pan.createCGap(0, panelInnerGap)
      f.pan.createCGap(2, panelInnerGap)
      f.pan.createTitle((1, 0), 'Pan', columnspan=2)
      f.panS = f.pan.createSlider((1, 1), (-64, 63), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.pan', int(x)+64))
      f.pan.createSmallText((1, 2), 'Pan')
      f.panModAmount = f.pan.createSlider((1, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.panModAmount', int(x)))
      f.panModSource = f.pan.createModSourceSelector((1, 4), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.panModSource', x), width=33)
      f.pan.createSmallText((1, 5), 'Mod')
      f.createCGap(19, outerGap)
      
      # LFO
      f.lfo = Application()
      f.lfo.init(f.frame, darkGrey)
      f.lfo.frame.grid(column = 16, row = 6, columnspan = 3, rowspan=2)
      f.lfo.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.lfo.createCGap(0, panelInnerGap)
      f.lfo.createCGap(6, panelInnerGap)
      f.lfo.createTitle((1, 0), 'LFO', columnspan=5)
      f.lfoRate = f.lfo.createSlider((1, 1), (0, 99), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.lfo.rate', int(x)))
      f.lfo.createSmallText((1, 2), 'Rate')
      f.lfoRateModAmount = f.lfo.createSlider((1, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.lfo.rateModAmount', int(x)))
      f.lfoRateModSource = f.lfo.createModSourceSelector((1, 4), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.lfo.rateModSource', x), width=25)
      f.lfo.createSmallText((1, 5), 'Rate Mod')
      f.lfo.createCGap(2, 10) #gap
      f.lfoDepth = f.lfo.createSlider((3, 1), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.lfo.depth', int(x)))
      f.lfo.createSmallText((3, 2), 'Depth')
      f.lfoDepthModSource = f.lfo.createModSourceSelector((3, 4), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.lfo.depthModSource', x), width=25)
      f.lfo.createSmallText((3, 5), 'Depth Mod')
      f.lfo.createCGap(4, 10) #gap
      f.lfoDelay = f.lfo.createSlider((5, 1), (0, 99), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.lfo.delay', int(x)))
      f.lfo.createSmallText((5, 2), 'Delay')
      f.lfoRestart = f.lfo.createToggleButton((5, 3), f'Restart', sticky=E+W+N, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.lfo.restart', x))
      lfoWave, f.lfoWave, lfoWaveLabel = f.lfo.createMenuButton((5, 4), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.lfo.waveshape', x), width=25)
      f.lfo.createMenuButtonOptions(lfoWave, ['Triangle', 'Sine', 'Sine/Tri', 'Pos/Sin', 'Pos/Tri', 'Saw', 'Square'], f.lfoWave, lfoWaveLabel)
      f.lfo.createSmallText((5, 5), 'Waveshape')
      
      # Mod Mixer
      f.mixer = Application()
      f.mixer.init(f.frame, darkGrey)
      f.mixer.frame.grid(column = 4, row = 7, columnspan = 3)
      f.mixer.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.mixer.createCGap(0, panelInnerGap)
      f.mixer.createCGap(6, panelInnerGap)
      f.mixer.createTitle((1, 0), 'Mod Mixer', columnspan=5)
      f.mixer.createRGap(1, 40)
      f.mixerSource1 = f.mixer.createModSourceSelector((1, 1), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.modMixer.modSource1', x), width=25)
      f.mixer.createSmallText((1, 2), 'Source 1')
      f.mixerSource2 = f.mixer.createModSourceSelector((1, 3), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.modMixer.modSource2', x), width=25)
      f.mixer.createSmallText((1, 4), 'Source 2')
      f.mixer.createCGap(2, 10) #gap
      mixerScaler, f.mixerScaler, mixerScalerLabel = f.mixer.createMenuButton((3, 1), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.modMixer.scaler', x), width=25)
      f.mixer.createMenuButtonOptions(mixerScaler, ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.5', '2.0', '3.0', '4.0', '6.0', '8.0'], f.mixerScaler, mixerScalerLabel)
      f.mixer.createSmallText((3, 2), 'Scaler')
      f.mixer.createCGap(4, 10) #gap
      mixerShape, f.mixerShape, mixerShapeLabel = f.mixer.createMenuButton((5, 1), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.modMixer.shape', x), width=25)
      f.mixer.createMenuButtonOptions(mixerShape, ['Quick Rise', 'Convex 1', 'Convex 2', 'Convex 3', 'Linear', 'Concave 1', 'Concave 2', 'Concave 3', 'Concave 4', 'Late Rise', 'Quantize 32', 'Quantize 16', 'Quantize 8', 'Quantize 4', 'Quantize 2', 'Smoother'], f.mixerShape, mixerShapeLabel)
      f.mixer.createSmallText((5, 2), 'Shape')
      f.noiseSourceRate = f.mixer.createSlider((3, 3), (0, 127), start = 0,  columnspan=3, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.lfo.noiseSourceRate', int(x)))
      f.mixer.createSmallText((3, 4), 'Noise Source Rate',  columnspan=3)
    
     
      # ENVELOPES
      def envelopeContextMenu(event, menu):
        try:
          menu.tk_popup(event.x_root, event.y_root)
        finally:
          menu.grab_release()
      
      f.envs = []
      f.envVars = []
      f.envModes = []
      f.envExtras = []
      f.envContexts = []
      envColSpan = 5
      c = 3
      r = 0
      for e in range(3):
        #f.createTitle((c, r), f'Envelope {e+1}', columnspan=env1ColumnSpan)
        env = f.createCanvas((c, r+1), size=(500,100), columnspan=envColSpan)
        envVars = [[0, 127, 100, 127, 50], [5, 99, 25, 50, 20]]
        envContext = tk.Menu(f.frame, tearoff=0)
        f.envs.append(env)
        f.envVars.append(envVars)
        f.envContexts.append(envContext)
        envMode = tk.IntVar(0)
        envMode.trace_add("write", lambda x, y, z, v=v, e=e, var=envMode, sd=sd: sd.changeParameter(f'voice{v}.envelopes.env{e}.mode', var.get()))
        f.envModes.append(envMode)
        envContext.add_radiobutton(label='Normal', variable=envMode, value=0)
        envContext.add_radiobutton(label='Finish', variable=envMode, value=1)
        envContext.add_radiobutton(label='Loop', variable=envMode, value=2)
        envContext.add_separator()
        envContext.add_command(label='Copy', command=lambda voice=v, gui=self, e=e: gui.copyEnvelope(voice, e))
        envContext.add_command(label='Paste', state=tk.DISABLED, command=lambda voice=v, gui=self, e=e: gui.pasteEnvelope(voice, e))
        env.bind("<Button-3>", lambda event, menu=envContext: envelopeContextMenu(event, menu))
        
        envParams = Application()
        envParams.init(f.frame, darkGrey)
        envParams.frame.grid(column = c, row = r+2, columnspan = envColSpan)
        envParams.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
        envParams.createCGap(0, 3)
        envExtras = []
        envExtras.append(
          envParams.createSlider((1, 0), (0, 127), start = 0, sticky = W+E+N, command=lambda x, v=v, e=e, sd=sd:sd.changeParameter(f'voice{v}.envelopes.env{e}.attackTimeVelocitySens', int(x))))
        envParams.createSmallText((1, 1), 'Atk. Vel. Sens.')
        envParams.resizableC(1)
        envParams.createCGap(2, 3)
        envExtras.append(
          envParams.createSlider((3, 0), (0, 127), start = 0, sticky = W+E+N, command=lambda x, v=v, e=e, sd=sd:sd.changeParameter(f'voice{v}.envelopes.env{e}.levelVelocitySens', int(x))))
        envParams.createSmallText((3, 1), 'Lvl. Vel. Sens.')
        envParams.resizableC(3)
        envParams.createCGap(4, 3)
        envExtras.append(
          envParams.createSlider((5, 0), (0, 9), start = 0, sticky = W+E+N, command=lambda x, v=v, e=e, sd=sd:sd.changeParameter(f'voice{v}.envelopes.env{e}.velocityCurve', int(x))))
        envParams.createSmallText((5, 1), 'Vel. Curve')
        envParams.resizableC(5)
        envParams.createCGap(6, 3)
        envExtras.append(
          envParams.createSlider((7, 0), (-127, 127), start = 0, sticky = W+E+N, command=lambda x, v=v, e=e, sd=sd:sd.changeParameter(f'voice{v}.envelopes.env{e}.keyboardTrack', int(x))))
        envParams.createSmallText((7, 1), 'Kbd. Track')
        envParams.resizableC(7)
        envParams.createCGap(8, 3)
        
        f.envExtras.append(envExtras)
        
        for i in range(6): 
          line = env.create_line(0, 0, 0, 0, tags=(f'line{i}'))
          
          rect = env.create_rectangle(0, 0, 0, 0, tags=(f'step{i}'))
          env.tag_bind(rect, '<B1-Motion>', lambda event, voice=v, step=i, e=e, gui=self: gui.envDrag(event, voice, e, step))
          env.tag_bind(rect, '<ButtonRelease-1>', lambda event, voice=v, step=i, e=e, gui=self: gui.emitEnv(event, voice, e, step))
          
          env.create_text(0, 0, tags=(f'duration{i}'), fill = '#ffffff')
      
        #GAP
        c += envColSpan + 1
      
      
      f.createCGap(c, 15)
    
  def loadParameters(self, params):
    self.programName.set(params['program']['name'])
    
    self.glideTime.set(params['programControl']['glideTime'])
    self.bendRange.set(params['programControl']['bendRange'])
    self.restrikeDelay.set(params['programControl']['restrikeDelay'])
    self.delayMultiplier.set(params['programControl']['delayMultiplier'])
    
    for v, voice in enumerate(self.voices):
      self.voiceStatus[v].set(params['selectVoice'][f'voice{v}Status'])
      
      voice.octave.set(params[f'voice{v}']['pitch']['octave'])
      voice.semitone.set(params[f'voice{v}']['pitch']['semitone'])
      voice.fineTune.set(params[f'voice{v}']['pitch']['fineTune'])
      voice.pitchTable.set(params[f'voice{v}']['pitch']['pitchTable'])
      voice.pitchEnv1ModAmount.set(params[f'voice{v}']['pitchMod']['env1ModAmount'])
      voice.pitchLfoModAmount.set(params[f'voice{v}']['pitchMod']['lfoModAmount'])
      voice.pitchModSource.set(params[f'voice{v}']['pitchMod']['modSource'])
      voice.pitchModAmount.set(params[f'voice{v}']['pitchMod']['modAmount'])
      
      #voice.filter1Type.set(params[f'voice{v}']['filters']['filter1']['type'])
      voice.filter1Cutoff.set(params[f'voice{v}']['filters']['filter1']['cutoff'])
      voice.filter1ModAmount.set(params[f'voice{v}']['filters']['filter1']['modAmount'])
      voice.filter1ModSource.set(params[f'voice{v}']['filters']['filter1']['modSource'])
      voice.filter1Env2ModAmount.set(params[f'voice{v}']['filters']['filter1']['env2ModAmount'])
      voice.filter1KeyboardTrack.set(params[f'voice{v}']['filters']['filter1']['keyboardTrack'])
      voice.filter2Type.set(params[f'voice{v}']['filters']['filter2']['type'])
      voice.filter2Cutoff.set(params[f'voice{v}']['filters']['filter2']['cutoff'])
      voice.filter2ModAmount.set(params[f'voice{v}']['filters']['filter2']['modAmount'])
      voice.filter2ModSource.set(params[f'voice{v}']['filters']['filter2']['modSource'])
      voice.filter2Env2ModAmount.set(params[f'voice{v}']['filters']['filter2']['env2ModAmount'])
      voice.filter2KeyboardTrack.set(params[f'voice{v}']['filters']['filter2']['keyboardTrack'])
      
      voice.volumeS.set(params[f'voice{v}']['output']['volume'])
      voice.volumeModAmount.set(params[f'voice{v}']['output']['volumeModAmount'])
      voice.volumeModSource.set(params[f'voice{v}']['output']['volumeModSource'])
      voice.volumeKeyboardTrack.set(params[f'voice{v}']['output']['keyboardScaleAmount'])
      
      voice.panS.set(params[f'voice{v}']['output']['pan'] - 64)
      voice.panModAmount.set(params[f'voice{v}']['output']['panModAmount'])
      voice.panModSource.set(params[f'voice{v}']['output']['panModSource'])
      
      voice.voicePreGain.set(params[f'voice{v}']['output']['preGain'])
      voice.outputDestination.set(params[f'voice{v}']['output']['destination'])
      voice.voicePriority.set(params[f'voice{v}']['output']['priority'])
      voice.velocityThreshold.set(params[f'voice{v}']['output']['velocityThreshold'])
      voice.glideMode.set(params[f'voice{v}']['pitchMod']['glideMode'])
      
      voice.mixerSource1.set(params[f'voice{v}']['modMixer']['modSource1'])
      voice.mixerSource2.set(params[f'voice{v}']['modMixer']['modSource2'])
      voice.mixerShape.set(params[f'voice{v}']['modMixer']['shape'])
      voice.mixerScaler.set(params[f'voice{v}']['modMixer']['scaler'])
      
      voice.lfoRate.set(params[f'voice{v}']['lfo']['rate'])
      voice.lfoRateModAmount.set(params[f'voice{v}']['lfo']['rateModAmount'])
      voice.lfoRateModSource.set(params[f'voice{v}']['lfo']['rateModSource'])
      voice.lfoDepth.set(params[f'voice{v}']['lfo']['depth'])
      voice.lfoDepthModSource.set(params[f'voice{v}']['lfo']['depthModSource'])
      voice.lfoDelay.set(params[f'voice{v}']['lfo']['delay'])
      voice.lfoWave.set(params[f'voice{v}']['lfo']['waveshape'])
      voice.lfoRestart.set(params[f'voice{v}']['lfo']['restart'])
      voice.noiseSourceRate.set(params[f'voice{v}']['lfo']['noiseSourceRate'])
      
      voice.waveformWave.set(params[f'voice{v}']['wave']['waveform']['waveName'])
      
      voice.transwaveWave.set(params[f'voice{v}']['wave']['transwave']['waveName'])
      voice.transwaveStart.set(params[f'voice{v}']['wave']['transwave']['waveStart'])
      voice.transwaveModAmount.set(params[f'voice{v}']['wave']['transwave']['waveModAmount'])
      voice.transwaveModSource.set(params[f'voice{v}']['wave']['transwave']['waveModSource'])
      
      voice.sampledWave.set(params[f'voice{v}']['wave']['sampledWave']['waveName'])
      voice.sampledWaveStart.set(params[f'voice{v}']['wave']['sampledWave']['waveStartIndex'])
      voice.sampledWaveStartVelocityMod.set(params[f'voice{v}']['wave']['sampledWave']['waveVelocityStartMod'])
      voice.sampledWaveLoopDirection.set(params[f'voice{v}']['wave']['sampledWave']['waveDirection'])
      
      voice.multiwaveLoopStart.set(params[f'voice{v}']['wave']['multiWave']['loopWaveStart'])
      voice.multiwaveLoopLength.set(params[f'voice{v}']['wave']['multiWave']['loopLength'])
      voice.multiwaveLoopDirection.set(params[f'voice{v}']['wave']['multiWave']['loopDirection'])
      
      t = params[f'voice{v}']['wave']['type']
      voice.delay.set(params[f'voice{v}']['wave'][('waveform', 'transwave', 'sampledWave', 'multiWave')[t]]['delayTime'])
      
      waveType = params[f'voice{v}']['wave']['type']
      voice.waveTabs.select([voice.waveformTab, voice.transwaveTab, voice.sampledTab, voice.multiwaveTab][waveType])
    
      for e in range(3):
        voice.envVars[e] = [
          [
            params[f'voice{v}']['envelopes'][f'env{e}']['initialLevel'],
            params[f'voice{v}']['envelopes'][f'env{e}']['peakLevel'],
            params[f'voice{v}']['envelopes'][f'env{e}']['breakpoint1Level'],
            params[f'voice{v}']['envelopes'][f'env{e}']['breakpoint2Level'],
            params[f'voice{v}']['envelopes'][f'env{e}']['sustainLevel']
          ],
          [
            params[f'voice{v}']['envelopes'][f'env{e}']['attackTime'],
            params[f'voice{v}']['envelopes'][f'env{e}']['decay1Time'],
            params[f'voice{v}']['envelopes'][f'env{e}']['decay2Time'],
            params[f'voice{v}']['envelopes'][f'env{e}']['decay3Time'],
            params[f'voice{v}']['envelopes'][f'env{e}']['releaseTime']
          ]
        ]
        voice.envModes[e].set(params[f'voice{v}']['envelopes'][f'env{e}']['mode'])
        voice.envExtras[e][0].set(params[f'voice{v}']['envelopes'][f'env{e}']['attackTimeVelocitySens'])
        voice.envExtras[e][1].set(params[f'voice{v}']['envelopes'][f'env{e}']['levelVelocitySens'])
        voice.envExtras[e][2].set(params[f'voice{v}']['envelopes'][f'env{e}']['velocityCurve'])
        voice.envExtras[e][3].set(params[f'voice{v}']['envelopes'][f'env{e}']['keyboardTrack'])
    
    





# waveforms = [
#   [string,
#   [
#     ('strings', 0),
#     ('Pizz-Str', 1),
#     ('grand-pno', 2),
#     ('piano.var', 3),
#     ('digipiano', 4),
#     ('clavpiano', 5),
#     ('acous-gtr', 6),
#     ('guit.var1', 7),
#     ('guit.var2', 8),
#     ('gtr-harmo', 9),
#     ('el-guitar', 10),
#     ('pluck-gtr', 11),
#     ('chukka-gtr', 12),
#     ('crunch-gt', 13),
#     ('crunch-lp', 14),
#   ]],
#   [brass,
#   [
#     ('uni-brass', 15),
#     ('trumpet', 16),
#     ('trump.var', 17),
#     ('frenchhorn', 18),
#     ('fhorn.var', 19),
#     ('saxophone', 20),
#     ('sax.var-1', 21),
#     ('sax.var-2', 22),
#   ]],
#   [bass,
#   [
#     ('pick-bass', 23),
#     ('pop-bass', 24),
#     ('pluckbass', 25),
#     ('doublbass', 26),
#     ('synbass-1', 27),
#     ('synbass-2', 28),
#   ]],
#   [breath,
#   [
#     ('woodflute', 29),
#     ('chifflute', 30),
#     ('ocarina', 31),
#     ('vox-ooohs', 32),
#     ('vocal-pad', 33),
#   ]],
#   [tunedPerc,
#   [
#     ('marimba', 34),
#     ('kalimba', 35),
#     ('steeldrum', 36),
#     ('doorbell', 37),
#     ('potlid-ht', 38),
#     ('syn-pluck', 39),
#     ('plinkhorn', 40),
#     ('flutedrum', 41),
#     ('pno-ping', 42),
#     ('orch-hit', 43),
#     ('kagong', 44),
#     ('rack-bell', 45),
#     ('crash-cym', 46),
#   ]],
#   [perc,
#   [
#     ('woody-hit', 47),
#     ('woodblock', 48),
#     ('templ-blk', 49),
#     ('dinky-hit', 50),
#     ('toyhammer', 51),
#     ('agogo-bel', 52),
#     ('slinkypop', 53),
#     ('duct-tape', 54),
#     ('steamdrum', 55),
#     ('big-blast', 56),
#     ('spray-can', 57),
#     ('metaldink', 58),
#     ('vocalperc', 59),
#     ('anvil-hit', 60),
#     ('kick-drum', 61),
#     ('snaredrum', 62),
#   ]],
#   [drum,
#   [
#     ('gate-kick', 109),
#     ('room-kick', 110),
#     ('gate-snare', 111),
#     ('rim-snare', 112),
#     ('close-hat', 113),
#     ('open-hat', 114),
#     ('ride-cymb', 115),
#     ('dry-tom-l', 116),
#     ('dry-tom-h', 117),
#     ('gat-tom-l', 118),
#     ('gat-tom-h', 119),
#     ('rim-tom-l', 120),
#     ('rim-tom-h', 121),
#     ('timbale', 122),
#     ('congo-lo', 123),
#     ('congo-hi', 124),
#     ('tamborine', 125),
#   ]],
#   [multiDrum,
#   [
#     ('all-perc', 126),
#     ('all-drums', 127),
#     ('kick-drms', 128),
#     ('snar-drms', 129),
#     ('hi-hats', 130),
#     ('cymbals', 131),
#     ('tom-toms', 132),
#     ('percussion', 133),
#     ('dry-toms', 134),
#     ('room-toms', 135),
#     ('gate-toms', 136),
#     ('congas', 137),
#     ('std-kit', 138),
#     ('gated-kit', 139),
#     ('room-kit', 140),
#   ]],
#   [piano,
#   [
#     ('piano-16', 141),
#     ('pno16.var', 142),
#     ('pno-noise', 143),
#     ('pno16-hi', 144),
#     ('sympathic', 145),
#     ('epno-soft', 146),
#     ('epno-hard', 147),
#     ('pno16-lo', 148),
#     ('pno-thump', 149),
#   ]],
#   [hipPerc,
#   [
#     ('pic-snare', 150),
#     ('shaker', 151),
#     ('hip.kick', 152),
#     ('hip.snare', 153),
#     ('hip.hihat', 154),
#     ('hip.conga', 155),
#     ('hip.cowbl', 156),
#     ('hip.shake', 157),
#     ('hip.rimsh', 158),
#     ('hip.claps', 159),
#     ('hip.kit-1', 160),
#   ]],
#   [misc,
#   [
#     ('vibes', 161),
#     ('tympani', 162),
#     ('violin', 163),
#     ('violin.var', 164),
#     ('slap-bass', 165),
#     ('synbass-3', 166),
#   ]],
#   ('drum-map', 167),
# ]