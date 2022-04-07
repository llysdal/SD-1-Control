g = __import__('control')
import tkinter as tk
from tkinter import N,S,E,W, HORIZONTAL, VERTICAL, BROWSE, filedialog, ttk, CENTER
from math import exp
import wave, struct
import json
from copy import deepcopy
import os
curDir = os.path.dirname(os.path.abspath(__file__))[0:-4]

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

class VSmain(g.Application):
  def __init__(self, master, vs, background):
    self.vs = vs
    
    s = ttk.Style()
    s.theme_create('vs', settings={
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
    s.theme_use('vs')
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
    self.setup(vs)
    
  def saveProgram(self):
    file = filedialog.asksaveasfile(title='Save Program', filetypes=[('Program', '.pgm')], defaultextension='.pgm', initialdir=curDir+'Data/ProgramsVS')
    print(f'{self.vs.transDecoupled}Saving program...')
    if file:
      json.dump(self.vs.params, file)
      file.close()
      print(f'{self.vs.endNoRecv}Saved successfully')
    else:
      print(f'{self.vs.alrt}Failed to save program')
    
  def loadProgram(self):
    file = filedialog.askopenfile(title='Load Program', filetypes=[('Program', '.pgm')], initialdir=curDir+'Data/ProgramsVS')
    print(f'{self.vs.transDecoupled}Loading program...')
    if file:
      self.vs.params = json.load(file)
      file.close()
      self.loadParameters(self.vs.getParameters())
      print(f'{self.vs.endNoRecv}Loaded successfully')
    else:
      print(f'{self.vs.alrt}Failed to load program')
    
  def updateEnvs(self):
    pass
    
  def setup(self, vs):
    self.master.title('Vector Synthesis Main Control')
    self.master.iconbitmap(g.fh.getRessourcePath('vs.ico'))
    
    self.master.minsize(500, 300)

    self.menu = self.createMenu()
    
    systemmenu = tk.Menu(self.menu, tearoff=0)
    self.menu.add_cascade(label='System', menu=systemmenu)
    
    self.menu.add_command(label="\u22EE", activebackground=self.menu.cget("background"), state=tk.DISABLED)

    programmenu = tk.Menu(self.menu, tearoff=0)
    programmenu.add_command(label='Request current', command = vs.requestCurrentProgram)
    programmenu.add_command(label='Send current', command = vs.saveProgramDump)
    programmenu.add_separator()
    programmenu.add_command(label='Save Program',   command = self.saveProgram)
    programmenu.add_command(label='Load Program',   command = self.loadProgram)
    self.menu.add_cascade(label='Programs', menu=programmenu)
    
    self.menu.add_command(label="\u22EE", activebackground=self.menu.cget("background"), state=tk.DISABLED)
    
    optionmenu = tk.Menu(self.menu, tearoff=0)
    optionmenu.add_command(label='Decouple',   command = vs.decouple)
    optionmenu.add_command(label='Couple',   command = vs.couple)
    self.menu.add_cascade(label='Options', menu=optionmenu)

    self.createRGap(0, 5)
    mainTabs = self.createTabs((0,1))
    masterFrame, masterTab = self.createTab(mainTabs, 'Master')
    midiFrame, midiTab = self.createTab(mainTabs, 'MIDI')
    programFrame, programTabs = self.createTab(mainTabs, 'Voices')
    mainTabs.select(programTabs)
    
    
    osc1 = g.Application()
    osc1.init(self.frame, darkGrey)
    osc1.frame.grid(column = 1, row = 1)
    osc1.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
    osc2 = g.Application()
    osc2.init(self.frame, darkGrey)
    osc2.frame.grid(column = 2, row = 1)
    osc2.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
    osc3 = g.Application()
    osc3.init(self.frame, darkGrey)
    osc3.frame.grid(column = 1, row = 2)
    osc3.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
    osc4 = g.Application()
    osc4.init(self.frame, darkGrey)
    osc4.frame.grid(column = 2, row = 2)
    osc4.frame.configure(background=darkGrey, relief='ridge', borderwidth=2)
    
    #Oscillators
    for v in range(4):
      f = (osc1, osc2, osc3, osc4)[v]
      
      f.waveTabs = f.createTabs((1,1), rowspan=2, command=lambda x, vs=vs, v=v: vs.changeWaveType(v, x))
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
      f.waveformWave.trace_add("write", lambda x, y, z, var=f.waveformWave, v=v, vs=vs:(
        vs.changeParameter(f'voice{v}.wave.waveform.waveName', var.get())))
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
      f.transwaveWave.trace_add("write", lambda x, y, z, var=f.transwaveWave, v=v, vs=vs:(
        vs.changeParameter(f'voice{v}.wave.transwave.waveName', var.get())))
      f.transwaveStart = f.transwaveFrame.createSlider((3, 1), (0, 99), start = 0, sticky=S+E+W, command=lambda x, v=v, vs=vs:vs.changeParameter(f'voice{v}.wave.transwave.waveStart', int(x)))
      f.transwaveFrame.createSmallText((3, 2), 'Start')
      f.transwaveModAmount = f.transwaveFrame.createSlider((3, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, vs=vs:vs.changeParameter(f'voice{v}.wave.transwave.waveModAmount', int(x)))
      f.transwaveModSource = f.transwaveFrame.createModSourceSelector((3, 4), sticky=S+E+W, command=lambda x, v=v: vs.changeParameter(f'voice{v}.wave.transwave.waveModSource', x))
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
      f.sampledWave.trace_add("write", lambda x, y, z, var=f.sampledWave, v=v, vs=vs:
        vs.changeParameter(f'voice{v}.wave.sampledWave.waveName', var.get()))
      f.sampledWaveStart = f.sampledFrame.createSlider((3, 1), (0, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, vs=vs:vs.changeParameter(f'voice{v}.wave.sampledWave.waveStartIndex', int(x)))
      f.sampledFrame.createSmallText((3, 2), 'Start')
      f.sampledWaveStartVelocityMod = f.sampledFrame.createSlider((3, 3), (-127, 127), start = 0, sticky=S+E+W, command=lambda x, v=v, vs=vs:vs.changeParameter(f'voice{v}.wave.sampledWave.waveVelocityStartMod', int(x)))
      f.sampledFrame.createSmallText((3, 4), 'Velocity Start Mod')
      sampledWaveLoopDirection, f.sampledWaveLoopDirection, sampledWaveLoopDirectionLabel = f.sampledFrame.createMenuButton((1, 3), sticky=S+E+W, width=18,
                                                                        command=lambda x, v=v: vs.changeParameter(f'voice{v}.wave.sampledWave.waveDirection', x))
      f.sampledFrame.createSmallText((1, 4), 'Wave Direction')
      f.sampledFrame.createMenuButtonOptions(sampledWaveLoopDirection, ['Forward', 'Reverse'], f.sampledWaveLoopDirection, sampledWaveLoopDirectionLabel)
      f.sampledFrame.createRGap(0, 5)
      f.sampledFrame.createCGap(0, 15)
      f.sampledFrame.createCGap(2, 10)
      f.sampledFrame.createCGap(4, 15)
      
      # MULTI-WAVE
      f.multiwaveLoopStart = f.multiwaveFrame.createSlider((3, 1), (0, 249), start = 0, sticky=S+E+W, command=lambda x, v=v, vs=vs:vs.changeParameter(f'voice{v}.wave.multiWave.loopWaveStart', int(x)))
      f.multiwaveFrame.createSmallText((3, 2), 'Loop Start')
      f.multiwaveLoopLength = f.multiwaveFrame.createSlider((3, 3), (1, 243), start = 243, sticky=S+E+W, command=lambda x, v=v, vs=vs:vs.changeParameter(f'voice{v}.wave.multiWave.loopLength', int(x)))
      f.multiwaveFrame.createSmallText((3, 4), 'Loop Length')
      multiwaveLoopDirection, f.multiwaveLoopDirection, multiwaveLoopDirectionLabel = f.multiwaveFrame.createMenuButton((1, 1), sticky=S+E+W, width=16,
                                                                        command=lambda x, v=v: vs.changeParameter(f'voice{v}.wave.multiWave.loopDirection', x))
      f.multiwaveFrame.createSmallText((1, 2), 'Loop Direction')
      f.multiwaveFrame.createMenuButtonOptions(multiwaveLoopDirection, ['Forward', 'Reverse'], f.multiwaveLoopDirection, multiwaveLoopDirectionLabel)
      f.multiwaveFrame.createRGap(0, 5)
      f.multiwaveFrame.createCGap(0, 15)
      f.multiwaveFrame.createCGap(2, 10)
      f.multiwaveFrame.createCGap(4, 15)
    
  
  def loadParameters(self, params):
    pass