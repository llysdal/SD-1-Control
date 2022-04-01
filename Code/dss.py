midi = __import__('midi')
t = __import__('tools')

channel = 0

EST    = 0b11110000
korgID = 0b01000010
formID = 0b00110000 + channel
dssID  = 0b00001011
EOX    = 0b11110111

sysexGet = {'mode'          : [EST, korgID, formID, dssID, 0x12, EOX],
            'parameters'    : [EST, korgID, formID, dssID, 0x10, 'program', EOX],
            'programlist'   : [EST, korgID, formID, dssID, 0x17, EOX],
            'multisound'    : [EST, korgID, formID, dssID, 0x15, 'number', EOX],
            'multisoundlist': [EST, korgID, formID, dssID, 0x16, EOX],
            'pcmdata'       : [EST, korgID, formID, dssID, 0x14, 'start', 'end', EOX]}

sysexSet = {'playmode'      : [EST, korgID, formID, dssID, 0x13, EOX],
            'parameter'     : [EST, korgID, formID, dssID, 0x41, 'parameter', 'value', EOX],
            'parameters'    : [EST, korgID, formID, dssID, 0x40, 'parameters', 'name', EOX],
            'writeprogram'  : [EST, korgID, formID, dssID, 0x11, 'program', EOX],
            'multisound'    : [EST, korgID, formID, dssID, 0x44, 'number', 'name', 'length', 'loopsounds', 'maxinterval', 'soundparams', 'checksum', EOX],
            'multisoundlist': [EST, korgID, formID, dssID, 0x45, 'amount', 'data', 'checksum', EOX],
            'pcmdata'       : [EST, korgID, formID, dssID, 0x43, 'start', 'end', 'data', 'checksum', EOX]}

