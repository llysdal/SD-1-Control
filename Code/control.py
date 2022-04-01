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
            11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 26, 28, 30, 32, 34, 37, 39, 42, 45, 49]

black = "#212121"
red = "#9D0000"
washedRed = "#6e3d3d"
darkRed = "#340000"
grey  = '#2e2e2e'
white = '#e2e2e2'
blue  = '#336ece'


class spinbox(tk.Spinbox):
  def set(self, value):
    self.delete(0,100)
    self.insert(0,value)

class Application():
  def init(self, master, titlefont, textfont, numberfont):
    self.master = master
    self.frame = tk.Frame(self.master, background="#9D0000")
    self.frame.grid(column=0, row=0, sticky=N+S+E+W)

    #Resizeability
    self.top = self.frame.winfo_toplevel()
    self.top.rowconfigure(0, weight=1)
    self.top.columnconfigure(0, weight=1)

    self.titlefont = titlefont
    self.textfont = textfont
    self.numberfont = numberfont

    self.frame.configure(background = black)

  def createCanvas(self, gridpos, frame = None, columnspan = 1, rowspan = 1, size = (100,100)):
    if frame == None: frame = self.frame
    canvas = tk.Canvas(frame, width = size[0], height = size[1], bg = 'black')
    canvas.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, rowspan = rowspan, sticky = N+S+E+W)

    return canvas
  
  def createTabs(self, gridpos, frame = None):
    if frame == None: frame = self.frame
    tabs = ttk.Notebook(frame)
    tabs.grid(column=gridpos[0], row=gridpos[1], sticky=N+S+E+W)
    frame.columnconfigure(gridpos[0], weight=1)
    frame.rowconfigure(gridpos[1], weight=1)
    return tabs
  
  def createTab(self, tabFrame, name):
    tab = ttk.Frame(tabFrame)
    tabFrame.add(tab, text=name)
    return tab
  
  def createSlider(self, gridpos, val, frame = None, res = 1, start = 0, length = 100, width = 15, orient = 0, columnspan = 1, rowspan = 1, showvalue = True, sticky = E+S, command = lambda s: None):
    if frame == None: frame = self.frame
    slider = tk.Scale(frame, from_ = val[0], to = val[1], resolution = res,\
                      orient = (HORIZONTAL, VERTICAL)[orient], length = length, showvalue = showvalue, width = width,
                      command = command)
    slider.configure(background = black, foreground = white, highlightthickness = 0, troughcolor = grey, activebackground = white, font = self.numberfont)
    slider.grid(column = gridpos[0], row = gridpos[1], rowspan = rowspan, columnspan = columnspan, sticky = sticky)

    slider.set(start)

    return slider

  def createDropdown(self, gridpos, frame = None, values = [1,2,3], start = 1, columnspan = 1, requestparent = False, command = lambda s: None):
    if frame == None: frame = self.frame
    string = tk.StringVar(frame)
    string.set(start)

    dropdown = tk.OptionMenu(frame, string, *values, command=command)
    dropdown.configure(background = black, foreground = white, highlightthickness = 0, borderwidth = 2)#, activebackground = self.blue)
    dropdown.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = E+S)

    if requestparent:
      return string, dropdown

    return string

  def createButton(self, gridpos, text, function, frame = None):
    if frame == None: frame = self.frame
    button = tk.Button(frame, text = text, command = function)
    button.configure(background = black, foreground = white)
    button.grid(column = gridpos[0], row = gridpos[1], stick = N+S+E+W)

  def createText(self, gridpos, text, frame = None, columnspan = 1, sticky = W+S):
    if frame == None: frame = self.frame
    label = tk.Label(frame, text = text, font = self.textfont, justify = 'left')
    label.configure(background = black, foreground = white)
    label.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return label

  def createTitle(self, gridpos, text, frame = None, columnspan = 1, sticky = E+W):
    if frame == None: frame = self.frame
    label = tk.Label(frame, text = text, font = self.titlefont, justify = 'left')
    label.configure(background = black, foreground = white)
    label.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return label

  def createDynText(self, gridpos, frame = None, columnspan = 1, sticky = E+N):
    if frame == None: frame = self.frame
    stringvar = tk.StringVar()

    label = tk.Label(frame, textvariable = stringvar, font = self.numberfont, justify = 'left')
    label.configure(background = black, foreground = white)
    label.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return stringvar

  def createCheckbutton(self, gridpos, text, frame = None, columnspan = 1, sticky = E+S):
    if frame == None: frame = self.frame
    intvar = tk.IntVar()

    button = tk.Checkbutton(frame, text = text, variable = intvar, onvalue = 1, offvalue = 0)
    button.configure(background = black)#, activebackground = self.blue)
    button.grid(column = gridpos[0], row = gridpos[1], columnspan = columnspan, sticky = sticky)

    return intvar

  def createSpinbox(self, gridpos, frame = None, from_ = 0, to = 10, values = [], width = 2, sticky = E+N, command = lambda: None):
    if frame == None: frame = self.frame
    if len(values) > 0:
      spin = spinbox(frame, values = values, width = width, command = command)
    else:
      spin = spinbox(frame, from_=from_, to=to, width = width, command = command)
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
  def __init__(self, master, sd, titlefont, textfont, numberfont):
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
          'background': black, 'foreground': white
        }
      },
      'TFrame': {
        'configure': {
          'background': black
        }
      },
      'TNotebook': {
          'configure': {
            'background': darkRed,
            'tabmargins': [0, 5, 2, 0],
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
    
    self.init(master, titlefont, textfont, numberfont)
    self.setup(sd)
    
  def envDrag(self, event, voice, env, step):
    v = self.voices[voice]
    if env == 1: envVars = v.env1Vars
    elif env == 2: envVars = v.env2Vars
    elif env == 3: envVars = v.env3Vars
    
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
      for envIndex, (env, envVars) in enumerate([(voice.env1, voice.env1Vars), (voice.env2, voice.env2Vars), (voice.env3, voice.env3Vars)]):
        lastPoint = (rectSize,0)
        for step, (level, duration) in enumerate(zip([*envVars[0], 0], [0, *envVars[1]])):
          newPoint = (lastPoint[0] + w/6*duration/99, (h-rectSize)-(h-rectSize*2)*level/127)
          if step == 5:
            line = env.find_withtag(f'line{step-1}')
            env.coords(line, lastPoint[0], lastPoint[1], lastPoint[0]+w/6, lastPoint[1])
            lastPoint = (lastPoint[0]+w/6, lastPoint[1])
            newPoint = (lastPoint[0] + w/6*duration/99, (h-rectSize)-(h-rectSize*2)*level/127)
            line = env.find_withtag(f'line{step}')
            env.coords(line, lastPoint[0], lastPoint[1], newPoint[0], newPoint[1])
          elif step > 0:
            line = env.find_withtag(f'line{step-1}')
            env.coords(line, lastPoint[0], lastPoint[1], newPoint[0], newPoint[1])
          
          if step > 0: 
            durText = env.find_withtag(f'duration{step-1}')
            env.coords(durText, (newPoint[0]-lastPoint[0])/2+lastPoint[0], (newPoint[1]-lastPoint[1])/2+lastPoint[1])
            env.itemconfigure(durText, text=f'{envTimes[duration]}s')
          
          rect = env.find_withtag(f'step{step}')
          env.coords(rect, newPoint[0]-rectSize, newPoint[1]-rectSize, newPoint[0]+rectSize, newPoint[1]+rectSize)
          lastPoint = newPoint
          
  def emitEnv(self, event, voice, env, step):
    v = self.voices[voice]
    if env == 1: envVars = v.env1Vars
    elif env == 2: envVars = v.env2Vars
    elif env == 3: envVars = v.env3Vars
    
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
        for e in [v.env1Context, v.env2Context, v.env3Context]:
          e.entryconfig("Paste", state=tk.ACTIVE)
    
    v = self.voices[voice]
    
    if env == 1: self.envelopeCopy = deepcopy(v.env1Vars)
    elif env == 2: self.envelopeCopy = deepcopy(v.env2Vars)
    elif env == 3: self.envelopeCopy = deepcopy(v.env3Vars)
  
  def pasteEnvelope(self, voice, env):
    if not self.envelopeCopy: 
      return
    
    v = self.voices[voice]
    
    if env == 1: v.env1Vars = deepcopy(self.envelopeCopy)
    elif env == 2: v.env2Vars = deepcopy(self.envelopeCopy)
    elif env == 3: v.env3Vars = deepcopy(self.envelopeCopy)

  def onWaveClassChange(self, voice, value):
    c = ['Waveform', 'Inharmonic', 'Transwave', 'Multi-wave', 'Sampled wave'].index(value)
    v = self.voices[voice]


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
    programmenu.add_command(label='Show Program List')
    programmenu.add_command(label='Save Program on SD-1')
    self.menu.add_cascade(label='Programs', menu=programmenu)
    
    self.menu.add_command(label="\u22EE", activebackground=self.menu.cget("background"), state=tk.DISABLED)
    
    optionmenu = tk.Menu(self.menu, tearoff=0)
    self.menu.add_cascade(label='Options', menu=optionmenu)

    mainTabs = self.createTabs((0,0))
    voicesTab = self.createTab(mainTabs, 'Master')
    voicesTab = self.createTab(mainTabs, 'MIDI')
    voicesTab = self.createTab(mainTabs, 'Program Control')
    voicesTab = self.createTab(mainTabs, 'Voices')

    voiceTabs = self.createTabs((0,0), frame=voicesTab)
    voice0Tab = self.createTab(voiceTabs, 'Voice 1')
    voice1Tab = self.createTab(voiceTabs, 'Voice 2')
    voice2Tab = self.createTab(voiceTabs, 'Voice 3')
    voice3Tab = self.createTab(voiceTabs, 'Voice 4')
    voice4Tab = self.createTab(voiceTabs, 'Voice 5')
    voice5Tab = self.createTab(voiceTabs, 'Voice 6')
    
    self.envelopeCopy = None
    
    self.voices = []
    for v in range(6):
      self.voices.append(Application())
      f = self.voices[v]
      f.init((voice0Tab, voice1Tab, voice2Tab, voice3Tab, voice4Tab, voice5Tab)[v], self.titlefont, self.textfont, self.numberfont)
      f.frame.grid(column = 0, row = 0)

      c = 0
      r = 0
      
      f.createTitle((c, r), 'Wave')
      f.createText((c, r+1), 'Class')
      f.waveclass = f.createDropdown((c+1, r+1), values=['Waveform', 'Inharmonic', 'Transwave', 'Multi-wave', 'Sampled wave'], start = 'Waveform', command=lambda value, voice=v, gui=self: gui.onWaveClassChange(voice, value))
      f.createText((c, r+2), 'Waveform')
      f.waveform = f.createDropdown((c+1, r+2), values=['Loading...'], start = 'Loading...')
      
      c += 10
      r += 0
      
      def envelopeContextMenu(event, menu):
        try:
          menu.tk_popup(event.x_root, event.y_root)
        finally:
          menu.grab_release()
      
      f.createTitle((c, r), 'Envelope 1')
      f.env1 = f.createCanvas((c, r+1), size=(500,100))
      f.env1Vars = [[0, 127, 100, 127, 50], [5, 99, 25, 50, 20]]
      f.env1Context = tk.Menu(f.frame, tearoff=0)
      f.env1Context.add_command(label='Copy', command=lambda voice=v, gui=self: gui.copyEnvelope(voice, 1))
      f.env1Context.add_command(label='Paste', state=tk.DISABLED, command=lambda voice=v, gui=self: gui.pasteEnvelope(voice, 1))
      f.env1.bind("<Button-3>", lambda event, menu=f.env1Context: envelopeContextMenu(event, menu))

      f.createTitle((c + 1, r), 'Envelope 2')
      f.env2 = f.createCanvas((c + 1, r+1), size=(500,100))
      f.env2Vars = [[0, 127, 100, 127, 50], [5, 99, 25, 50, 20]]
      f.env2Context = tk.Menu(f.frame, tearoff=0)
      f.env2Context.add_command(label='Copy', command=lambda voice=v, gui=self: gui.copyEnvelope(voice, 2))
      f.env2Context.add_command(label='Paste', state=tk.DISABLED, command=lambda voice=v, gui=self: gui.pasteEnvelope(voice, 2))
      f.env2.bind("<Button-3>", lambda event, menu=f.env2Context: envelopeContextMenu(event, menu))
        
      f.createTitle((c + 2, r), 'Envelope 3')
      f.env3 = f.createCanvas((c + 2, r+1), size=(500,100))
      f.env3Vars = [[0, 127, 100, 127, 50], [5, 99, 25, 50, 20]]
      f.env3Context = tk.Menu(f.frame, tearoff=0)
      f.env3Context.add_command(label='Copy', command=lambda voice=v, gui=self: gui.copyEnvelope(voice, 3))
      f.env3Context.add_command(label='Paste', state=tk.DISABLED, command=lambda voice=v, gui=self: gui.pasteEnvelope(voice, 3))
      f.env3.bind("<Button-3>", lambda event, menu=f.env3Context: envelopeContextMenu(event, menu))
      
      for i in range(6): 
        line = f.env1.create_line(0, 0, 0, 0, tags=(f'line{i}'), fill = '#2b7cff')
        line = f.env2.create_line(0, 0, 0, 0, tags=(f'line{i}'), fill = '#2b7cff')
        line = f.env3.create_line(0, 0, 0, 0, tags=(f'line{i}'), fill = '#2b7cff')
        
        rect = f.env1.create_rectangle(0, 0, 0, 0, tags=(f'step{i}'), fill = '#2b7cff')
        f.env1.tag_bind(rect, '<B1-Motion>', lambda event, voice=v, step=i, gui=self: gui.envDrag(event, voice, 1, step))
        f.env1.tag_bind(rect, '<ButtonRelease-1>', lambda event, voice=v, step=i, gui=self: gui.emitEnv(event, voice, 1, step))
        rect = f.env2.create_rectangle(0, 0, 0, 0, tags=(f'step{i}'), fill = '#2b7cff')
        f.env2.tag_bind(rect, '<B1-Motion>', lambda event, voice=v, step=i, gui=self: gui.envDrag(event, voice, 2, step))
        f.env2.tag_bind(rect, '<ButtonRelease-1>', lambda event, voice=v, step=i, gui=self: gui.emitEnv(event, voice, 2, step))       
        rect = f.env3.create_rectangle(0, 0, 0, 0, tags=(f'step{i}'), fill = '#2b7cff')
        f.env3.tag_bind(rect, '<B1-Motion>', lambda event, voice=v, step=i, gui=self: gui.envDrag(event, voice, 3, step))
        f.env3.tag_bind(rect, '<ButtonRelease-1>', lambda event, voice=v, step=i, gui=self: gui.emitEnv(event, voice, 3, step))
        
        f.env1.create_text(0, 0, tags=(f'duration{i}'), fill = '#ffffff')
        f.env2.create_text(0, 0, tags=(f'duration{i}'), fill = '#ffffff')
        f.env3.create_text(0, 0, tags=(f'duration{i}'), fill = '#ffffff')
      
      #self.filtercutoff = self.createSlider((0, 1), (0,127), frame=voiceTab, command = lambda v, sd=sd, i=i: sd.changeParameter(f'voice{i}.filters.filter1.cutoff', int(v)))
    
    

    #Background
    # backimage = tk.PhotoImage(file = fh.getRessourcePath('background.png'))
    # backlabel = tk.Label(self.frame, image=backimage, bd = 0)
    # backlabel.place(x=0, y=0)
    # backlabel.image = backimage
