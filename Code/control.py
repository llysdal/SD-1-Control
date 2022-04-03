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
    self.numberfont = ('Lucida Sans', 8)
    
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

  def createMenuButton(self, gridpos, sticky = E+S, columnspan=1, width=10, value=0, command=None):    
    labelVar = tk.StringVar(value='default')
    var = tk.IntVar(value=value)
    
    menubutton = ttk.Menubutton(self.frame, textvariable=labelVar, width=width)
    menu = tk.Menu(menubutton, tearoff=0, borderwidth=0, activeborderwidth=0)
    menubutton['menu'] = menu
    menubutton.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)
    
    if command:
      var.trace_add("write", lambda x, y, z, var=var: command(var.get()))

    return menu, var, labelVar
  
  def createMenuButtonOption(self, menubutton, label, value, variable, labelvariable):
    menubutton.add_radiobutton(label=label, value=value, variable=variable, command=lambda l=labelvariable, label=label: l.set(label))
  
  def createModSourceSelector(self, gridpos, sticky = E+S, command=None, width=17):
    menu, var, label = self.createMenuButton(gridpos, sticky=sticky, width=width)
    var.set(15)
    menu.add_radiobutton(label='*OFF*', value=15, variable=var, command=lambda l=label: l.set('*OFF*'))
    menu.add_radiobutton(label='LFO', value=0, variable=var, command=lambda l=label: l.set('LFO'))
    menu.add_radiobutton(label='Noise', value=3, variable=var, command=lambda l=label: l.set('Noise'))
    menu.add_radiobutton(label='Envelope 1', value=1, variable=var, command=lambda l=label: l.set('Envelope 1'))
    menu.add_radiobutton(label='Envelope 2', value=2, variable=var, command=lambda l=label: l.set('Envelope 2'))
    menu.add_radiobutton(label='Mixer', value=4, variable=var, command=lambda l=label: l.set('Mixer'))
    menu.add_radiobutton(label='Pitch', value=9, variable=var, command=lambda l=label: l.set('Pitch'))
    keyb = tk.Menu(menu, tearoff=0)
    keyb.add_radiobutton(label='Velocity', value=5, variable=var, command=lambda l=label: l.set('Velocity'))
    keyb.add_radiobutton(label='Pressure', value=14, variable=var, command=lambda l=label: l.set('Pressure'))
    keyb.add_radiobutton(label='Pressure + Velocity', value=11, variable=var, command=lambda l=label: l.set('Pressure + Velocity'))
    keyb.add_radiobutton(label='Pedal', value=8, variable=var, command=lambda l=label: l.set('Pedal') )
    keyb.add_radiobutton(label='Wheel', value=13, variable=var, command=lambda l=label: l.set('Wheel'))
    keyb.add_radiobutton(label='Wheel + Pressure', value=12, variable=var, command=lambda l=label: l.set('Wheel + Pressure'))
    keyb.add_radiobutton(label='Timbre', value=7, variable=var, command=lambda l=label: l.set('Timbre'))
    keyb.add_radiobutton(label='Keyboard', value=6, variable=var, command=lambda l=label: l.set('Keyboard'))
    menu.add_cascade(label='Keyboard', menu=keyb)
    menu.add_radiobutton(label='X-Ctrl', value=10, variable=var, command=lambda l=label: l.set('X-Ctrl'))
    label.set('*OFF*')
    
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
            env.itemconfigure(durText, text=f'{envTimes[duration]}s')
          
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

  def onWaveClassChange(self, voice, t):
    v = self.voices[voice]
    #print(voice, t)

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
    self.menu.add_cascade(label='Programs', menu=programmenu)
    
    self.menu.add_command(label="\u22EE", activebackground=self.menu.cget("background"), state=tk.DISABLED)
    
    optionmenu = tk.Menu(self.menu, tearoff=0)
    self.menu.add_cascade(label='Options', menu=optionmenu)

    self.createRGap(0, 5)
    mainTabs = self.createTabs((0,1))
    masterFrame, masterTab = self.createTab(mainTabs, 'Master')
    midiFrame, midiTab = self.createTab(mainTabs, 'MIDI')
    programcontrolFrame, programcontrolTab = self.createTab(mainTabs, 'Program Control')
    voicesFrame, voicesTab = self.createTab(mainTabs, 'Voices')
    mainTabs.select(voicesTab)

    voicesFrame.createRGap(0, 5)
    voiceTabs = voicesFrame.createTabs((0,1))
    voice0Frame, voice0Tab = voicesFrame.createTab(voiceTabs, 'Voice 1')
    voice1Frame, voice1Tab = voicesFrame.createTab(voiceTabs, 'Voice 2')
    voice2Frame, voice2Tab = voicesFrame.createTab(voiceTabs, 'Voice 3')
    voice3Frame, voice3Tab = voicesFrame.createTab(voiceTabs, 'Voice 4')
    voice4Frame, voice4Tab = voicesFrame.createTab(voiceTabs, 'Voice 5')
    voice5Frame, voice5Tab = voicesFrame.createTab(voiceTabs, 'Voice 6')
    
    self.envelopeCopy = None
    
    self.voices = [voice0Frame, voice1Frame, voice2Frame, voice3Frame, voice4Frame, voice5Frame]
    for v in range(6):
      f = self.voices[v]

      f.createCGap(0, 10)
      f.createRGap(0, 10)
      f.createRGap(100, 10)
      
      #f.createTitle((c, r), 'Wave', columnspan=2)
      f.waveType = 0
      waveTabs = f.createTabs((1,1), rowspan=2, command=lambda x, gui=self, v=v: gui.onWaveClassChange(v, x))
      f.waveformFrame, waveformTab = f.createTab(waveTabs, 'Waveform')
      f.transwaveFrame, transwaveTab = f.createTab(waveTabs, 'Transwave')
      f.sampledFrame, sampledTab = f.createTab(waveTabs, 'Sampled')
      f.multiwaveFrame, multiwaveTab = f.createTab(waveTabs, 'Multiwave')
      
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
      for elm in waveforms:
        if type(elm) == list:
          cat, waves = elm
          for w, i in waves:
            cat.add_radiobutton(label=w, value=i, variable=f.waveformWave, command=lambda l=waveformWaveLabel, w=w: l.set(w))
        else:
          w, i = elm
          waveformWave.add_radiobutton(label=w, value=i, variable=f.waveformWave, command=lambda l=waveformWaveLabel, w=w: l.set(w))
      f.waveformWave.set(84)
      waveformWaveLabel.set('Sawtooth')
      f.waveformWave.trace_add("write", lambda x, y, z, var=f.waveformWave, v=v, sd=sd:(
        sd.changeParameter(f'voice{v}.wave.waveform.waveform', var.get())))
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
      for w, i in waveforms:
        transwaveWave.add_radiobutton(label=w, value=i, variable=f.transwaveWave, command=lambda l=transwaveWaveLabel, w=w: l.set(w))
      f.transwaveWave.set(63)
      transwaveWaveLabel.set('Spectral')
      f.transwaveWave.trace_add("write", lambda x, y, z, var=f.transwaveWave, v=v, sd=sd:(
        sd.changeParameter(f'voice{v}.wave.transwave.waveform', var.get())))
      f.transwaveFrame.createSlider((3, 1), (0, 99), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.transwave.waveStart', int(x)))
      f.transwaveFrame.createSmallText((3, 2), 'Start')
      f.transwaveFrame.createSlider((3, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.transwave.waveModAmount', int(x)))
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
          ('uni-brass', 15),
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
      
      for elm in waveforms:
        if type(elm) == list:
          cat, waves = elm
          for w, i in waves:
            if w == '-':
              cat.add_separator()
              continue
            cat.add_radiobutton(label=w, value=i, variable=f.sampledWave, command=lambda l=sampledWaveLabel, w=w: l.set(w))
        else:
          w, i = elm
          sampledWave.add_radiobutton(label=w, value=i, variable=f.sampledWave, command=lambda l=sampledWaveLabel, w=w: l.set(w))
      f.sampledWave.set(0)
      sampledWaveLabel.set('Strings')
      f.sampledWave.trace_add("write", lambda x, y, z, var=f.sampledWave, v=v, sd=sd:(
        sd.changeParameter(f'voice{v}.wave.sampledWave.waveform', var.get())))
      f.sampledFrame.createSlider((3, 1), (0, 249), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.sampledWave.waveStartIndex', int(x)))
      f.sampledFrame.createSmallText((3, 2), 'Start')
      f.sampledFrame.createSlider((3, 3), (1, 243), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.sampledWave.waveVelocityStartMod', int(x)))
      f.sampledFrame.createSmallText((3, 4), 'Velocity Start Mod')
      sampledWaveLoopDirection, f.sampledWaveLoopDirection, sampledWaveLoopDirectionLabel = f.sampledFrame.createMenuButton((1, 3), sticky=S+E+W, width=18,
                                                                        command=lambda x, v=v: sd.changeParameter(f'voice{v}.wave.sampledWave.waveDirection', x))
      f.sampledFrame.createSmallText((1, 4), 'Wave Direction')
      f.sampledFrame.createMenuButtonOption(sampledWaveLoopDirection, 'Forward', 0, f.sampledWaveLoopDirection, sampledWaveLoopDirectionLabel)
      f.sampledFrame.createMenuButtonOption(sampledWaveLoopDirection, 'Reverse', 1, f.sampledWaveLoopDirection, sampledWaveLoopDirectionLabel)
      sampledWaveLoopDirectionLabel.set('Forward')
      f.sampledFrame.createRGap(0, 5)
      f.sampledFrame.createCGap(0, 15)
      f.sampledFrame.createCGap(2, 10)
      f.sampledFrame.createCGap(4, 15)
      
      # MULTI-WAVE
      f.multiwaveFrame.createSlider((3, 1), (0, 249), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.multiWave.loopWaveStart', int(x)))
      f.multiwaveFrame.createSmallText((3, 2), 'Loop Start')
      f.multiwaveFrame.createSlider((3, 3), (1, 243), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.multiWave.loopLength', int(x)))
      f.multiwaveFrame.createSmallText((3, 4), 'Loop Length')
      multiwaveLoopDirection, f.multiwaveLoopDirection, multiwaveLoopDirectionLabel = f.multiwaveFrame.createMenuButton((1, 1), sticky=S+E+W, width=16,
                                                                        command=lambda x, v=v: sd.changeParameter(f'voice{v}.wave.multiWave.loopDirection', x))
      f.multiwaveFrame.createSmallText((1, 2), 'Loop Direction')
      f.multiwaveFrame.createMenuButtonOption(multiwaveLoopDirection, 'Forward', 0, f.multiwaveLoopDirection, multiwaveLoopDirectionLabel)
      f.multiwaveFrame.createMenuButtonOption(multiwaveLoopDirection, 'Reverse', 1, f.multiwaveLoopDirection, multiwaveLoopDirectionLabel)
      multiwaveLoopDirectionLabel.set('Forward')
      f.multiwaveFrame.createRGap(0, 5)
      f.multiwaveFrame.createCGap(0, 15)
      f.multiwaveFrame.createCGap(2, 10)
      f.multiwaveFrame.createCGap(4, 15)

      #GAP
      f.createCGap(2, 15)
    
      f.createRGap(3, 25)
      
      sectionGap = 40
      innerGap = 30
      outerGap = 0
      panelInnerGap = 15
      
      # VOICE
      f.voice = Application()
      f.voice.init(f.frame, darkGrey)
      f.voice.frame.grid(column = 1, row = 4)
      f.voice.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.resizableC(1)
      f.voice.resizableC(1)
      f.voice.createCGap(0, panelInnerGap)
      f.voice.createCGap(2, panelInnerGap)
      f.voice.createTitle((1, 0), 'Voice')
      f.voice.createRGap(1, 40)
      voicePreGain, f.voicePreGain, voicePreGainLabel = f.voice.createMenuButton((1, 1), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.preGain', x), width=15)
      f.createMenuButtonOption(voicePreGain, 'Off', 0, f.voicePreGain, voicePreGainLabel)
      f.createMenuButtonOption(voicePreGain, 'On', 1, f.voicePreGain, voicePreGainLabel)
      voicePreGainLabel.set('Off')
      f.voice.createSmallText((1, 2), 'Pre-Gain')
      f.voice.createRGap(2, 36)
      outputDestination, f.outputDestination, outputDestinationLabel = f.voice.createMenuButton((1, 3), value=1, sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.destination', x), width=15)
      f.createMenuButtonOption(outputDestination, 'Dry', 0, f.outputDestination, outputDestinationLabel)
      f.createMenuButtonOption(outputDestination, 'FX 1', 1, f.outputDestination, outputDestinationLabel)
      f.createMenuButtonOption(outputDestination, 'FX 2', 2, f.outputDestination, outputDestinationLabel)
      f.createMenuButtonOption(outputDestination, 'AUX', 3, f.outputDestination, outputDestinationLabel)
      outputDestinationLabel.set('FX 1')
      f.voice.createSmallText((1, 4), 'Destination')
      f.voice.createRGap(4, 36)
      voicePriority, f.voicePriority, voicePriorityLabel = f.voice.createMenuButton((1, 5), value=1, sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.priority', x), width=15)
      f.createMenuButtonOption(voicePriority, 'Low', 0, f.voicePriority, voicePriorityLabel)
      f.createMenuButtonOption(voicePriority, 'Medium', 1, f.voicePriority, voicePriorityLabel)
      f.createMenuButtonOption(voicePriority, 'High', 2, f.voicePriority, voicePriorityLabel)
      voicePriorityLabel.set('Medium')
      f.voice.createSmallText((1, 6), 'Priority')
      f.voice.createSlider((1, 7), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.velocityThreshold', int(x)))
      f.voice.createSmallText((1, 8), 'Velocity Threshold')
      f.voice.createSlider((1, 9), (0, 251), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.wave.waveform.delayTime', int(x)))
      f.voice.createSmallText((1, 10), 'Delay')
      
      # PITCH
      f.createCGap(3, outerGap)
      f.pitch = Application()
      f.pitch.init(f.frame, darkGrey)
      f.pitch.frame.grid(column = 4, row = 4)
      f.pitch.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.resizableC(4)
      f.pitch.resizableC(1)
      f.pitch.createCGap(0, panelInnerGap)
      f.pitch.createCGap(2, panelInnerGap)
      f.pitch.createTitle((1, 0), 'Pitch')
      f.pitch.createSlider((1, 1), (-4, 4), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitch.octave', int(x)))
      f.pitch.createSmallText((1, 2), 'Octave')
      f.pitch.createSlider((1, 3), (-11, 11), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitch.semitone', int(x)))
      f.pitch.createSmallText((1, 4), 'Semitone')
      f.pitch.createSlider((1, 5), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitch.fineTune', int(x)))
      f.pitch.createSmallText((1, 6), 'Fine')
      f.pitch.createRGap(7, 40)
      pitchTable, f.pitchTable, pitchTableLabel = f.pitch.createMenuButton((1, 7), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.pitch.pitchTable', x), width=15)
      f.pitch.createMenuButtonOption(pitchTable, 'System', 0, f.pitchTable, pitchTableLabel)
      f.pitch.createMenuButtonOption(pitchTable, 'All C4', 1, f.pitchTable, pitchTableLabel)
      pitchTableLabel.set('System')
      f.pitch.createSmallText((1, 8), 'Pitch Table')
      
      f.createCGap(5, innerGap)
      
      # PITCH MOD 
      f.pitchMod = Application()
      f.pitchMod.init(f.frame, darkGrey)
      f.pitchMod.frame.grid(column = 6, row = 4)
      f.pitchMod.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.pitchMod.createCGap(0, panelInnerGap)
      f.pitchMod.createCGap(2, panelInnerGap)
      f.pitchMod.createTitle((1, 0), 'Pitch Mod')
      f.pitchMod.createSlider((1, 1), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitchMod.modAmount', int(x)))
      f.transwaveModSource = f.pitchMod.createModSourceSelector((1, 2), sticky=N, command=lambda x, v=v: sd.changeParameter(f'voice{v}.pitchMod.modSource', x), width=33)
      f.pitchMod.createSmallText((1, 3), 'Mod')
      f.pitchMod.createSlider((1, 4), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitchMod.env1ModAmount', int(x)))
      f.pitchMod.createSmallText((1, 5), 'Env. 1 Mod Amount')
      f.pitchMod.createSlider((1, 6), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.pitchMod.lfoModAmount', int(x)))
      f.pitchMod.createSmallText((1, 7), 'LFO Mod Amount')
      f.createCGap(7, outerGap)
      
      # GAP
      f.createCGap(8, sectionGap)
      
      # FILTER 1
      f.createCGap(9, outerGap)
      f.filter1 = Application()
      f.filter1.init(f.frame, darkGrey)
      f.filter1.frame.grid(column = 10, row = 4)
      f.filter1.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.filter1.createCGap(0, panelInnerGap)
      f.filter1.createCGap(2, panelInnerGap)
      f.filter1.createTitle((1, 0), 'Filter 1')
      f.filter1.createRGap(1, 40)
      filter1Type, f.filter1Type, filter1TypeLabel = f.filter1.createMenuButton((1, 1), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.filters.filter1.type', x), width=15)
      f.filter1.createMenuButtonOption(filter1Type, 'Low Pass 2', 0, f.filter1Type, filter1TypeLabel)
      f.filter1.createMenuButtonOption(filter1Type, 'Low Pass 3', 1, f.filter1Type, filter1TypeLabel)
      filter1TypeLabel.set('Low Pass 2')
      f.filter1.createSmallText((1, 2), 'Type')
      f.filter1.createSlider((1, 3), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter1.cutoff', int(x)))
      f.filter1.createSmallText((1, 4), 'Cutoff')
      f.filter1.createSlider((1, 5), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter1.modAmount', int(x)))
      f.filter1ModSource = f.filter1.createModSourceSelector((1, 6), sticky=N+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.filters.filter1.modSource', x), width=33)
      f.filter1.createSmallText((1, 7), 'Mod')
      f.filter1.createSlider((1, 8), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter1.env2ModAmount', int(x)))
      f.filter1.createSmallText((1, 9), 'Env. 2 Mod Amount')
      f.filter1.createSlider((1, 10), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter1.keyboardTrack', int(x)))
      f.filter1.createSmallText((1, 11), 'Keyboard Track')
      f.filter1.createRGap(12, 10)
      
      f.createCGap(11, innerGap)
      
      # FILTER 2
      f.filter2 = Application()
      f.filter2.init(f.frame, darkGrey)
      f.filter2.frame.grid(column = 12, row = 4)
      f.filter2.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
      f.filter2.createCGap(0, panelInnerGap)
      f.filter2.createCGap(2, panelInnerGap)
      f.filter2.createTitle((1, 0), 'Filter 2')
      f.filter2.createRGap(1, 40)
      filter2Type, f.filter2Type, filter2TypeLabel = f.filter2.createMenuButton((1, 1), sticky=S, command=lambda x, v=v: sd.changeParameter(f'voice{v}.filters.filter2.type', x), width=15)
      f.filter2.createMenuButtonOption(filter2Type, 'High Pass 2', 0, f.filter2Type, filter2TypeLabel)
      f.filter2.createMenuButtonOption(filter2Type, 'High Pass 1', 1, f.filter2Type, filter2TypeLabel)
      f.filter2.createMenuButtonOption(filter2Type, 'Low Pass 2', 2, f.filter2Type, filter2TypeLabel)
      f.filter2.createMenuButtonOption(filter2Type, 'Low Pass 1', 3, f.filter2Type, filter2TypeLabel)
      filter2TypeLabel.set('High Pass 2')
      f.filter2.createSmallText((1, 2), 'Type')
      f.filter2.createSlider((1, 3), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter2.cutoff', int(x)))
      f.filter2.createSmallText((1, 4), 'Cutoff')
      f.filter2.createSlider((1, 5), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter2.modAmount', int(x)))
      f.filter2ModSource = f.filter2.createModSourceSelector((1, 6), sticky=N+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.filters.filter2.modSource', x), width=33)
      f.filter2.createSmallText((1, 7), 'Mod')
      f.filter2.createSlider((1, 8), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter2.env2ModAmount', int(x)))
      f.filter2.createSmallText((1, 9), 'Env. 2 Mod Amount')
      f.filter2.createSlider((1, 10), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.filters.filter2.keyboardTrack', int(x)))
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
      f.volume.createSlider((1, 1), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.volume', int(x)))
      f.volume.createSmallText((1, 2), 'Volume')
      f.volume.createSlider((1, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.volumeModAmount', int(x)))
      f.volumeModSource = f.volume.createModSourceSelector((1, 4), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.volumeModSource', x), width=33)
      f.volume.createSmallText((1, 5), 'Mod')
      f.volume.createSlider((1, 6), (-128, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.keyboardScaleAmount', int(x)))
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
      f.pan.createSlider((1, 1), (0, 127), start = 64, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.pan', int(x)))
      f.pan.createSmallText((1, 2), 'Pan')
      f.pan.createSlider((1, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, sd=sd:sd.changeParameter(f'voice{v}.output.panModAmount', int(x)))
      f.panModSource = f.pan.createModSourceSelector((1, 4), sticky=S+E+W, command=lambda x, v=v: sd.changeParameter(f'voice{v}.output.panModSource', x), width=33)
      f.pan.createSmallText((1, 5), 'Mod')
      f.createCGap(19, outerGap)
    
     
      # ENVELOPES
      def envelopeContextMenu(event, menu):
        try:
          menu.tk_popup(event.x_root, event.y_root)
        finally:
          menu.grab_release()
      
      f.envs = []
      f.envVars = []
      f.envModes = []
      f.envContexts = []
      envColSpan = 5
      c = 3
      r = 0
      for e in range(3):
        #f.createTitle((c, r), 'Envelope 1', columnspan=env1ColumnSpan)
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
        envParams.createSlider((1, 0), (0, 127), start = 0, sticky = W+E+N, command=lambda x, v=v, e=e, sd=sd:sd.changeParameter(f'voice{v}.envelopes.env{e}.attackTimeVelocitySens', int(x)))
        envParams.createSmallText((1, 1), 'Atk. Vel. Sens.')
        envParams.resizableC(1)
        envParams.createCGap(2, 3)
        envParams.createSlider((3, 0), (0, 127), start = 0, sticky = W+E+N, command=lambda x, v=v, e=e, sd=sd:sd.changeParameter(f'voice{v}.envelopes.env{e}.levelVelocitySens', int(x)))
        envParams.createSmallText((3, 1), 'Lvl. Vel. Sens.')
        envParams.resizableC(3)
        envParams.createCGap(4, 3)
        envParams.createSlider((5, 0), (0, 9), start = 0, sticky = W+E+N, command=lambda x, v=v, e=e, sd=sd:sd.changeParameter(f'voice{v}.envelopes.env{e}.velocityCurve', int(x)))
        envParams.createSmallText((5, 1), 'Vel. Curve')
        envParams.resizableC(5)
        envParams.createCGap(6, 3)
        envParams.createSlider((7, 0), (-127, 127), start = 0, sticky = W+E+N, command=lambda x, v=v, e=e, sd=sd:sd.changeParameter(f'voice{v}.envelopes.env{e}.keyboardTrack', int(x)))
        envParams.createSmallText((7, 1), 'Kbd. Track')
        envParams.resizableC(7)
        envParams.createCGap(8, 3)
        
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
    v = self.voices[0]
    
    for e in range(3):
      v.envVars[e] = [
        [
          params['voice0']['envelopes'][f'env{e}']['initialLevel'][2],
          params['voice0']['envelopes'][f'env{e}']['peakLevel'][2],
          params['voice0']['envelopes'][f'env{e}']['breakpoint1Level'][2],
          params['voice0']['envelopes'][f'env{e}']['breakpoint2Level'][2],
          params['voice0']['envelopes'][f'env{e}']['sustainLevel'][2]
        ],
        [
          params['voice0']['envelopes'][f'env{e}']['attackTime'][2],
          params['voice0']['envelopes'][f'env{e}']['decay1Time'][2],
          params['voice0']['envelopes'][f'env{e}']['decay2Time'][2],
          params['voice0']['envelopes'][f'env{e}']['decay3Time'][2],
          params['voice0']['envelopes'][f'env{e}']['releaseTime'][2]
        ]
      ]
    
    # self.params['voice0']['envelopes']['env0']['levelVelocitySans'][2] = values[10]
    # self.params['voice0']['envelopes']['env0']['attackTimeVelocitySens'][2] = values[11]
    # self.params['voice0']['envelopes']['env0']['keyboardTrack'][2] = neg(values[12])
    # self.params['voice0']['envelopes']['env0']['mode'][2] = (values[13] & 0xf0) >> 4
    # self.params['voice0']['envelopes']['env0']['velocityCurve'][2]
    
    





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