class DSS():
    def __init__(self, inputID, outputID, debug=False, logParameterChanges=False):
        self.input  = midi.getMidiInputDevice(inputID)
        self.output = midi.getMidiOutputDevice(outputID)

        self.updateGUI = False
        self.emitPCM = False
        self.debug = debug
        self.logParameterChanges = logParameterChanges
        self.trans =        '┌─T  '
        self.transNoExp =   '  T  '
        self.alrt =         '└──//── '
        self.info =         '├────── '
        self.recv =         '└──R '
        self.linebreakRecv = True
        
        self.operationQueue = []
        self.runningOperation = False
        self.receivedResponse = False
        
        #Assume she's in playmode
        self.mode = 0
        self.modeNames = (
            'Play',
            'Sample',
            'Edit Sample',
            'Create Waveform',
            'Multisound',
            'MIDI',
            'System',
            'Disk Utility',
            'Program Parameter'
        )
        #Namelist
        self.namelist = []
        for i in range(32):
            self.namelist.append('NO-COMM')

        #PCM
        self.pcmStart = 0
        self.pcmEnd   = 0
        self.pcmLen   = 0
        self.pcmRange = 261885
        self.pcmMaxTime = 999999
        self.pcm      = []
        
        self.samples = []

        #Multisound dictionary
        self.multiAmount = 0
        self.multiName = []
        self.multiLen = []

        #Multisound parameters
        self.msparam = {'number'        :   0,
                        'name'          :   '',
                        'length'        :   0,
                        'loop'          :   0,
                        'sounds'        :   1,
                        'maxinterval'   :   0,
                        'checksum'      :   0}
        self.soundparam = {'topkey'     :   72,
                           'origkey'    :   60,
                           'tune'       :   64,
                           'level'      :   63,
                           'cutoff'     :   63,
                           'soundwadr'  :   1,
                           'soundsadr'  :   0,
                           'soundlen'   :   1,
                           'loopsadr'   :   0,
                           'looplen'    :   1,
                           'transpose'  :   1,
                           'samplingfreq':  0}
        self.soundparameters = []
        for i in range(16):
            self.soundparameters.append(self.soundparam.copy())
        #Initial DSS1 parameters
        self.param = {'osc1vol'         :   {'l': 0, 'h': 127, 'v': 100},   #osc 1 mix ratio
                      'osc2vol'         :   {'l': 0, 'h': 127, 'v':   0},   #osc 2 mix ratio
                      'autobendint'     :   {'l': 0, 'h': 127, 'v':   0},   #auto bend intensity
                      'noisevol'        :   {'l': 0, 'h':  63, 'v':   0},   #noise level
                      'vcfmode'         :   {'l': 0, 'h':   1, 'v':   1},   #vcf mode
                      'vcfegpol'        :   {'l': 0, 'h':   1, 'v':   1},   #vcf eg polarity
                      'vcfcutoff'       :   {'l': 0, 'h': 127, 'v': 127},   #vcf cutoff frequency
                      'vcfegint'        :   {'l': 0, 'h':  63, 'v':   0},   #vcf eg intensity
                      'vcfres'          :   {'l': 0, 'h':  63, 'v':   0},   #vcf resonance
                      'vcfkbd'          :   {'l': 0, 'h':  63, 'v':   0},   #vcf keyboard track
                      'vcfmgfreq'       :   {'l': 0, 'h':  63, 'v':  44},   #vcf mg-frequency
                      'vcfmgdelay'      :   {'l': 0, 'h':  63, 'v':   0},   #vcf mg-delay
                      'vcfmgint'        :   {'l': 0, 'h':  63, 'v':   0},   #vcf mg-intensity
                      'vcfega'          :   {'l': 0, 'h':  63, 'v':   0},   #vcf eg attack
                      'vcfegd'          :   {'l': 0, 'h':  63, 'v':  63},   #decay
                      'vcfegb'          :   {'l': 0, 'h':  63, 'v':  63},   #break point
                      'vcfegsl'         :   {'l': 0, 'h':  63, 'v':  63},   #slope
                      'vcfegs'          :   {'l': 0, 'h':  63, 'v':  63},   #sustain
                      'vcfegr'          :   {'l': 0, 'h':  63, 'v':   0},   #release
                      'vcadkbd'         :   {'l': 0, 'h': 127, 'v':   0},   #vca decay keyboard track (val above 63 negative)
                      'vcalevel'        :   {'l': 0, 'h':  63, 'v':  50},   #vca total level
                      'vcaega'          :   {'l': 0, 'h':  63, 'v':   0},   #vca eg attack
                      'vcaegd'          :   {'l': 0, 'h':  63, 'v':  63},   #decay
                      'vcageb'          :   {'l': 0, 'h':  63, 'v':  63},   #break point
                      'vcaegsl'         :   {'l': 0, 'h':  63, 'v':  63},   #slope
                      'vcaegs'          :   {'l': 0, 'h':  63, 'v':  63},   #sustain
                      'vcaegr'          :   {'l': 0, 'h':  63, 'v':   0},   #release
                      'vel-autobendint' :   {'l': 0, 'h':  63, 'v':   0},   #velocity sensitive auto bend intensity
                      'vel-vcfcutoff'   :   {'l': 0, 'h':  63, 'v':   0},   #cutoff
                      'vel-vcfega'      :   {'l': 0, 'h':  63, 'v':   0},   #vcf eg attack
                      'vel-vcfegd'      :   {'l': 0, 'h':  63, 'v':   0},   #vcf eg decay
                      'vel-vcfegsl'     :   {'l': 0, 'h':  63, 'v':   0},   #vcf eg slope
                      'vel-vcaeglevel'  :   {'l': 0, 'h':  63, 'v':   0},   #vca eg level
                      'vel-vcaega'      :   {'l': 0, 'h':  63, 'v':   0},   #vca eg attack
                      'vel-vcaegd'      :   {'l': 0, 'h':  63, 'v':   0},   #vca eg decay
                      'vel-vcaegsl'     :   {'l': 0, 'h':  63, 'v':   0},   #vca eg slope
                      'aft-oscmgint'    :   {'l': 0, 'h':  15, 'v':   0},   #after touch oscillator mg intensity
                      'aft-vcfmod'      :   {'l': 0, 'h':  15, 'v':   0},   #vcf mod (cutoff / mg)
                      'aft-vcfpar.'     :   {'l': 0, 'h':   1, 'v':   0},   #vcf mod slot
                      'aft-vcalevel'    :   {'l': 0, 'h':  15, 'v':   0},   #vca level
                      'joypitchrange'   :   {'l': 0, 'h':  12, 'v':   2},   #joystick pitch bend range
                      'joyvcf'          :   {'l': 0, 'h':   1, 'v':   0},   #joystick vcf sweep
                      'eqtreble'        :   {'l': 0, 'h':  12, 'v':   4},   #equalizer treble
                      'eqbass'          :   {'l': 0, 'h':  12, 'v':   4},   #equalizer bass
                      'ddlmgafreq'      :   {'l': 0, 'h':  63, 'v':  20},   #delay mg-a frequency
                      'ddlmgbfreq.'     :   {'l': 0, 'h':  63, 'v':  20},   #delay mg-b frequency
                      'ddl1time'        :   {'l': 0, 'h': 500, 'v': 500},   #delay 1 time
                      'ddl1fb'          :   {'l': 0, 'h':  15, 'v':   0},   #delay 1 feedback
                      'ddl1level'       :   {'l': 0, 'h':  15, 'v':   0},   #delay 1 effect level
                      'ddl1mgaint'      :   {'l': 0, 'h':  63, 'v':   0},   #delay 1 mg a modulation intensity
                      'ddl1mgbint'      :   {'l': 0, 'h':  63, 'v':   0},   #delay 1 mg b modulation intensity
                      'ddl2input'       :   {'l': 0, 'h':   1, 'v':   0},   #delay 2 input select
                      'ddl2time'        :   {'l': 0, 'h': 500, 'v': 500},   #delay 2 time
                      'ddl2fb'          :   {'l': 0, 'h':  15, 'v':   0},   #delay 2 feedback
                      'ddl2level'       :   {'l': 0, 'h':  15, 'v':   0},   #delay 2 effect level
                      'ddl2mgaint'      :   {'l': 0, 'h':  63, 'v':   0},   #delay 2 mg a modulation intensity
                      'ddl2mgbint'      :   {'l': 0, 'h':  63, 'v':   0},   #delay 2 mg b modulation intensity
                      'ddl2modinv'      :   {'l': 0, 'h':   1, 'v':   0},   #delay 2 modulation invertion
                      'osc1ms'          :   {'l': 0, 'h':  15, 'v':   0},   #oscillator 1 multi sound number
                      'osc2ms'          :   {'l': 0, 'h':  15, 'v':   0},   #oscillator 2 multi sound number
                      'oscbendrange'    :   {'l': 0, 'h':  12, 'v':  12},   #do not touch?
                      'sync'            :   {'l': 0, 'h':   1, 'v':   0},   #osc 2 sync
                      'resolution'      :   {'l': 0, 'h':   4, 'v':   4},   #d/a resolution
                      'osc1oct'         :   {'l': 0, 'h':   2, 'v':   1},   #osc 1 octave
                      'osc2oct'         :   {'l': 0, 'h':   2, 'v':   1},   #osc 2 octave
                      'osc2detune'      :   {'l': 0, 'h':  63, 'v':   0},   #osc 2 detune
                      'osc2interval'    :   {'l': 0, 'h':  11, 'v':   0},   #osc 2 interval
                      'oscmgselect'     :   {'l': 0, 'h':   3, 'v':   3},   #modulation select
                      'oscmgfreq'       :   {'l': 0, 'h':  31, 'v':  18},   #osc mod freq
                      'oscmgint'        :   {'l': 0, 'h':  15, 'v':   0},   #osc mod intensity
                      'oscmgdelay'      :   {'l': 0, 'h':  15, 'v':   0},   #osc mod delay
                      'autobendselect'  :   {'l': 0, 'h':   3, 'v':   3},   #auto bend select
                      'autobendpol'     :   {'l': 0, 'h':   1, 'v':   1},   #auto bend polarity
                      'autobendtime'    :   {'l': 0, 'h':  31, 'v':   0},   #auto bend time
                      'unisondetune'    :   {'l': 0, 'h':   7, 'v':   7},   #unison detune
                      'veloscchange'    :   {'l': 0, 'h':  31, 'v':   0},   #???
                      'assign'          :   {'l': 0, 'h':   2, 'v':   1},   #poly2, poly1, unison
                      'unisonvoices'    :   {'l': 0, 'h':   3, 'v':   3}}   #amount of unison voices

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
            

    def lenDecode(self, sysex):
        #stupid data coming from DSS1 (Service manual page 6 [4](1))
        lenSum =  min(sysex[1], 1)
        lenSum += sysex[0] * (2**1)
        lenSum += min(sysex[3], 1) * (2**8)
        lenSum += sysex[2] * (2**9)
        lenSum += min(sysex[5], 1) * (2**16)
        lenSum += sysex[4] * (2**17)

        return lenSum

    def lenEncode(self, length):
        #Same as above, but reverse
        binary = bin(length)[2:].zfill(19)
        sysex = [0,0,0,0,0,0]

        sysex[4] = int(binary[0:2], 2)
        sysex[5] = int(binary[2], 2) * (2**6)
        sysex[2] = int(binary[3:10], 2)
        sysex[3] = int(binary[10], 2) * (2**6)
        sysex[0] = int(binary[11:18], 2)
        sysex[1] = int(binary[18], 2) * (2**6)

        return sysex
    
    def addSample(self, sampleName, start, length):
        self.samples.append([sampleName, start, length])
        
    def getSampleMemoryFreeLoc(self):
        return max([s[1] + s[2] for s in self.samples], default=0)
    
    def pcmEncodeSample(self, sample):
        b = bin(max(0, min(4095, int(sample*2048)+2048)))[2:].zfill(12)
        
        sysex = [0, 0]
        
        sysex[0] = int(b[7:12], 2) << 2
        sysex[1] = int(b[0:7], 2)
        
        return sysex
    
    def pcmEncode(self, samples):
        return [b for s in samples for b in self.pcmEncodeSample(s)]

    def checksum(self, data):
        checksum = bin(sum(data))[2:].zfill(8)[-7:]
        return int(checksum, 2)

    def pcmEstimate(self, length):
        #Sysex delay times half the pcm length
        return 0.002 * (length/2)

    def decodeSysex(self, sysex):
        #Check if the sysex message is for us.
        if sysex[0:4] == [EST, korgID, formID, dssID]:
            self.receivedResponse = True
            
            #Mode Data
            if sysex[4] == 0x42:
                if self.debug: print(f'{self.recv}Mode data')
                self.mode = sysex[5]
                self.updateGUI = True

            #Multi Sound List
            elif sysex[4] == 0x45:
                if self.debug: print(f'{self.recv}Multi sound name list')
                self.multiLen = []
                self.multiName = []
            
                #Assigning data
                self.multiAmount = sysex[5]

                for i in range(self.multiAmount):
                    self.multiName.append(''.join(map(chr, sysex[6+14*i:6+14*i+8])).strip())
                    self.multiLen.append(self.lenDecode(sysex[6+14*i+8:6+14*i+14]))
                    
                while len(self.multiName) < 16:
                    self.multiName.append(f'EMPTY {len(self.multiName)+1:02d}')
                    
                while len(self.multiLen) < 16:
                    self.multiLen.append(0)

                self.updateGUI = True

            #Multi Sound Parameter Dump
            elif sysex[4] == 0x44:
                if self.debug: print(f'{self.recv}Multi sound parameters')

                sysex = sysex[5:-1]

                self.msparam['number'] = sysex[0]
                sysex = sysex[1:]

                self.msparam['name']   = ''.join(map(chr, sysex[0:8]))
                sysex = sysex[8:]

                self.msparam['length'] = self.lenDecode(sysex[0:6])
                sysex = sysex[6:]

                if sysex[0]>63:
                    self.msparam['loop'] = 1
                    self.msparam['sounds'] = sysex[0]-64
                else:
                    self.msparam['loop'] = 0
                    self.msparam['sounds'] = sysex[0]
                sysex = sysex[1:]

                self.msparam['maxinterval'] = sysex[0]
                sysex = sysex[1:]

                #Sound handling
                for s in range(self.msparam['sounds']):
                    self.soundparameters[s]['topkey']   = sysex[0]
                    self.soundparameters[s]['origkey']  = sysex[1]
                    self.soundparameters[s]['tune']     = sysex[2]
                    self.soundparameters[s]['level']    = sysex[3]
                    self.soundparameters[s]['cutoff']   = sysex[4]
                    self.soundparameters[s]['soundwadr']= self.lenDecode(sysex[5:11])
                    self.soundparameters[s]['soundsadr']= self.lenDecode(sysex[11:17])
                    self.soundparameters[s]['soundlen'] = self.lenDecode(sysex[17:23])
                    self.soundparameters[s]['loopsadr'] = self.lenDecode(sysex[23:29])
                    self.soundparameters[s]['looplen']  = self.lenDecode(sysex[29:35])

                    if sysex[35]>63:
                        self.soundparameters[s]['transpose'] = 0
                        self.soundparameters[s]['samplingfreq'] = sysex[35]-64
                    else:
                        self.soundparameters[s]['transpose'] = 1
                        self.soundparameters[s]['samplingfreq'] = sysex[35]

                    sysex = sysex[36:]

                self.msparam['checksum'] = sysex[-1]

                self.updateGUI = True

            #PCM Data Dump
            elif sysex[4] == 0x43:
                if self.debug: print(f'{self.recv}PCM data dump')

                sysex = sysex[5:-1]

                self.pcmStart = self.lenDecode(sysex[0:6])
                sysex = sysex[6:]
                self.pcmEnd = self.lenDecode(sysex[0:6])
                sysex = sysex[6:]

                self.pcmLen = self.pcmEnd - self.pcmStart

                self.pcm = []
                for p in range(self.pcmLen):
                    pcmVal =  sysex[0]>>2
                    pcmVal += sysex[1]*32
                    pcmVal -= 2048
                    self.pcm.append(pcmVal)
                    sysex = sysex[2:]

                self.emitPCM = True

            #Program Name List
            elif sysex[4] == 0x46:
                if self.debug: print(f'{self.recv}Program name list')
                
                for i in range(32):
                    self.namelist[i] = ''.join(map(chr, sysex[5+8*i:5+8*i+8]))

                self.updateGUI = True

            #Program Parameter Dump
            elif sysex[4] == 0x40:
                if self.debug: print(f'{self.recv}Program parameters')

                sysex = sysex[5:-1]
                #Replace the stored parameters with the sysex gotten ones
                for i, key in enumerate(self.param.keys()):
                    if i != 46 and i != 52:
                        self.param[key]['v'] = sysex[0]
                        sysex.pop(0)
                    else:
                        #Special case for the delay times, where instead of 1 byte we receive 2 bytes.
                        self.param[key]['v'] = sysex[0] + sysex[1]*128
                        sysex.pop(0)
                        sysex.pop(0)

                self.updateGUI = True

            #Data Load Completed
            elif sysex[4] == 0x23:
                if self.debug: print(f'{self.recv}Data load complete')
                pass

            #Data Load Error
            elif sysex[4] == 0x24:
                if self.debug: print(f'{self.alrt}Data load error')
                pass

            #Write Completed
            elif sysex[4] == 0x21:
                if self.debug: print(f'{self.recv}Write complete')
                pass

            #Write Error
            elif sysex[4] == 0x22:
                if self.debug: print(f'{self.alrt}Write error')
                pass
            
            if self.debug and self.linebreakRecv:
                print()


    def getMode(self):
        if self.debug: print(f'{self.trans}Get mode')

        midi.sendSysex(self.output, sysexGet['mode'])

    def setPlayMode(self):
        if self.debug: print(f'{self.transNoExp}Set mode to playmode')

        midi.sendSysex(self.output, sysexSet['playmode'])

    def programChange(self, program):
        if self.debug: print(f'{self.transNoExp}Change program to '+ str(program+1))

        midi.sendMidi(self.output, 192, program, 0)
        self.updateGUI = True

    def getNameList(self):
        if self.debug: print(f'{self.trans}Request program name list')

        midi.sendSysex(self.output, sysexGet['programlist'])

    def getPCM(self, start, end):
        if self.debug: print(f'{self.trans}Request PCM from address ' + str(start) + ' to ' + str(end))

        if start < 0 or start > self.pcmRange or end < start or end > self.pcmRange:
            print(f'{self.alrt}PCM request out of bounds, cancelling')
            return

        est = self.pcmEstimate(end-start)
        print(f'{self.info}PCM estimated time is {est:.1f}s')
        if est > self.pcmMaxTime:
            print(f'{self.alrt}PCM estimate over max time of ' + str(self.pcmMaxTime) + 's, cancelling')
            return

        sysex = sysexGet['pcmdata'].copy()
        startIndex = sysex.index('start')
        sysex[startIndex:startIndex+1] = self.lenEncode(start)

        endIndex = sysex.index('end')
        sysex[endIndex:endIndex+1] = self.lenEncode(end)

        midi.sendSysex(self.output, sysex)
        
    def setPCM(self, wave, offset):
        start = offset
        end = len(wave) + offset
        
        if self.debug: print(f'{self.trans}Sending PCM from address ' + str(start) + ' to ' + str(end))

        if start < 0 or start > self.pcmRange or end < start or end > self.pcmRange:
            print(f'{self.alrt}PCM dump out of bounds, cancelling')
            return

        est = self.pcmEstimate(end-start)
        print(f'{self.info}PCM estimated time is {0:.1f}s'.format(est))
        if est > self.pcmMaxTime:
            print(f'{self.alrt}PCM estimate over max time of ' + str(self.pcmMaxTime) + 's, cancelling')
            return

        sysex = sysexSet['pcmdata'].copy()
        startIndex = sysex.index('start')
        pcmStart = self.lenEncode(start)
        sysex[startIndex:startIndex+1] = pcmStart

        endIndex = sysex.index('end')
        pcmEnd = self.lenEncode(end)
        sysex[endIndex:endIndex+1] = pcmEnd
        
        dataIndex = sysex.index('data')
        pcmSamples = self.pcmEncode(wave)
        sysex[dataIndex:dataIndex+1] = pcmSamples
        
        checksumIndex = sysex.index('checksum')
        sysex[checksumIndex] = self.checksum(sysex[startIndex:checksumIndex])

        midi.sendSysex(self.output, sysex)

    def getMultisoundsList(self):
        if self.debug: print(f'{self.trans}Request multisound list')
        

        midi.sendSysex(self.output, sysexGet['multisoundlist'])
        
    def setMultisoundsListAfterMultisoundSet(self, progno, multisound):   
        name, loop, soundAmount, sounds = multisound
        while len(name) < 8:
            name += ' '
        length = sum([s[5] for s in sounds])
        
        if progno == self.multiAmount:
            self.multiAmount += 1
        self.multiName[progno] = name
        self.multiLen[progno] = length
            
        self.setMultisoundsList()
        
    def setMultisoundsList(self):
        if self.debug:
            print(f'{self.trans}Setting multisound list')
            print(f'{self.info}Load error okay')

        sysex = sysexSet['multisoundlist'].copy()
        
        amountIndex = sysex.index('amount')
        sysex[amountIndex] = self.multiAmount
        
        dataIndex = sysex.index('data')
        sysex[dataIndex:dataIndex+1] = [x for name, length in zip(self.multiName, self.multiLen) for x in (*list(map(ord, name.ljust(8))), *self.lenEncode(length))]
        
        checksumIndex = sysex.index('checksum')
        sysex[checksumIndex] = self.checksum(sysex[amountIndex:checksumIndex])

        midi.sendSysex(self.output, sysex)

    def getMultisound(self, number):
        if self.debug:
            print(f'{self.trans}Request multisound parameters from ', end = '')
            try:
                print(self.multiName[number])
            except:
                print('EMPTY')

        sysex = sysexGet['multisound'].copy()
        sysex[sysex.index('number')] = number

        midi.sendSysex(self.output, sysex)
        
    def deleteMultisound(self, no):
        # pre: no is the last multisound in the list
        self.multiAmount -= 1
        self.multiLen.pop()
        self.multiName.pop()
        
        self.setMultisoundsList()
        
    def setMultisound(self, no, multisound):
        if self.debug:
            print(f'{self.trans}Sending multisound parameters for multisound {no}')
        
        name, loop, soundAmount, sounds = multisound
        
        while len(name) < 8:
            name += ' '
        nameList = list(map(ord, name[0:8]))
        
        
        sysex = sysexSet['multisound'].copy()
        
        noIndex = sysex.index('number')
        sysex[noIndex] = no
        
        nameIndex = sysex.index('name')
        sysex[nameIndex:nameIndex+1] = nameList
        
        length = sum([s[5] for s in sounds])
        lengthIndex = sysex.index('length')
        sysex[lengthIndex:lengthIndex+1] = self.lenEncode(length)
        sysex[sysex.index('loopsounds')] = (loop << 6) + soundAmount
        maxint = max([s[0] - s[1] + (0, -7, -12, 5)[s[11]] for s in sounds])
        sysex[sysex.index('maxinterval')] = ~maxint & 0b01111111
        
        soundParamIndex = sysex.index('soundparams')
        sysex[soundParamIndex:soundParamIndex+1] = [v for s in sounds for v in (
            s[0], s[1], s[2], s[3], s[4],
            *self.lenEncode(s[5]),
            *self.lenEncode(s[6]),
            *self.lenEncode(s[7]),
            *self.lenEncode(s[8]),
            *self.lenEncode(s[9]),
            ((1-s[10]) << 6) + s[11]
        )]
        
        checksumIndex = sysex.index('checksum')
        sysex[checksumIndex] = self.checksum(sysex[noIndex:checksumIndex])
        
        midi.sendSysex(self.output, sysex)

    def getParameters(self, program):
        if self.debug: print(f'{self.trans}Request all parameters from program ' + str(program+1))

        sysex = sysexGet['parameters'].copy()
        sysex[sysex.index('program')] = program

        midi.sendSysex(self.output, sysex)

    def setParameter(self, parameter, value):
        if self.debug and self.logParameterChanges: print(f'{self.transNoExp}Set parameter ' + str(parameter) + ' to ' + str(value))

        sysex = sysexSet['parameter'].copy()
        sysex[sysex.index('parameter')] = parameter

        valueIndex = sysex.index('value')

        if parameter == 46 or parameter == 52:
            sysex[valueIndex] = value//128
            sysex.insert(valueIndex, value%128)
        else:
            sysex[valueIndex] = value

        midi.sendSysex(self.output, sysex)

    def setKey(self, key):
        parNum = list(self.param.keys()).index(key)
        parVal = self.param[key]['v']

        self.setParameter(parNum, parVal)

    def setParameters(self, name, param='self'):
        if self.debug: print(f'{self.trans}Set all parameters and assign the name \"' + name + '\"')

        while len(name) < 8:
            name += ' '
        nameList = list(map(ord, name[0:8]))
        
        if param == 'self':
            param = self.param
            parameterList = [par['v'] for par in param.values()]
        else:
            parameterList = [par for par in param.values()]

        #Treat the 2 delay times (address 46 and 52)
        dh, dl = parameterList[46]//128, parameterList[46]%128
        parameterList[46] = dl
        parameterList.insert(47, dh)
        #53 here, we inserted an additional value
        dh, dl = parameterList[53]//128, parameterList[53]%128
        parameterList[53] = dl
        parameterList.insert(54, dh)

        #Insert these 2 lists into the sysex
        sysex = sysexSet['parameters'].copy()
        parIndex = sysex.index('parameters')
        sysex[parIndex:parIndex+1] = parameterList
        nameIndex = sysex.index('name')
        sysex[nameIndex:nameIndex+1] = nameList

        #Send the finalized sysex patch
        midi.sendSysex(self.output, sysex)

    def saveProgram(self, program):
        if self.debug: print(f'{self.trans}Save program as program ' + str(program+1))

        #Getting the sysex command
        sysex = sysexSet['writeprogram'].copy()
        #Replacing the pointer with the program
        sysex[sysex.index('program')] = program

        midi.sendSysex(self.output, sysex)


    #Extract parameters from emulation
    def extractParameters(self):
        parList = []
        for key in self.param.keys():
            parList.append(self.param[key]['v'])

        return parList

    #Load parameters from a list
    def putParameters(self, parList):
        for i, key in enumerate(self.param.keys()):
            self.param[key]['v'] = parList[i]

        self.updateGUI = True


    def extractMultisoundParameters(self):
        multParList = []
        for key in self.msparam.keys():
            multParList.append(self.msparam[key])

        soundParList = []
        for i in range(16):
            soundParList.append([])
            for key in self.soundparam.keys():
                soundParList[i].append(self.soundparameters[i][key])

        multParList.append(soundParList)

        return multParList
